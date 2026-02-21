<?php
/**
 * ========================================
 * 编辑盘点单功能 - API接口代码
 * 文件名: edit_inventory_apis.php
 * 版本: v1.0.0
 * 说明: 此代码需要插入到 index.php 的 API 部分
 *       位置：在 delete_inventory_session API 之后，最后的 } 之前
 * ========================================
 */

// ========================================
// 编辑盘点单功能 API
// ========================================

/**
 * 获取可编辑的盘点单详情
 */
if ($action === 'get_editable_session') {
    $session_id = $_GET['session_id'] ?? '';

    if (empty($session_id)) {
        echo json_encode(['success' => false, 'message' => '缺少session_id参数']);
        exit;
    }

    // 验证权限：只能编辑自己创建的盘点单，或管理员可以编辑所有
    $stmt = $conn->prepare("SELECT user_id FROM inventory_sessions WHERE session_key = ?");
    $stmt->bind_param("s", $session_id);
    $stmt->execute();
    $session = $stmt->get_result()->fetch_assoc();

    if (!$session) {
        echo json_encode(['success' => false, 'message' => '盘点单不存在']);
        exit;
    }

    // 检查是否是管理员
    $adminCheck = $conn->prepare("SELECT is_admin FROM users WHERE id = ?");
    $adminCheck->bind_param("i", $_SESSION['user_id']);
    $adminCheck->execute();
    $isAdmin = $adminCheck->get_result()->fetch_assoc()['is_admin'] ?? 0;

    if ($session['user_id'] != $_SESSION['user_id'] && !$isAdmin) {
        echo json_encode(['success' => false, 'message' => '无权编辑此盘点单']);
        exit;
    }

    // 获取盘点单详情
    $stmt = $conn->prepare("SELECT p.sku, p.name, p.removal_buffer, b.id as batch_id,
                                   b.expiry_date, b.quantity
                            FROM batches b
                            JOIN products p ON b.product_id = p.id
                            WHERE b.session_id = ?
                            ORDER BY b.expiry_date ASC");
    $stmt->bind_param("s", $session_id);
    $stmt->execute();
    $result = $stmt->get_result();

    $items = [];
    while ($row = $result->fetch_assoc()) {
        $items[] = $row;
    }

    echo json_encode([
        'success' => true,
        'data' => [
            'session_id' => $session_id,
            'items' => $items,
            'item_count' => count($items)
        ]
    ]);
    exit;
}

/**
 * 更新批次信息
 */
if ($action === 'update_batch') {
    $data = json_decode(file_get_contents('php://input'), true);

    $batch_id = intval($data['batch_id'] ?? 0);
    $expiry_date = $data['expiry_date'] ?? '';
    $quantity = intval($data['quantity'] ?? 0);

    if (!$batch_id) {
        echo json_encode(['success' => false, 'message' => '批次ID无效']);
        exit;
    }

    if ($quantity <= 0) {
        echo json_encode(['success' => false, 'message' => '数量必须大于0']);
        exit;
    }

    if (empty($expiry_date)) {
        echo json_encode(['success' => false, 'message' => '有效期不能为空']);
        exit;
    }

    // 验证日期格式
    if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $expiry_date)) {
        echo json_encode(['success' => false, 'message' => '日期格式错误，应为YYYY-MM-DD']);
        exit;
    }

    $conn->begin_transaction();

    try {
        // 获取当前批次信息（用于审计日志）
        $stmt = $conn->prepare("SELECT b.*, p.name as product_name, p.sku
                                FROM batches b
                                JOIN products p ON b.product_id = p.id
                                WHERE b.id = ?");
        $stmt->bind_param("i", $batch_id);
        $stmt->execute();
        $old_batch = $stmt->get_result()->fetch_assoc();

        if (!$old_batch) {
            throw new Exception('批次不存在');
        }

        // 验证权限：只能编辑自己创建的盘点单，或管理员可以编辑所有
        $sessionCheck = $conn->prepare("SELECT user_id FROM inventory_sessions WHERE session_key = ?");
        $sessionCheck->bind_param("s", $old_batch['session_id']);
        $sessionCheck->execute();
        $session = $sessionCheck->get_result()->fetch_assoc();

        $adminCheck = $conn->prepare("SELECT is_admin FROM users WHERE id = ?");
        $adminCheck->bind_param("i", $_SESSION['user_id']);
        $adminCheck->execute();
        $isAdmin = $adminCheck->get_result()->fetch_assoc()['is_admin'] ?? 0;

        if ($session['user_id'] != $_SESSION['user_id'] && !$isAdmin) {
            throw new Exception('无权编辑此批次');
        }

        // 更新批次信息
        $updateStmt = $conn->prepare("UPDATE batches SET expiry_date = ?, quantity = ? WHERE id = ?");
        $updateStmt->bind_param("sii", $expiry_date, $quantity, $batch_id);

        if (!$updateStmt->execute()) {
            throw new Exception('更新失败');
        }

        // 记录审计日志
        $old_value = json_encode([
            'expiry_date' => $old_batch['expiry_date'],
            'quantity' => $old_batch['quantity']
        ]);

        $new_value = json_encode([
            'expiry_date' => $expiry_date,
            'quantity' => $quantity
        ]);

        $logStmt = $conn->prepare("INSERT INTO inventory_edit_logs
                                   (session_id, batch_id, action, old_value, new_value, user_id)
                                   VALUES (?, ?, 'update', ?, ?, ?)");
        $logStmt->bind_param("sissi", $old_batch['session_id'], $batch_id, $old_value, $new_value, $_SESSION['user_id']);
        $logStmt->execute();

        $conn->commit();

        echo json_encode([
            'success' => true,
            'message' => '批次信息已更新'
        ]);

    } catch (Exception $e) {
        $conn->rollback();
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
    exit;
}

/**
 * 删除批次
 */
if ($action === 'delete_batch') {
    $data = json_decode(file_get_contents('php://input'), true);
    $batch_id = intval($data['batch_id'] ?? 0);

    if (!$batch_id) {
        echo json_encode(['success' => false, 'message' => '批次ID无效']);
        exit;
    }

    $conn->begin_transaction();

    try {
        // 获取批次信息（用于权限验证和审计日志）
        $stmt = $conn->prepare("SELECT b.*, p.name as product_name, p.sku
                                FROM batches b
                                JOIN products p ON b.product_id = p.id
                                WHERE b.id = ?");
        $stmt->bind_param("i", $batch_id);
        $stmt->execute();
        $batch = $stmt->get_result()->fetch_assoc();

        if (!$batch) {
            throw new Exception('批次不存在');
        }

        // 验证权限
        $sessionCheck = $conn->prepare("SELECT user_id FROM inventory_sessions WHERE session_key = ?");
        $sessionCheck->bind_param("s", $batch['session_id']);
        $sessionCheck->execute();
        $session = $sessionCheck->get_result()->fetch_assoc();

        $adminCheck = $conn->prepare("SELECT is_admin FROM users WHERE id = ?");
        $adminCheck->bind_param("i", $_SESSION['user_id']);
        $adminCheck->execute();
        $isAdmin = $adminCheck->get_result()->fetch_assoc()['is_admin'] ?? 0;

        if ($session['user_id'] != $_SESSION['user_id'] && !$isAdmin) {
            throw new Exception('无权删除此批次');
        }

        // 删除批次
        $deleteStmt = $conn->prepare("DELETE FROM batches WHERE id = ?");
        $deleteStmt->bind_param("i", $batch_id);

        if (!$deleteStmt->execute()) {
            throw new Exception('删除失败');
        }

        // 记录审计日志
        $old_value = json_encode([
            'sku' => $batch['sku'],
            'name' => $batch['product_name'],
            'expiry_date' => $batch['expiry_date'],
            'quantity' => $batch['quantity']
        ]);

        $logStmt = $conn->prepare("INSERT INTO inventory_edit_logs
                                   (session_id, batch_id, action, old_value, user_id)
                                   VALUES (?, ?, 'delete', ?, ?)");
        $logStmt->bind_param("sisi", $batch['session_id'], $batch_id, $old_value, $_SESSION['user_id']);
        $logStmt->execute();

        $conn->commit();

        echo json_encode([
            'success' => true,
            'message' => '批次已删除'
        ]);

    } catch (Exception $e) {
        $conn->rollback();
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
    exit;
}

/**
 * 添加商品到盘点单
 */
if ($action === 'add_to_session') {
    $data = json_decode(file_get_contents('php://input'), true);

    $session_id = $data['session_id'] ?? '';
    $sku = trim($data['sku'] ?? '');
    $batches = $data['batches'] ?? [];

    if (empty($session_id) || empty($sku) || empty($batches)) {
        echo json_encode(['success' => false, 'message' => '缺少必要参数']);
        exit;
    }

    $conn->begin_transaction();

    try {
        // 验证权限
        $sessionCheck = $conn->prepare("SELECT user_id FROM inventory_sessions WHERE session_key = ?");
        $sessionCheck->bind_param("s", $session_id);
        $sessionCheck->execute();
        $session = $sessionCheck->get_result()->fetch_assoc();

        if (!$session) {
            throw new Exception('盘点单不存在');
        }

        $adminCheck = $conn->prepare("SELECT is_admin FROM users WHERE id = ?");
        $adminCheck->bind_param("i", $_SESSION['user_id']);
        $adminCheck->execute();
        $isAdmin = $adminCheck->get_result()->fetch_assoc()['is_admin'] ?? 0;

        if ($session['user_id'] != $_SESSION['user_id'] && !$isAdmin) {
            throw new Exception('无权编辑此盘点单');
        }

        // 查找或创建商品
        $productStmt = $conn->prepare("SELECT id, name FROM products WHERE sku = ?");
        $productStmt->bind_param("s", $sku);
        $productStmt->execute();
        $product = $productStmt->get_result()->fetch_assoc();

        if (!$product) {
            throw new Exception('商品SKU不存在，请先在系统中添加该商品');
        }

        $product_id = $product['id'];

        // 添加批次
        $insertStmt = $conn->prepare("INSERT INTO batches (product_id, expiry_date, quantity, session_id)
                                      VALUES (?, ?, ?, ?)");
        $insertStmt->bind_param("isis", $product_id, $expiry_date, $quantity, $session_id);

        $added_batches = [];
        foreach ($batches as $batch) {
            $expiry_date = $batch['expiry_date'];
            $quantity = intval($batch['quantity']);

            if ($quantity <= 0) {
                throw new Exception('数量必须大于0');
            }

            if (!$insertStmt->execute()) {
                throw new Exception('添加批次失败');
            }

            $batch_id = $conn->insert_id;

            // 记录审计日志
            $new_value = json_encode([
                'sku' => $sku,
                'name' => $product['name'],
                'expiry_date' => $expiry_date,
                'quantity' => $quantity
            ]);

            $logStmt = $conn->prepare("INSERT INTO inventory_edit_logs
                                       (session_id, batch_id, action, new_value, user_id)
                                       VALUES (?, ?, 'add', ?, ?)");
            $logStmt->bind_param("sisi", $session_id, $batch_id, $new_value, $_SESSION['user_id']);
            $logStmt->execute();

            $added_batches[] = [
                'batch_id' => $batch_id,
                'expiry_date' => $expiry_date,
                'quantity' => $quantity
            ];
        }

        $conn->commit();

        echo json_encode([
            'success' => true,
            'message' => '商品已添加',
            'data' => [
                'sku' => $sku,
                'name' => $product['name'],
                'batches' => $added_batches
            ]
        ]);

    } catch (Exception $e) {
        $conn->rollback();
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
    exit;
}
?>
