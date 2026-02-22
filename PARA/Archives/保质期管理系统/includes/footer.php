<?php
/**
 * 公共底部文件
 * 包含JavaScript等
 */

if (!defined('APP_LOADED')) {
    die('Direct access not allowed');
}
?>
    </div><!-- /.container -->

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- 通用工具函数 -->
    <script>
        // 格式化日期
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // 复制到剪贴板
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('已复制到剪贴板');
            });
        }

        // 确认对话框
        function confirmAction(message) {
            return confirm(message);
        }

        // 显示Toast提示
        function showToast(message, type = 'info') {
            // 简单实现，可以用Bootstrap Toast增强
            alert(message);
        }
    </script>
</body>
</html>
