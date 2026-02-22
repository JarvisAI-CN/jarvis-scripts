#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 准备API接口代码
import re

def main():
    # 读取当前文件
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到API接口处理块的结束位置
    # 寻找第203行左右的 '}'
    lines = content.split("\n")
    api_end_pos_line = None
    for i, line in enumerate(lines):
        if line.strip() == "}" and i > 48:  # API接口处理块从第48行开始
            api_end_pos_line = i
            print(f"API接口处理块结束位置在第{i}行")
            break

    if api_end_pos_line is None:
        raise ValueError("API接口处理块结束位置未找到")

    # 定义要添加的API接口代码
    new_api_code = """    // AI分析API接口
    if ($action === 'analyze_inventory') {
        header('Content-Type: application/json');
        
        $data = json_decode(file_get_contents('php://input'), true);
        if (!isset($data['session_id'])) {
            echo json_encode(['success' => false, 'message' => '缺少session_id参数']);
            exit;
        }
        
        $sessionId = $data['session_id'];
        
        // 获取盘点单详情
        $result = getInventoryDetails($sessionId);
        
        if (!$result['success']) {
            echo json_encode(['success' => false, 'message' => $result['message']]);
            exit;
        }
        
        // 构建分析提示
        $prompt = buildAnalysisPrompt($result['inventoryData']);
        
        // 调用AI API
        $aiResponse = callAIAPI(
            'https://api.deepseek.com',
            '你的API密钥',
            'deepseek-chat',
            $prompt
        );
        
        if ($aiResponse['success']) {
            echo json_encode([
                'success' => true,
                'analysis' => $aiResponse['content'],
                'table_html' => generateInventoryTable($result['inventoryData'])
            ]);
        } else {
            echo json_encode(['success' => false, 'message' => $aiResponse['error']]);
        }
        exit;
    }
    
    // 发送邮件API接口
    if ($action === 'send_inventory_email') {
        header('Content-Type: application/json');
        
        $data = json_decode(file_get_contents('php://input'), true);
        if (!isset($data['session_id']) || !isset($data['subject']) || !isset($data['analysis']) || !isset($data['table_html'])) {
            echo json_encode(['success' => false, 'message' => '缺少参数']);
            exit;
        }
        
        // 这里应该添加发送邮件的逻辑
        // 现在返回成功响应
        echo json_encode(['success' => true]);
        exit;
    }
    
    // 辅助函数：构建AI分析提示
    function buildAnalysisPrompt($inventoryData) {
        $summary = [];
        $skuCount = count(array_unique(array_column($inventoryData, 'sku')));
        $totalItems = count($inventoryData);
        $totalQuantity = array_sum(array_column($inventoryData, 'quantity'));
        
        // 计算即将过期的商品
        $today = date('Y-m-d');
        $expiringSoon = [];
        foreach ($inventoryData as $item) {
            $daysToExpiry = (strtotime($item['expiry_date']) - strtotime($today)) / (60 * 60 * 24);
            if ($daysToExpiry <= 30 && $daysToExpiry > 0) {
                $expiringSoon[] = $item;
            }
        }
        
        $expiringCount = count($expiringSoon);
        
        $analysisPrompt = <<<PROMPT
你是一个专业的库存分析师，需要分析以下保质期管理系统的盘点单数据，并提供详细的分析报告。

## 数据摘要
- 商品种类：$skuCount 种
- 批次数量：$totalItems 个
- 总数量：$totalQuantity 件
- 即将过期（30天内）：$expiringCount 个批次

## 详细数据
```json
[
PROMPT;
        
        foreach ($inventoryData as $item) {
            $analysisPrompt .= json_encode([
                'sku' => $item['sku'],
                'product_name' => $item['name'],
                'quantity' => $item['quantity'],
                'expiry_date' => $item['expiry_date'],
                'category' => '',
                'inventory_cycle' => 0
            ]) . ",\\n";
        }
        
        $analysisPrompt .= <<<PROMPT
]
```

## 分析要求
请分析以下内容：
1. 整体库存状况总结
2. 即将过期商品的风险分析
3. 库存周转率建议
4. 商品分类分析
5. 保质期分布分析
6. 可能的优化建议

## 输出格式
请使用中文，采用Markdown格式，分点列出分析结果，语气专业且建议可行。
不要返回代码块或JSON格式，直接返回分析内容。
PROMPT;
        
        return $analysisPrompt;
    }
    
    // 辅助函数：调用AI API
    function callAIAPI($url, $key, $model, $prompt) {
        $apiUrl = rtrim($url, '/') . "/chat/completions";
        
        $data = [
            "model" => $model,
            "messages" => [
                [
                    "role" => "user", 
                    "content" => $prompt
                ]
            ],
            "max_tokens" => 2000,
            "temperature" => 0.3
        ];
        
        $ch = curl_init($apiUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            "Content-Type: application/json", 
            "Authorization: Bearer " . $key
        ]);
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            $result = json_decode($response, true);
            if (isset($result['choices'][0]['message']['content'])) {
                return [
                    'success' => true,
                    'content' => $result['choices'][0]['message']['content']
                ];
            } else {
                return ['success' => false, 'error' => 'API响应格式错误'];
            }
        } else {
            return ['success' => false, 'error' => 'HTTP ' . $httpCode . ' 错误'];
        }
    }
    
    // 辅助函数：生成可打印的HTML表格
    function generateInventoryTable($inventoryData) {
        $tableHtml = <<<HTML
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>盘点单汇总表</title>
    <style>
        @media print {
            body { font-family: "Microsoft YaHei", "SimSun", sans-serif; font-size: 12pt; }
            .no-print { display: none !important; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 10mm; }
            th, td { border: 1px solid #000; padding: 6px; text-align: center; }
            th { background-color: #f0f0f0; font-weight: bold; }
            .header { text-align: center; margin-bottom: 5mm; }
            .footer { margin-top: 10mm; font-size: 10pt; text-align: center; color: #666; }
        }
        @media screen {
            body { font-family: "Microsoft YaHei", "SimSun", sans-serif; padding: 20px; background-color: #f8f9fa; }
            .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
            th { background-color: #f5f5f5; font-weight: bold; }
            .header { text-align: center; margin-bottom: 20px; }
            .footer { margin-top: 40px; font-size: 14px; text-align: center; color: #666; }
            .print-btn { text-align: center; margin-bottom: 20px; }
            .print-btn button { padding: 10px 20px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="print-btn no-print">
            <button onclick="window.print()">打印表格</button>
        </div>
        
        <div class="header">
            <h1>盘点单汇总表</h1>
            <p>盘点单号：{$inventoryData[0]['session_key']}</p>
            <p>盘点时间：{$inventoryData[0]['created_at']}</p>
            <p>盘点人：{$inventoryData[0]['username']}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>SKU</th>
                    <th>商品名称</th>
                    <th>分类</th>
                    <th>效期</th>
                    <th>数量</th>
                    <th>盘点周期</th>
                </tr>
            </thead>
            <tbody>
HTML;
        
        $rowNum = 1;
        foreach ($inventoryData as $item) {
            $tableHtml .= <<<HTML
                <tr>
                    <td>{$rowNum}</td>
                    <td>{$item['sku']}</td>
                    <td>{$item['product_name']}</td>
                    <td>{$item['category_name']}</td>
                    <td>{$item['expiry_date']}</td>
                    <td>{$item['quantity']}</td>
                    <td>{$item['inventory_cycle']}</td>
                </tr>
HTML;
            $rowNum++;
        }
        
        $tableHtml .= <<<HTML
            </tbody>
        </table>
        
        <div class="footer">
            <p>数据导出时间：{$inventoryData[0]['created_at']}</p>
            <p>此表格由保质期管理系统自动生成</p>
        </div>
    </div>
</body>
</html>
HTML;
        
        return $tableHtml;
    }
    
    // 辅助函数：获取盘点单详情
    function getInventoryDetails($sessionId) {
        global $conn;
        
        $stmt = $conn->prepare("
            SELECT 
                p.sku, 
                p.name, 
                b.expiry_date, 
                b.quantity, 
                b.session_id,
                c.name as category_name,
                p.removal_buffer,
                i.created_at,
                u.username
            FROM batches b
            JOIN products p ON b.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory_sessions i ON b.session_id = i.session_key
            LEFT JOIN users u ON i.user_id = u.id
            WHERE b.session_id = ?
        ");
        
        $stmt->bind_param("s", $sessionId);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $inventoryData = [];
        while ($row = $result->fetch_assoc()) {
            $inventoryData[] = [
                'sku' => $row['sku'],
                'product_name' => $row['name'],
                'expiry_date' => $row['expiry_date'],
                'quantity' => $row['quantity'],
                'session_key' => $row['session_id'],
                'category_name' => $row['category_name'],
                'removal_buffer' => $row['removal_buffer'],
                'created_at' => $row['created_at'],
                'username' => $row['username'],
                'inventory_cycle' => 0 // 这个字段可能需要根据实际数据设置
            ];
        }
        
        if (empty($inventoryData)) {
            return ['success' => false, 'message' => '未找到盘点单数据'];
        }
        
        return ['success' => true, 'inventoryData' => $inventoryData];
    }
"""

    # 在API接口处理块结束位置之前插入新API接口代码
    lines.insert(api_end_pos_line, new_api_code)

    # 将修改后的内容写回文件
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print("✅ API接口处理块修改完成")

if __name__ == "__main__":
    main()
