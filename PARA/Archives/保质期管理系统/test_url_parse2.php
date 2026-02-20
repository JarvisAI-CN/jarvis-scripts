<?php
// 测试修复后的URL解析逻辑

$qrCode = "https://artwork.starbucks.com.cn/mobile/gtin/6977696000116/cii1/001118701720260129&20260924#/";
$sku = $qrCode;
$expiryDateFromQR = null;

echo "原始URL: $qrCode\n\n";

// 格式1: 星巴克URL格式
if (strpos($qrCode, 'artwork.starbucks.com.cn') !== false) {
    $pathParts = explode('/', parse_url($qrCode, PHP_URL_PATH));
    $ciiIndex = array_search('cii1', $pathParts);

    echo "cii1数据: {$pathParts[$ciiIndex + 1]}\n\n";

    if ($ciiIndex !== false && $ciiIndex + 1 < count($pathParts)) {
        $ciiData = $pathParts[$ciiIndex + 1]; // 00+SKU+生产日期&到期日期

        // 分离&前后的部分
        $ampIndex = strpos($ciiData, '&');
        if ($ampIndex !== false) {
            $datePart = substr($ciiData, $ampIndex + 1); // 20260924
            $ciiData = substr($ciiData, 0, $ampIndex); // 00+SKU+生产日期

            echo "cii数据部分: $ciiData\n";
            echo "日期部分: $datePart\n";

            // 解析到期日期（8位数字）
            if (strlen($datePart) === 8 && ctype_digit($datePart)) {
                $year = substr($datePart, 0, 4);
                $month = substr($datePart, 4, 2);
                $day = substr($datePart, 6, 2);
                $expiryDateFromQR = "$year-$month-$day";
                echo "解析的到期日期: $expiryDateFromQR\n";
            }
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
?>
