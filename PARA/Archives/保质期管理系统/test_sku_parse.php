<?php
// 测试SKU提取逻辑

$qrCode = "001117979820251124#20251124#20260523";
$sku = $qrCode;
$expiryDateFromQR = null;

echo "原始二维码: $qrCode\n\n";

// 解析二维码格式
if (strpos($qrCode, '#') !== false) {
    $parts = explode('#', $qrCode);
    echo "分割后的部分: " . count($parts) . " 个\n";
    echo "Part 0: " . $parts[0] . "\n";
    echo "Part 1: " . $parts[1] . "\n";
    echo "Part 2: " . $parts[2] . "\n\n";

    if (count($parts) >= 3) {
        // 格式: 00 + SKU(8位) + 生产日期 + 到期日期
        $skuPart = $parts[0]; // 第一部分是 00 + SKU
        $prodDatePart = $parts[1]; // 第二部分是生产日期
        $expiryDatePart = $parts[2]; // 第三部分是到期日期

        echo "SKU部分: $skuPart\n";
        echo "生产日期: $prodDatePart\n";
        echo "到期日期: $expiryDatePart\n\n";

        // 去掉前缀 "00"，提取纯SKU
        if (strpos($skuPart, '00') === 0) {
            $sku = substr($skuPart, 2);
            echo "去掉00前缀后的SKU: $sku\n";
        }

        // 解析到期日期
        if (strlen($expiryDatePart) === 8 && ctype_digit($expiryDatePart)) {
            $year = substr($expiryDatePart, 0, 4);
            $month = substr($expiryDatePart, 4, 2);
            $day = substr($expiryDatePart, 6, 2);
            $expiryDateFromQR = "$year-$month-$day";
            echo "解析后的到期日期: $expiryDateFromQR\n";
        }
    }
}

echo "\n最终SKU: $sku\n";
echo "最终到期日期: " . ($expiryDateFromQR ?? 'null') . "\n";
?>
