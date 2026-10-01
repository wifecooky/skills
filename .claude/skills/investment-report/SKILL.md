---
name: investment-report
description: 生成专业券商风格的投研报告（HTML单文件）。输入行业或标的，自动完成数据搜集、横向对比、深度分析、组合策略，输出可直接在浏览器打开的精美研报。
---

# 投研报告生成器

## 工作流程

按以下步骤顺序执行。每一步都必须完成后才进入下一步。

### STEP 1: 确认需求

用 AskUserQuestion 收集以下信息（未指定的参数才需要询问）：

| 参数 | 选项 | 默认值 |
|------|------|--------|
| 行业方向 | 用户指定 | 必填 |
| 推荐标的数 | 2 / 3 / 4 | 3 |
| 配色方案 | A券商经典 / B科技成长 / C消费医药 | 根据行业自动选 |
| 保存路径 | 桌面 / 文档 / 当前目录 | ~/Documents/ |

配色自动选择规则：
- 周期行业/传统行业/金融 → 方案A（深蓝#1a2744 + 金色#c9a84c）
- 科技/新能源/成长赛道 → 方案B（深灰#1e2a3a + 青绿#00b894）
- 消费/医药/防御型 → 方案C（深蓝#2c3e50 + 橙红#e74c3c）

### STEP 2: 数据搜集

使用 WebSearch 并行搜索以下数据（至少5次搜索）：

1. **行业全景**：行业估值分位数、PE/PB历史水位、周期定位
2. **候选龙头**：7~8家行业代表性公司的基本面数据
3. **逐家深挖**（并行）：每家公司的 PE、PB、股息率、净利润、核心优势、核心风险
4. **行业催化剂**：政策变化、供需拐点、价格走势
5. **宏观背景**：利率环境、资金流向、机构持仓变化

每个公司至少收集：代码、PE、PB、股息率/利润增速、现金流/负债率、核心竞争力、主要风险。

### STEP 3: 分析与筛选

基于数据完成以下分析（在思考中完成，不需要单独输出）：

1. 从候选池（7~8家）中按"安全性+弹性"或"估值+成长"双维度打分
2. 淘汰不符合标准的公司，给出一句话淘汰理由
3. 确定最终推荐标的（用户指定数量）
4. 确定每只标的的角色定位和仓位占比
5. 确定组合的互补逻辑

### STEP 4: 生成报告

输出单文件 HTML（内嵌CSS），结构如下：

```
1. 封面/标题区
   - 报告类型标签（行业深度研究 / 公司深度 / 专题研究）
   - 标题 + 副标题
   - 日期、行业、评级

2. 核心观点摘要（3~5条）
   - summary-box 组件
   - 投资逻辑链 logic-flow 组件（4节点）

3. 行业现状分析
   - 周期定位论证（3~5个 highlight-card）
   - 供需格局
   - 估值水位

4. 横向对比筛选表
   - 全部候选（7~8家）对比表
   - 入选/淘汰表（badge标注）
   - 每家淘汰理由

5. 标的深度分析（重复N次，每个推荐标的一节）
   - stock-card 组件（header + body）
   - kpi-grid（4个核心指标）
   - highlight-card.green（核心竞争力，3~4条）
   - 盈利弹性/增长测算
   - highlight-card.red（主要风险）

6. 组合策略与仓位建议
   - position-bar（仓位可视化条）
   - 角色/代码/仓位/买入逻辑/卖出信号 表格
   - 互补维度对比表
   - 催化剂时间表

7. 风险提示
   - risk-box（5~8项）

8. 免责声明
   - disclaimer 组件
```

### STEP 5: 打开验证

用 `open` 命令在浏览器中打开生成的 HTML 文件。

---

## CSS 组件规范

所有报告必须包含以下组件的 CSS 定义：

```
核心组件：
- .cover              封面区（渐变背景 + 标签 + 标题 + 元信息）
- .summary-box        核心观点摘要（深色背景 + 亮色要点列表）
- .highlight-card      关键论据卡片（左侧色条 .green/.red 变体）
- .stock-card          个股分析卡片（header + body 结构）
- .kpi-grid            4宫格关键指标（grid 布局）
- .strategy-box        组合策略区域
- .position-bar        仓位比例可视化条（flex 分段）
- .risk-box            风险提示区域（暖色背景 + ⚠ 图标列表）
- .logic-flow          逻辑链流程图（节点 + 箭头）
- .table-wrapper       响应式表格（深色表头、斑马纹、hover、row-highlight）
- .disclaimer          免责声明（灰色低调区域）
- .badge               标签（badge-green/red/orange/blue 变体）
- .two-col             双栏对比布局

布局规范：
- 最大宽度 920px 居中
- 移动端断点 640px
- 打印时 page-break-inside: avoid
```

---

## 配色方案详细定义

### 方案A：券商经典（周期/金融/传统行业）
```css
--primary: #1a2744;  --primary-light: #2c3e6b;
--accent: #c9a84c;   --accent-light: #e8d5a0;
```

### 方案B：科技成长（科技/新能源/成长赛道）
```css
--primary: #1e2a3a;  --primary-light: #34495e;
--accent: #00b894;   --accent-light: #b2dfdb;
```

### 方案C：消费医药（消费/医药/防御型）
```css
--primary: #2c3e50;  --primary-light: #445566;
--accent: #e74c3c;   --accent-light: #f5b7b1;
```

通用色值（所有方案共享）：
```css
--text: #2c2c2c;  --text-light: #666;  --bg: #fff;
--bg-alt: #f7f8fb; --border: #dde1e8;
--red: #c0392b;  --green: #27ae60;  --orange: #e67e22;
```

---

## 质量标准

生成完成后自检：

- [ ] HTML 文件能独立在浏览器中正常渲染
- [ ] 所有数据与搜索结果一致，无编造
- [ ] 表格在移动端可横向滚动
- [ ] 每个标的都有 KPI卡片 + 竞争力 + 风险
- [ ] 仓位建议有明确的买入逻辑和卖出信号
- [ ] 风险提示覆盖系统性风险和标的特有风险
- [ ] 免责声明已包含
- [ ] 配色一致，无色彩冲突

---

## 文件命名规范

`{行业英文}-investment-report.html`

示例：
- photovoltaic-investment-report.html
- chemical-industry-investment-report.html
- high-dividend-investment-report.html
- consumer-staples-investment-report.html
