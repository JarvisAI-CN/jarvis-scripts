        </main>
        
        <!-- Footer -->
        <footer class="footer mt-auto py-3 bg-white border-top">
            <div class="container">
                <div class="row align-items-center">
                    <!-- Copyright -->
                    <div class="col-md-6 text-center text-md-start">
                        <p class="mb-0 text-muted">
                            <i class="bi bi-shield-check"></i>
                            &copy; <?php echo date('Y'); ?> 保质期管理系统 v<?php echo APP_VERSION; ?> - All Rights Reserved
                        </p>
                    </div>
                    
                    <!-- Version Info -->
                    <div class="col-md-6 text-center text-md-end">
                        <div class="d-flex flex-wrap justify-content-center justify-content-md-end gap-3">
                            <span class="text-muted small">
                                <i class="bi bi-clock-history"></i>
                                最后更新: <?php echo APP_VERSION; ?>
                            </span>
                            
                            <?php if (DEBUG_MODE): ?>
                                <span class="text-warning small">
                                    <i class="bi bi-bug"></i>
                                    调试模式
                                </span>
                            <?php endif; ?>
                            
                            <a href="<?php echo BASE_URL; ?>/settings.php" class="text-decoration-none text-muted small">
                                <i class="bi bi-gear"></i>
                                系统设置
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    </div>
    
    <!-- Global JavaScript -->
    <script src="<?php echo BASE_URL; ?>/assets/js/main.js"></script>
    <script src="<?php echo BASE_URL; ?>/assets/js/<?php echo $customJs ?? 'default'; ?>.js"></script>
    
    <!-- Page Specific Script -->
    <?php if ($pageName && file_exists(ASSETS_DIR . '/js/pages/' . $pageName . '.js')): ?>
        <script src="<?php echo BASE_URL; ?>/assets/js/pages/<?php echo $pageName; ?>.js"></script>
    <?php endif; ?>
    
    <!-- Global Error Handling -->
    <script>
        // 全局错误处理
        window.addEventListener('error', function(e) {
            if (<?php echo DEBUG_MODE ? 'true' : 'false'; ?>) {
                console.error('JavaScript 错误:', e.error);
                <?php if (checkAuth()): ?>
                    showAlert('JavaScript 错误: ' + e.error.message, 'danger');
                <?php endif; ?>
            }
            // 防止默认错误显示
            e.preventDefault();
        });
        
        // 全局 AJAX 错误处理
        $(document).ajaxError(function(event, jqxhr, settings, exception) {
            if (<?php echo DEBUG_MODE ? 'true' : 'false'; ?>) {
                console.error('AJAX 错误:', exception);
                <?php if (checkAuth()): ?>
                    showAlert('网络请求失败: ' + exception, 'danger');
                <?php endif; ?>
            }
        });
        
        // 页面加载完成后执行
        document.addEventListener('DOMContentLoaded', function() {
            // 检查是否需要更新版本信息
            checkVersion();
            
            // 初始化工具提示
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // 初始化弹出框
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            const popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
            
            // 页面访问记录
            trackPageVisit();
        });
        
        // 版本检查函数
        function checkVersion() {
            const currentVersion = '<?php echo APP_VERSION; ?>';
            
            // 这里可以添加远程版本检查逻辑
            console.log('当前版本:', currentVersion);
        }
        
        // 页面访问记录
        function trackPageVisit() {
            // 发送页面访问信息到服务器
            fetch('<?php echo API_BASE; ?>/analytics.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    page: '<?php echo $pageName ?? 'unknown'; ?>',
                    timestamp: new Date().toISOString()
                })
            }).catch(error => {
                if (<?php echo DEBUG_MODE ? 'true' : 'false'; ?>) {
                    console.error('页面访问记录失败:', error);
                }
            });
        }
    </script>
    
    <!-- Google Analytics (可选) -->
    <?php if (isset($googleAnalyticsId)): ?>
        <script async src="https://www.googletagmanager.com/gtag/js?id=<?php echo $googleAnalyticsId; ?>"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            
            gtag('config', '<?php echo $googleAnalyticsId; ?>');
        </script>
    <?php endif; ?>
</body>
</html>
