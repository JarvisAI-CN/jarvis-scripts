<?php
// 测试修复后的URL解析逻辑

$qrCode = "https://artwork.starbucks.com.cn/mobile/gtin/6977696000116/cii1/001118701720260129&20260129&20260924#/";
$sku = $qrCode;
$expiryDateFromQR = null;

echo "原始URL: $qrCode\n\n";

if (strpos($qrCode, 'artwork.starbucks.com.cn') !== false) {
    $pathParts = explode('/', parse_url($qrCode, PHP_URL_PATH));
    $ciiIndex = array_search('cii1', $pathParts);

    if ($ciiIndex !== false && $ciiIndex + 1 < count($pathParts)) {
        $ciiData = $pathParts[$ciiIndex + 1]; // 00+SKU+生产日期&生产日期&到期日期

        echo "cii1完整数据: $ciiData\n\n";

        // 分离所有&后的部分
        $ampParts = explode('&', $ciiData);
        $ciiData = $ampParts[0]; // 第一部分：00+SKU+生产日期

        echo "分解后的部分:\n";
        foreach ($ampParts as $i => $part) {
            echo "  Part $i: $part\n";
        }
        echo "\n";

        // 提取最后一个日期（到期日期）
        $lastPart = $ampParts[count($ampParts) - 1];
        echo "最后一部分: $lastPart\n";

        if (strlen($lastPart) === 8 && ctype_digit($lastPart)) {
            $year = substr($lastPart, 0, 4);
            $month = substr($lastPart, 4, 2);
            $day = substr($lastPart, 6, 2);
            $expiryDateFromQR = "$year-$month-$day";
            echo "解析的到期日期: $expiryDateFromQR\n";
        }

        // 去掉00前缀
        if (strpos($ciiData, '00') === 0) {
            $ciiData = substr($ciiData, 2);
        }
        echo "去掉00后: $ciiData\n";

        // 提取SKU（前8位）
        if (strlen($ciiData) >= 8) {
            $sku = substr($ciiData, 0, 8);
            echo "提取的SKU: $sku\n";
        }
    }
}

echo "\n=== 最终结果 ===\n";
echo "SKU: $sku\n";
echo "到期日期: " . ($expiryDateFromQR ?? 'null') . "\n";
echo "\n验证:\n";
echo "- SKU应该是: 11187017\n";
echo "- 到期日期应该是: 2026-09-24\n";
?>
