<?php
// 测试URL解析逻辑

$qrCode = "https://artwork.starbucks.com.cn/mobile/gtin/6977696000116/cii1/001118701720260129&20260924#/";
$sku = $qrCode;
$expiryDateFromQR = null;

echo "原始URL: $qrCode\n\n";

// 格式1: 星巴克URL格式
if (strpos($qrCode, 'artwork.starbucks.com.cn') !== false) {
    echo "检测到星巴克URL格式\n";

    // 解析URL路径
    $pathParts = explode('/', parse_url($qrCode, PHP_URL_PATH));
    echo "路径部分: " . print_r($pathParts, true) . "\n";

    $ciiIndex = array_search('cii1', $pathParts);
    echo "cii1索引位置: $ciiIndex\n";

    if ($ciiIndex !== false && $ciiIndex + 1 < count($pathParts)) {
        $ciiData = $pathParts[$ciiIndex + 1];
        echo "cii1数据: $ciiData\n";

        // 去掉00前缀
        $dataPart = $ciiData;
        if (strpos($dataPart, '00') === 0) {
            $dataPart = substr($dataPart, 2);
        }
        echo "去掉00后: $dataPart\n";

        // 提取SKU（前8位）
        if (strlen($dataPart) >= 8) {
            $sku = substr($dataPart, 0, 8);
            echo "提取的SKU: $sku\n";
        }

        // 从URL参数中提取到期日期
        $query = parse_url($qrCode, PHP_URL_QUERY);
        echo "URL参数: $query\n";

        if (preg_match('/&(\d{8})/', $query, $matches)) {
            $dateStr = $matches[1];
            $year = substr($dateStr, 0, 4);
            $month = substr($dateStr, 4, 2);
            $day = substr($dateStr, 6, 2);
            $expiryDateFromQR = "$year-$month-$day";
            echo "提取的到期日期: $expiryDateFromQR\n";
        }
    }
}

echo "\n=== 最终结果 ===\n";
echo "SKU: $sku\n";
echo "到期日期: " . ($expiryDateFromQR ?? 'null') . "\n";
?>
