# PRD：保质期管理系统 - 批量导出功能

## 文档信息
- **项目名称**: 保质期管理系统批量导出功能
- **文档版本**: v1.0
- **创建日期**: 2026-02-20
- **技术栈**: PHP + MySQL
- **负责人**: 开发团队

---

## 一、需求概述

### 1.1 背景与目标
现有保质期管理系统已实现盘点数据的管理功能，但缺少将数据导出到本地的能力。用户希望能够将盘点数据导出为Excel格式，用于：
- 离线数据分析和报表制作
- 历史数据存档
- 跨部门数据共享
- 审计和合规性要求

### 1.2 用户角色
- **仓管员**: 日常盘点导出，用于分析库存周转
- **财务人员**: 导出数据进行成本核算
- **管理层**: 导出月度/季度报表用于决策
- **审计人员**: 导出历史数据进行合规审计

### 1.3 核心价值
1. 提升数据利用效率，支持离线分析
2. 满足数据存档和合规要求
3. 降低系统依赖，提高灵活性
4. 改善用户体验，减少手工录入

---

## 二、核心功能点

### 2.1 字段选择导出
- 支持自定义选择导出字段
- 预设常用导出模板（标准模板、财务模板、简明模板）
- 支持保存自定义字段配置

### 2.2 数据筛选
- 按日期范围筛选（生产日期、到期日期、盘点日期）
- 按商品分类筛选
- 按到期状态筛选（正常、临期、过期）
- 支持多条件组合筛选

### 2.3 Excel格式导出
- 导出为.xlsx格式（Excel 2007+）
- 清晰的中文表头
- 自动调整列宽
- 数据格式化（日期、数字、百分比）
- 冻结首行表头
- 添加导出时间水印

### 2.4 性能与安全
- 支持大批量数据导出（10万+记录）
- 导出进度提示
- 导出权限控制
- 导出日志记录

---

## 三、模块拆解

## Task 1: 数据库设计与优化

### 目标
设计支持导出功能的数据库结构，优化查询性能

### 工作内容
1. **设计导出配置表**
   ```sql
   CREATE TABLE export_templates (
     id INT PRIMARY KEY AUTO_INCREMENT,
     name VARCHAR(100) NOT NULL COMMENT '模板名称',
     fields JSON NOT NULL COMMENT '导出字段配置',
     created_by INT COMMENT '创建人ID',
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );
   ```

2. **设计导出日志表**
   ```sql
   CREATE TABLE export_logs (
     id INT PRIMARY KEY AUTO_INCREMENT,
     user_id INT NOT NULL COMMENT '操作用户ID',
     export_type VARCHAR(50) COMMENT '导出类型',
     record_count INT COMMENT '导出记录数',
     file_size BIGINT COMMENT '文件大小(字节)',
     filters JSON COMMENT '筛选条件',
     status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
     error_message TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

3. **优化盘点数据表索引**
   - 为生产日期字段添加索引
   - 为到期日期字段添加索引
   - 为盘点日期字段添加索引
   - 为分类字段添加索引

### 验收标准
- [ ] 导出配置表创建成功，支持JSON字段存储
- [ ] 导出日志表创建成功，记录完整操作信息
- [ ] 相关索引创建完成，查询性能提升
- [ ] 通过EXPLAIN验证查询计划最优

---

## Task 2: 后端API开发

### 目标
开发导出功能的后端接口，实现数据查询和Excel生成

### 工作内容

1. **安装依赖库**
   ```bash
   composer require phpoffice/phpspreadsheet
   ```

2. **创建导出服务类 ExportService.php**
   ```php
   <?php
   class ExportService {
       
       // 可导出字段定义
       private $availableFields = [
           'sku' => 'SKU编码',
           'product_name' => '商品名称',
           'category' => '商品分类',
           'production_date' => '生产日期',
           'expiry_date' => '到期日期',
           'quantity' => '库存数量',
           'unit' => '单位',
           'warehouse' => '仓库位置',
           'check_date' => '盘点日期',
           'status' => '到期状态',
           'days_to_expiry' => '剩余天数'
       ];
       
       /**
        * 执行导出
        */
       public function export($params) {
           // 1. 参数验证
           // 2. 构建查询
           // 3. 生成Excel
           // 4. 保存日志
       }
       
       /**
        * 构建查询
        */
       private function buildQuery($filters) {
           // 日期范围筛选
           // 分类筛选
           // 状态筛选
       }
       
       /**
        * 生成Excel文件
        */
       private function generateExcel($data, $fields) {
           // 创建Spreadsheet对象
           // 设置表头
           // 填充数据
           // 格式化
           // 保存文件
       }
   }
   ```

3. **创建导出控制器 ExportController.php**
   ```php
   <?php
   class ExportController {
       
       /**
        * 导出接口
        * POST /api/export
        */
       public function export() {
           // 获取请求参数
           // 调用ExportService
           // 返回文件下载
       }
       
       /**
        * 获取可导出字段
        * GET /api/export/fields
        */
       public function getFields() {
           // 返回可用字段列表
       }
       
       /**
        * 保存导出模板
        * POST /api/export/templates
        */
       public function saveTemplate() {
           // 保存字段配置
       }
       
       /**
        * 获取导出历史
        * GET /api/export/logs
        */
       public function getLogs() {
           // 返回导出历史记录
       }
   }
   ```

4. **实现数据查询优化**
   - 使用预处理语句防止SQL注入
   - 实现分批次查询（每批5000条）
   - 使用游标方式处理大数据集

### 验收标准
- [ ] 导出接口正常工作，支持自定义字段
- [ ] 日期筛选功能正确，边界条件处理完善
- [ ] Excel文件格式正确，表头清晰
- [ ] 10万条数据导出时间 < 30秒
- [ ] 内存使用合理，峰值 < 256MB
- [ ] 错误处理完善，失败有明确提示

---

## Task 3: 前端界面开发

### 目标
开发用户友好的导出配置界面

### 工作内容

1. **创建导出页面 export.php**
   ```html
   <div class="export-container">
       <!-- 筛选条件区域 -->
       <div class="filter-section">
           <h3>筛选条件</h3>
           <form id="filterForm">
               <div class="form-group">
                   <label>日期范围</label>
                   <input type="date" name="start_date" id="startDate">
                   <span>至</span>
                   <input type="date" name="end_date" id="endDate">
               </div>
               <div class="form-group">
                   <label>商品分类</label>
                   <select name="category" id="category">
                       <option value="">全部分类</option>
                       <!-- 动态加载 -->
                   </select>
               </div>
               <div class="form-group">
                   <label>到期状态</label>
                   <select name="status" id="status">
                       <option value="">全部</option>
                       <option value="normal">正常</option>
                       <option value="near">临期(30天内)</option>
                       <option value="expired">已过期</option>
                   </select>
               </div>
           </form>
       </div>
       
       <!-- 字段选择区域 -->
       <div class="fields-section">
           <h3>选择导出字段</h3>
           <div class="template-selector">
               <button class="template-btn" data-template="standard">标准模板</button>
               <button class="template-btn" data-template="finance">财务模板</button>
               <button class="template-btn" data-template="simple">简明模板</button>
           </div>
           <div class="field-checkboxes">
               <label><input type="checkbox" value="sku" checked> SKU编码</label>
               <label><input type="checkbox" value="product_name" checked> 商品名称</label>
               <label><input type="checkbox" value="category"> 商品分类</label>
               <label><input type="checkbox" value="production_date"> 生产日期</label>
               <label><input type="checkbox" value="expiry_date" checked> 到期日期</label>
               <label><input type="checkbox" value="quantity" checked> 库存数量</label>
               <!-- 更多字段 -->
           </div>
       </div>
       
       <!-- 操作按钮 -->
       <div class="action-section">
           <button id="exportBtn" class="btn-primary">导出Excel</button>
           <button id="saveTemplateBtn" class="btn-secondary">保存为模板</button>
       </div>
       
       <!-- 导出历史 -->
       <div class="history-section">
           <h3>导出历史</h3>
           <table id="historyTable">
               <thead>
                   <tr>
                       <th>导出时间</th>
                       <th>记录数</th>
                       <th>筛选条件</th>
                       <th>操作</th>
                   </tr>
               </thead>
               <tbody></tbody>
           </table>
       </div>
   </div>
   ```

2. **实现JavaScript交互 export.js**
   ```javascript
   // 导出按钮点击事件
   $('#exportBtn').on('click', function() {
       // 收集筛选条件
       const filters = {
           start_date: $('#startDate').val(),
           end_date: $('#endDate').val(),
           category: $('#category').val(),
           status: $('#status').val()
       };
       
       // 收集选中字段
       const fields = [];
       $('input[type="checkbox"]:checked').each(function() {
           fields.push($(this).val());
       });
       
       // 验证
       if (fields.length === 0) {
           alert('请至少选择一个导出字段');
           return;
       }
       
       // 显示加载动画
       showLoading();
       
       // 调用导出接口
       $.ajax({
           url: '/api/export',
           method: 'POST',
           data: {
               filters: filters,
               fields: fields
           },
           success: function(response) {
               // 触发文件下载
               window.location.href = response.download_url;
               hideLoading();
               // 刷新历史记录
               loadExportHistory();
           },
           error: function(xhr) {
               hideLoading();
               alert('导出失败：' + xhr.responseJSON.message);
           }
       });
   });
   
   // 模板快速选择
   $('.template-btn').on('click', function() {
       const template = $(this).data('template');
       applyTemplate(template);
   });
   
   // 日期范围快速选择
   $('#quickDateRange').on('change', function() {
       const range = $(this).val();
       setQuickDateRange(range);
   });
   ```

3. **添加样式 export.css**
   ```css
   .export-container {
       max-width: 1200px;
       margin: 0 auto;
       padding: 20px;
   }
   
   .filter-section, .fields-section {
       background: #f5f5f5;
       padding: 20px;
       margin-bottom: 20px;
       border-radius: 8px;
   }
   
   .field-checkboxes {
       display: grid;
       grid-template-columns: repeat(3, 1fr);
       gap: 10px;
       margin-top: 15px;
   }
   
   .field-checkboxes label {
       display: flex;
       align-items: center;
       cursor: pointer;
   }
   
   .btn-primary {
       background: #1890ff;
       color: white;
       padding: 10px 30px;
       border: none;
       border-radius: 4px;
       cursor: pointer;
   }
   
   .loading-overlay {
       position: fixed;
       top: 0;
       left: 0;
       right: 0;
       bottom: 0;
       background: rgba(0,0,0,0.5);
       display: flex;
       align-items: center;
       justify-content: center;
       z-index: 1000;
   }
   ```

### 验收标准
- [ ] 界面美观，交互流畅
- [ ] 字段选择功能正常，支持多选
- [ ] 日期筛选器正常工作，支持快捷选择
- [ ] 预设模板一键应用
- [ ] 导出进度有视觉反馈
- [ ] 导出历史实时更新
- [ ] 兼容主流浏览器（Chrome、Firefox、Edge）
- [ ] 响应式设计，支持不同屏幕尺寸

---

## Task 4: Excel格式化与美化

### 目标
生成专业、美观的Excel文件

### 工作内容

1. **实现Excel格式化**
   ```php
   private function formatExcel($spreadsheet) {
       // 获取活动工作表
       $sheet = $spreadsheet->getActiveSheet();
       
       // 设置表头样式
       $headerStyle = [
           'font' => [
               'bold' => true,
               'color' => ['rgb' => 'FFFFFF'],
               'size' => 11
           ],
           'fill' => [
               'fillType' => Fill::FILL_SOLID,
               'startColor' => ['rgb' => '4472C4']
           ],
           'alignment' => [
               'horizontal' => Alignment::HORIZONTAL_CENTER,
               'vertical' => Alignment::VERTICAL_CENTER
           ]
       ];
       
       // 应用表头样式
       $sheet->getStyle('A1:' . $lastColumn . '1')->applyFromArray($headerStyle);
       
       // 设置日期列格式
       $sheet->getStyle('D2:D' . $rowCount)
             ->getNumberFormat()
             ->setFormatCode('yyyy-mm-dd');
       
       // 设置数字列格式（千分位）
       $sheet->getStyle('F2:F' . $rowCount)
             ->getNumberFormat()
             ->setFormatCode('#,##0');
       
       // 冻结首行
       $sheet->freezePane('A2');
       
       // 自动调整列宽
       foreach (range('A', $lastColumn) as $col) {
           $sheet->getColumnDimension($col)->setAutoSize(true);
       }
       
       // 添加边框
       $borderStyle = [
           'borders' => [
               'allBorders' => [
                   'borderStyle' => Border::BORDER_THIN,
                                         'color' => ['rgb' => 'CCCCCC']
               ]
           ]
       ];
       $sheet->getStyle('A1:' . $lastColumn . $rowCount)->applyFromArray($borderStyle);
       
       // 添加条件格式（临期商品标红）
       $conditional = new Conditional();
       $conditional->setConditionType(Conditional::CONDITION_CELLIS)
                   ->setOperatorType(Conditional::OPERATOR_LESSTHAN)
                   ->addCondition('30');
       $conditional->getStyle()->getFont()->getColor()->setRGB('FF0000');
       $sheet->getStyle('J2:J' . $rowCount)
             ->setConditionalStyles([$conditional]);
   }
   ```

2. **添加数据水印**
   ```php
   private function addWatermark($spreadsheet) {
       $sheet = $spreadsheet->getActiveSheet();
       $timestamp = date('Y-m-d H:i:s');
       
       // 在最后一行添加导出信息
       $lastRow = $sheet->getHighestRow() + 2;
       $sheet->setCellValue('A' . $lastRow, "导出时间: {$timestamp}");
       $sheet->setCellValue('B' . $lastRow, "导出人: {$_SESSION['username']}");
       $sheet->getStyle('A' . $lastRow . ':B' . $lastRow)
             ->getFont()
             ->setColor(new Color('999999'));
   }
   ```

3. **实现多Sheet支持**（可选）
   - 汇总数据Sheet
   - 明细数据Sheet
   - 统计图表Sheet

### 验收标准
- [ ] 表头样式醒目，颜色搭配合理
- [ ] 日期格式正确（YYYY-MM-DD）
- [ ] 数字格式带千分位分隔符
- [ ] 冻结首行，滚动查看方便
- [ ] 列宽自动调整，内容完整显示
- [ ] 临期商品自动标红
- [ ] 导出时间水印清晰
- [ ] 文件大小合理（10万条约5MB）

---

## Task 5: 权限控制与日志

### 目标
确保导出功能安全可控

### 工作内容

1. **实现权限检查**
   ```php
   class ExportController {
       
       private function checkPermission() {
           // 检查用户是否登录
           if (!isset($_SESSION['user_id'])) {
               throw new Exception('用户未登录');
           }
           
           // 检查导出权限
           if (!$this->hasExportPermission($_SESSION['user_id'])) {
               throw new Exception('无导出权限');
           }
           
           // 检查导出频率限制（每小时最多10次）
           if ($this->exceedRateLimit($_SESSION['user_id'])) {
               throw new Exception('导出过于频繁，请稍后再试');
           }
       }
       
       private function hasExportPermission($userId) {
           // 检查用户角色权限
           // 管理员、仓管员、财务员可导出
       }
       
       private function exceedRateLimit($userId) {
           // 检查最近1小时导出次数
       }
   }
   ```

2. **实现导出日志**
   ```php
   private function logExport($params, $result) {
       $logData = [
           'user_id' => $_SESSION['user_id'],
           'export_type' => 'inventory',
           'record_count' => $result['count'],
           'file_size' => $result['file_size'],
           'filters' => json_encode($params['filters']),
           'fields' => json_encode($params['fields']),
           'status' => $result['success'] ? 'success' : 'failed',
           'error_message' => $result['error'] ?? null,
           'ip_address' => $_SERVER['REMOTE_ADDR'],
           'user_agent' => $_SERVER['HTTP_USER_AGENT']
       ];
       
       $this->db->insert('export_logs', $logData);
   }
   ```

3. **实现导出历史查询**
   ```php
   public function getExportHistory($userId, $limit = 20) {
       $sql = "SELECT * FROM export_logs 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?";
       
       return $this->db->query($sql, [$userId, $limit])->fetchAll();
   }
   ```

### 验收标准
- [ ] 未登录用户无法导出
- [ ] 无权限用户无法导出
- [ ] 导出频率限制生效
- [ ] 所有导出操作有日志记录
- [ ] 日志包含用户、时间、记录数等信息
- [ ] 可查询个人导出历史
- [ ] 管理员可查看所有导出日志

---

## Task 6: 性能优化与测试

### 目标
确保功能稳定、高效

### 工作内容

1. **实现分批次导出**
   ```php
   private function exportInBatches($params) {
       $batchSize = 5000;
       $offset = 0;
       $allData = [];
       
       while (true) {
           $batch = $this->queryData($params, $offset, $batchSize);
           
           if (empty($batch)) {
               break;
           }
           
           $allData = array_merge($allData, $batch);
           $offset += $batchSize;
           
           // 释放内存
           if ($offset % ($batchSize * 4) == 0) {
               gc_collect_cycles();
           }
       }
       
       return $allData;
   }
   ```

2. **实现异步导出**（大数据量）
   ```php
   // 创建导出任务
   public function createExportTask($params) {
       $taskId = uniqid('export_');
       
       // 将任务存入队列或数据库
       $this->saveTask($taskId, $params);
       
       // 返回任务ID
       return ['task_id' => $taskId, 'status' => 'pending'];
   }
   
   // 执行导出任务（后台进程）
   public function executeExportTask($taskId) {
       $task = $this->getTask($taskId);
       $result = $this->export($task['params']);
       $this->updateTask($taskId, $result);
   }
   ```

3. **编写测试用例**
   - 单元测试：字段映射、日期格式化
   - 集成测试：完整导出流程
   - 性能测试：不同数据量导出时间
   - 压力测试：并发导出

4. **性能基准**
   - 1,000条： < 2秒
   - 10,000条： < 5秒
   - 100,000条：< 30秒
   - 1,000,000条：< 5分钟（异步）

### 验收标准
- [ ] 小数据量（<1万）秒级响应
- [ ] 中数据量（1-10万）30秒内完成
- [ ] 大数据量（>10万）支持异步导出
- [ ] 内存使用稳定，无内存泄漏
- [ ] 并发导出不冲突
- [ ] 单元测试覆盖率 > 80%
- [ ] 通过性能压力测试

---

## 四、非功能性需求

### 4.1 性能要求
- 导出1万条数据 < 5秒
- 导出10万条数据 < 30秒
- 支持最多5个并发导出

### 4.2 安全要求
- 导出权限与用户角色绑定
- 敏感数据脱敏（如有需要）
- 导出日志完整记录
- 防止导出攻击（频率限制）

### 4.3 兼容性要求
- Excel版本：2007及以上
- 浏览器：Chrome 90+、Firefox 88+、Edge 90+
- PHP版本：7.4及以上
- MySQL版本：5.7及以上

### 4.4 可维护性要求
- 代码注释完整
- 遵循PSR编码规范
- 错误日志详细
- 便于扩展新字段

---

## 五、实施计划

### 5.1 开发排期（共5天）

| 阶段 | 任务 | 工作量 | 负责人 |
|------|------|--------|--------|
| Day 1 | Task 1: 数据库设计与优化 | 0.5天 | 后端开发 |
| Day 1-2 | Task 2: 后端API开发 | 1.5天 | 后端开发 |
| Day 2-3 | Task 3: 前端界面开发 | 1.5天 | 前端开发 |
| Day 3 | Task 4: Excel格式化 | 0.5天 | 后端开发 |
| Day 4 | Task 5: 权限控制与日志 | 0.5天 | 后端开发 |
| Day 4-5 | Task 6: 性能优化与测试 | 1天 | 全员 |
| Day 5 | 联调测试与上线 | 0.5天 | 全员 |

### 5.2 里程碑
- M1: 数据库设计完成（Day 1结束）
- M2: 后端API开发完成（Day 2结束）
- M3: 前端界面完成（Day 3结束）
- M4: 功能联调通过（Day 4结束）
- M5: 正式上线（Day 5结束）

---

## 六、风险评估

### 6.1 技术风险
| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 大数据量导出内存溢出 | 高 | 中 | 分批次查询、及时释放内存 |
| Excel生成超时 | 中 | 中 | 设置合理超时时间，使用异步导出 |
| 依赖库兼容性问题 | 低 | 低 | 充分测试，准备降级方案 |

### 6.2 业务风险
| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 用户导出敏感数据 | 高 | 中 | 权限控制、日志审计 |
| 频繁导出影响系统性能 | 中 | 中 | 导出频率限制 |
| 导出文件过大下载困难 | 低 | 低 | 提供保留24小时下载链接 |

---

## 七、成功标准

### 7.1 功能完整性
- ✅ 支持自定义字段选择
- ✅ 支持多种筛选条件
- ✅ 导出Excel格式正确
- ✅ 表头清晰、格式美观

### 7.2 用户体验
- ✅ 操作简单直观
- ✅ 导出速度满足要求
- ✅ 错误提示清晰
- ✅ 进度反馈及时

### 7.3 系统稳定性
- ✅ 无内存泄漏
- ✅ 并发导出正常
- ✅ 权限控制有效
- ✅ 日志记录完整

---

## 八、后续优化方向

### 8.1 短期优化（1-2个月）
- 增加定时自动导出功能
- 支持导出到云存储（OSS）
- 增加导出数据对比功能
- 优化大数据量导出性能

### 8.2 长期规划（3-6个月）
- 支持导出为其他格式（CSV、PDF）
- 增加数据可视化图表
- 实现导出模板市场
- 支持导出数据邮件发送

---

## 附录

### A. 可导出字段清单

| 字段代码 | 字段名称 | 数据类型 | 示例值 |
|---------|---------|---------|--------|
| sku | SKU编码 | 字符串 | SP202501001 |
| product_name | 商品名称 | 字符串 | 有机牛奶1L |
| category | 商品分类 | 字符串 | 乳制品 |
| brand | 品牌 | 字符串 | 伊利 |
| specification | 规格 | 字符串 | 1L/盒 |
| unit | 单位 | 字符串 | 盒 |
| production_date | 生产日期 | 日期 | 2024-12-01 |
| expiry_date | 到期日期 | 日期 | 2025-06-01 |
| quantity | 库存数量 | 数字 | 500 |
| warehouse | 仓库位置 | 字符串 | A区-01-01 |
| check_date | 盘点日期 | 日期 | 2025-01-15 |
| checker | 盘点人 | 字符串 | 张三 |
| status | 到期状态 | 字符串 | 正常/临期/过期 |
| days_to_expiry | 剩余天数 | 数字 | 132 |
| batch_no | 批次号 | 字符串 | 20241201-001 |

### B. 预设模板配置

**标准模板**（适用于日常盘点）
- 包含字段：SKU、商品名称、分类、生产日期、到期日期、数量、仓库、盘点日期、到期状态

**财务模板**（适用于成本核算）
- 包含字段：SKU、商品名称、规格、数量、单位、单价、金额、到期日期

**简明模板**（适用于快速查看）
- 包含字段：SKU、商品名称、到期日期、数量、到期状态

### C. API接口文档

#### 导出接口
```
POST /api/export
Content-Type: application/json

请求体：
{
  "filters": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "category": "乳制品",
    "status": "near"
  },
  "fields": ["sku", "product_name", "expiry_date", "quantity"]
}

响应：
{
  "success": true,
  "download_url": "/downloads/export_20250120_143025.xlsx",
  "record_count": 1523,
  "file_size": 245760
}
```

#### 获取可导出字段
```
GET /api/export/fields

响应：
{
  "success": true,
  "fields": {
    "sku": "SKU编码",
    "product_name": "商品名称",
    ...
  }
}
```

---

**文档结束**

*本文档为需求规格说明书，具体实现细节以最终代码为准*
