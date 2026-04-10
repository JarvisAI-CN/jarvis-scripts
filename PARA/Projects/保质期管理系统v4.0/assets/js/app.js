/**
 * 保质期管理系统 v4.0 - 主JavaScript文件
 * 创建时间: 2026-04-11
 * 描述: 系统全局功能和工具函数
 */

// ==================== 全局变量 ====================
const App = {
    config: {
        apiBaseUrl: '/api/',
        refreshInterval: 30000, // 30秒
    },
    user: null,
    isAuthenticated: false
};

// ==================== 工具函数 ====================

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success/danger/warning/info)
 */
function showMessage(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // 在页面顶部显示消息
    const container = document.querySelector('.container');
    if (container) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = alertHtml;
        container.insertBefore(tempDiv.firstElementChild, container.firstElementChild);
        
        // 5秒后自动隐藏
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

/**
 * 确认对话框
 * @param {string} message - 确认消息
 * @returns {boolean} - 用户选择
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式 (default: 'YYYY-MM-DD HH:mm:ss')
 * @returns {string} - 格式化后的日期
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

/**
 * 计算保质期状态
 * @param {string} expiryDate - 过期日期
 * @param {number} bufferDays - 缓冲天数
 * @returns {object} - 状态对象 {status, label, class}
 */
function getExpiryStatus(expiryDate, bufferDays = 0) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const expiry = new Date(expiryDate);
    expiry.setHours(0, 0, 0, 0);
    
    // 计算剩余天数
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) - bufferDays;
    
    if (diffDays < 0) {
        return {
            status: 'expired',
            label: '已过期',
            class: 'bg-danger',
            days: diffDays
        };
    } else if (diffDays <= 7) {
        return {
            status: 'critical',
            label: `临期 (${diffDays}天)`,
            class: 'bg-warning',
            days: diffDays
        };
    } else if (diffDays <= 30) {
        return {
            status: 'warning',
            label: `预警 (${diffDays}天)`,
            class: 'bg-info',
            days: diffDays
        };
    } else {
        return {
            status: 'normal',
            label: `正常 (${diffDays}天)`,
            class: 'bg-success',
            days: diffDays
        };
    }
}

/**
 * 格式化数字
 * @param {number} num - 数字
 * @param {number} decimals - 小数位数
 * @returns {string} - 格式化后的数字
 */
function formatNumber(num, decimals = 0) {
    return num.toLocaleString('zh-CN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * 复制到剪贴板
 * @param {string} text - 要复制的文本
 */
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showMessage('已复制到剪贴板', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * 备用复制方法
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showMessage('已复制到剪贴板', 'success');
        } else {
            showMessage('复制失败', 'danger');
        }
    } catch (err) {
        showMessage('复制失败', 'danger');
    }
    
    document.body.removeChild(textArea);
}

// ==================== API调用 ====================

/**
 * 发送API请求
 * @param {string} url - API URL
 * @param {object} options - 请求选项
 * @returns {Promise} - Promise对象
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API请求错误:', error);
        showMessage(error.message, 'danger');
        throw error;
    }
}

/**
 * GET请求
 */
function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

/**
 * POST请求
 */
function apiPost(url, data) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ==================== 表单验证 ====================

/**
 * 验证必填字段
 * @param {HTMLFormElement} form - 表单元素
 * @returns {boolean} - 是否验证通过
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        const value = field.value.trim();
        if (!value) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    if (!isValid) {
        showMessage('请填写所有必填字段', 'warning');
    }
    
    return isValid;
}

/**
 * 验证SKU格式
 * @param {string} sku - SKU代码
 * @returns {boolean} - 是否有效
 */
function validateSKU(sku) {
    // SKU必须是字母数字组合，长度3-50
    const skuRegex = /^[A-Za-z0-9_-]{3,50}$/;
    return skuRegex.test(sku);
}

/**
 * 验证日期格式
 * @param {string} dateStr - 日期字符串
 * @returns {boolean} - 是否有效
 */
function validateDate(dateStr) {
    const date = new Date(dateStr);
    return date instanceof Date && !isNaN(date);
}

// ==================== 分页功能 ====================

/**
 * 渲染分页
 * @param {number} currentPage - 当前页
 * @param {number} totalPages - 总页数
 * @param {function} onPageChange - 页面变化回调
 */
function renderPagination(currentPage, totalPages, onPageChange) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;
    
    let html = '<nav aria-label="分页导航"><ul class="pagination">';
    
    // 上一页
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page="${currentPage - 1}">上一页</a>
    </li>`;
    
    // 页码
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // 下一页
    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page="${currentPage + 1}">下一页</a>
    </li>`;
    
    html += '</ul></nav>';
    
    paginationContainer.innerHTML = html;
    
    // 绑定点击事件
    paginationContainer.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = parseInt(e.target.dataset.page);
            if (page && page !== currentPage && onPageChange) {
                onPageChange(page);
            }
        });
    });
}

// ==================== 搜索功能 ====================

/**
 * 防抖函数
 * @param {function} func - 要执行的函数
 * @param {number} wait - 等待时间(ms)
 * @returns {function} - 防抖后的函数
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 搜索处理
 * @param {string} keyword - 搜索关键词
 * @param {function} onSearch - 搜索回调
 */
function handleSearch(keyword, onSearch) {
    const debouncedSearch = debounce((query) => {
        onSearch(query);
    }, 500);
    
    debouncedSearch(keyword);
}

// ==================== 数据导出 ====================

/**
 * 导出为CSV
 * @param {array} data - 数据数组
 * @param {string} filename - 文件名
 */
function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        showMessage('没有数据可导出', 'warning');
        return;
    }
    
    // 获取表头
    const headers = Object.keys(data[0]);
    
    // 构建CSV内容
    let csv = headers.join(',') + '\n';
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // 处理包含逗号的值
            if (typeof value === 'string' && value.includes(',')) {
                return `"${value}"`;
            }
            return value || '';
        });
        csv += values.join(',') + '\n';
    });
    
    // 创建下载链接
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    
    showMessage('导出成功', 'success');
}

/**
 * 导出为Excel (简化版)
 * @param {array} data - 数据数组
 * @param {string} filename - 文件名
 */
function exportToExcel(data, filename = 'export.xlsx') {
    // 简化实现，实际应使用 SheetJS 等库
    exportToCSV(data, filename.replace('.xlsx', '.csv'));
}

// ==================== 自动保存 ====================

/**
 * 自动保存管理器
 */
const AutoSave = {
    timer: null,
    interval: 30000, // 30秒
    
    /**
     * 开始自动保存
     * @param {function} saveCallback - 保存回调函数
     */
    start(saveCallback) {
        if (this.timer) {
            this.stop();
        }
        
        this.timer = setInterval(() => {
            if (typeof saveCallback === 'function') {
                saveCallback();
            }
        }, this.interval);
    },
    
    /**
     * 停止自动保存
     */
    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
};

// ==================== 页面加载完成 ====================

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化下拉菜单
    const dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    dropdownTriggerList.map(function (dropdownTriggerEl) {
        return new bootstrap.Dropdown(dropdownTriggerEl);
    });
    
    // 全表单验证
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // 搜索框防抖
    const searchInputs = document.querySelectorAll('input[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function(e) {
            const keyword = e.target.value.trim();
            const searchTarget = e.target.dataset.search;
            
            // 触发自定义事件
            const event = new CustomEvent('search', {
                detail: { keyword, target: searchTarget }
            });
            document.dispatchEvent(event);
        }, 500));
    });
    
    console.log('保质期管理系统 v4.0 已加载');
});

// ==================== 导出到全局 ====================
window.App = App;
window.showMessage = showMessage;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
window.getExpiryStatus = getExpiryStatus;
window.formatNumber = formatNumber;
window.copyToClipboard = copyToClipboard;
window.apiRequest = apiRequest;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.validateForm = validateForm;
window.validateSKU = validateSKU;
window.validateDate = validateDate;
window.renderPagination = renderPagination;
window.handleSearch = handleSearch;
window.exportToCSV = exportToCSV;
window.exportToExcel = exportToExcel;
window.AutoSave = AutoSave;
