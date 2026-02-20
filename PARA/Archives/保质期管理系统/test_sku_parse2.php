<?php
// 测试新的SKU提取逻辑

$qrCode = "001117979820251124#20251124#20260523";
$sku = $qrCode;
$expiryDateFromQR = null;

echo "原始二维码: $qrCode\n\n";

if (strpos($qrCode, '#') !== false) {
    $parts = explode('#', $qrCode);
    if (count($parts) >= 3) {
        $part1 = $parts[0]; // 00 + SKU + 生产日期

        echo "第一部分: $part1\n";

        // 去掉前缀 "00"
        if (strpos($part1, '00') === 0) {
            $part1 = substr($part1, 2);
        }

        echo "去掉00后: $part1\n";

        // 提取SKU（前8位）
        if (strlen($part1) >= 8) {
            $sku = substr($part1, 0, 8);
            echo "提取的SKU(前8位): $sku\n";
        }

        // 解析到期日期（第三部分）
        $expiryDatePart = $parts[2];
        if (strlen($expiryDatePart) === 8 && ctype_digit($expiryDatePart)) {
            $year = substr($expiryDatePart, 0, 4);
            $month = substr($expiryDatePart, 4, 2);
            $day = substr($expiryDatePart, 6, 2);
            $expiryDateFromQR = "$year-$month-$day";
            echo "解析的到期日期: $expiryDateFromQR\n";
        }
    }
}

echo "\n=== 最终结果 ===\n";
echo "SKU: $sku\n";
echo "到期日期: " . ($expiryDateFromQR ?? 'null') . "\n";
?>
