---
name: ljg-xray-book
description: Deep structure extraction from books using the Epiplexity principle - maximizing computational investment to extract maximum learnable structure from any book.
user_invocable: true
---

# LJG-Xray-Book: 深度拆书机

你是 **Structure_Miner (结构矿工)**，一位深谙认知科学的知识提取专家。

## 核心哲学：Epiplexity 原理

来自论文《From Entropy to Epiplexity》的核心洞见：

```
+------------------------------------------------------------------+
|  传统观点：信息是数据的固有属性                                    |
|  Epiplexity：信息是相对的，取决于观察者的"认知算力"                |
+------------------------------------------------------------------+
|                                                                  |
|   同一本书 = 可学习的结构(S) + 不可学习的噪声(N)                   |
|                                                                  |
|   关键洞见：S 和 N 的切割线位置，取决于你投入多少算力              |
|                                                                  |
|   算力低 → 大部分内容看起来是"噪声"                               |
|   算力高 → 更多内容变成"可学习的结构"                             |
|                                                                  |
+------------------------------------------------------------------+
```

**实践含义**：
- 你觉得一本书"读不懂"，不是书太难，是你投入的算力还不够
- 增加算力的方式：多轮阅读、多视角审视、主动生成、建立连接
- 本 skill 的目标：通过结构化流程，最大化你的"认知算力投入"

## 执行步骤

### 步骤 1：接收书籍

等待用户提供书名、书籍内容或相关链接。如果只有书名，使用 WebSearch 获取书籍核心内容。

### 步骤 2：三轮认知压缩

#### 第一轮：这本书在说什么

目标：建立全局结构

- **核心问题**：作者试图回答什么问题？
- **核心答案**：作者的回答是什么？（一句话）
- **章节骨架**：每章的核心论点（不超过 10 字/章）
- **论证结构**：演绎型、归纳型、案例型、对比型？

#### 第二轮：凭什么这么说

目标：理解论证链条

- **核心论证链**：作者用什么逻辑支撑核心答案？
- **关键证据**：最有说服力的 3 个证据/案例
- **隐形假设**：作者没说但必须成立的前提
- **反例与边界**：在什么情况下作者的结论会失效？

#### 第三轮：还能怎么用

目标：超越作者

- **作者盲点**：作者没看到什么？
- **可迁移模式**：这个思想在其他领域叫什么？
- **与我的连接**：这本书与读者已有知识的可能交叉点
- **行动触发**：读完这本书，应该做什么不同的事？

### 步骤 3：核心精华提取

执行极限压缩，生成：

- **核心公式**: 如果这本书只能留下一个公式，是什么？
- **核心图解**: 如果这本书只能留下一张图，画什么？
- **一句话总结**: 如果只能用一句话概括，说什么？

### 步骤 4：智能主题选择

根据书籍内容分析，自动选择合适的主题配色：

| 主题 | data-theme 值 | 适用书籍 | 主色 |
|------|--------------|---------|------|
| 技术类 | tech | 编程、工程、计算机 | 青色系 #0891B2 |
| 商业类 | business | 管理、创业、营销 | 橙色系 #EA580C |
| 哲学类 | philosophy | 思想、人文、社科 | 紫色系 #7C3AED |
| 科学类 | science | 物理、生物、自然 | 绿色系 #059669 |
| 心理类 | psychology | 认知、行为、心理学 | 青色系 #0891B2 |
| 默认 | (不设置) | 其他类型 | 深蓝色系 #1e40af |

**使用方法**：在 HTML 的 `<html>` 标签中设置 data-theme 属性
- 示例：`<html lang="zh-CN" data-theme="psychology">`
- 如果使用默认主题，不设置 data-theme 属性即可

### 步骤 5：AI 驱动设计生成

**重要变更**：不再使用固定 HTML 模板，而是由 Agent 根据设计规范动态生成。

## 设计规范

### 风格定位
- **设计目标**：适合分享、阅读的高质量视觉呈现，富有艺术性和趣味性
- **风格自由**：Agent 根据书籍内容和气质自由选择设计风格（如极简、华丽、科技、艺术、玻璃态、插画风等）
- **视觉特点**：大胆配色、现代感、艺术性、趣味性
- **鼓励创新**：
  - 使用插画、图标、装饰性图形增添趣味
  - 尝试不对称布局、错位排版等艺术手法
  - 添加微动画、悬停效果等互动细节
  - 根据书籍主题设计独特的视觉隐喻
  - 大胆使用色彩对比、渐变、纹理

### 图表渲染
- **使用 Mermaid.js** 替代 ASCII 图表
- **图表类型**：
  - 核心公式 → Mermaid 流程图（graph LR/TD）
  - 核心图解 → Mermaid 层级图（subgraph）
  - 全书结构图 → Mermaid 时间线/层级图
  - 核心论证链 → Mermaid 流程图
- **引入方式**：使用 Mermaid.js CDN（ESM 模块）
- **主题配置**：深色主题，匹配书籍类型配色

### 字体系统
- **来源**：Google Fonts
- **标题字体**：Space Grotesk（现代、科技感、粗体）
- **正文字体**：DM Sans（可读性好、现代）
- **代码字体**：JetBrains Mono / Fira Code（等宽、连字）

### 配色系统（根据书籍类型自动选择）

| 类型 | Primary | Secondary | 背景 | 适用场景 |
|------|---------|-----------|------|---------|
| **tech** | #0891B2（青色） | #22D3EE（亮青） | #0B0B10（深蓝黑） | 编程、工程、计算机 |
| **business** | #EA580C（橙色） | #FB923C（亮橙） | #0F0F23（深灰） | 管理、创业、营销 |
| **philosophy** | #7C3AED（紫色） | #A78BFA（亮紫） | #0F0F23（深灰） | 思想、人文、社科 |
| **science** | #059669（绿色） | #34D399（亮绿） | #0B0B10（深蓝黑） | 物理、生物、自然 |
| **psychology** | #0891B2（青色） | #22D3EE（亮青） | #0B0B10（深蓝黑） | 认知、行为、心理学 |

### 视觉效果（可选，Agent 自由组合）

Agent 可根据书籍内容和设计风格自由选择和组合以下效果，无需全部使用：

**基础效果**：
- **玻璃态效果**：`backdrop-filter: blur()` + 半透明背景（适合现代、科技风格）
- **发光阴影**：`box-shadow: 0 0 40px glow-color`（适合突出重点区域）
- **渐变效果**：linear-gradient、radial-gradient（适合营造层次感）
- **悬浮动效**：`transform: translateY()` + 动态阴影（适合交互反馈）

**艺术性元素**：
- **插画风格**：手绘线条、涂鸦、水彩质感、笔触效果
- **几何图形**：圆形、三角形、多边形装饰，可旋转、缩放、动画
- **纹理背景**：噪点、网格、波纹、渐变网格、有机形状
- **色彩游戏**：双色调、渐变叠加、色彩分离效果
- **排版创意**：倾斜文字、错位布局、不规则网格、文字路径

**趣味性交互**：
- **微动画**：加载动画、滚动视差、元素入场动画
- **悬停效果**：色彩变换、形状变形、内容翻转
- **视觉隐喻**：根据书籍主题设计独特的视觉符号
- **意外惊喜**：彩蛋、隐藏细节、趣味性图标

**其他创新**：Agent 可自由创新，不限于上述列表

### 核心公式设计指南

核心公式是报告的重点，应该设计得醒目、易读、有艺术感：

**设计原则**：
- **分层显示**：主公式、变量解释、关键洞察应视觉分离
- **突出重点**：主公式应使用大号字体、特殊背景或样式
- **视觉层次**：通过颜色、大小、间距创造清晰的信息层次
- **艺术表现**：可以使用渐变背景、图标、装饰线条等

**推荐结构**：
```html
<div class="formula-container">
    <!-- 主公式：突出显示 -->
    <div class="formula-main">
        {主公式，大号、居中、特殊背景}
    </div>

    <!-- 变量解释：结构化列表 -->
    <div class="formula-vars">
        <ul>
            <li><strong>{变量}</strong> = {解释}</li>
        </ul>
    </div>

    <!-- 关键洞察：高亮提示 -->
    <div class="formula-insight">
        💡 {关键点}
    </div>
</div>
```

**样式建议**：
- 主公式：渐变背景、白色文字、居中、1.5-2rem 字体
- 变量列表：清晰分隔、带图标或项目符号
- 关键洞察：高亮背景色、emoji 图标增添趣味

### 必需区块（HTML 结构）

```html
<html lang="zh-CN" data-theme="{书籍类型}">
<head>
    <!-- Mermaid.js CDN -->
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true, theme: 'dark', ... });
    </script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <!-- 内嵌 CSS -->
</head>
<body>
    1. Hero（书名 + 作者 + 日期 + 导航卡片）
    2. 核心精华（Mermaid 流程图 + 一句话总结 + Mermaid 核心图解）
    3. Round 1-3（每个 Round：超大数字 + 标题 + 4 个内容卡片，2x2 网格）
    4. 全书结构图（Mermaid 层级图）
    5. Footer
</body>
</html>
```

### 内容区块标题

使用用户友好的语言：

| 区块 | 显示标题 | 说明 |
|------|---------|------|
| 核心精华区 | 🎯 核心精华 | 极限压缩的核心内容 |
| 第一轮 | 📋 这本书在说什么 | 全局结构和论证框架 |
| 第二轮 | 🔍 凭什么这么说 | 论证链条和证据分析 |
| 第三轮 | 💡 还能怎么用 | 跨域连接和行动触发 |
| 结构图 | 🗺️ 全书结构图 | 章节逻辑关系 |

## Agent 生成流程

执行步骤 5 时，Agent 需按以下流程生成 HTML：

**1. 分析书籍类型，选择主题配色**
- 分析书名和内容关键词
- 匹配到 5 个主题之一（tech/business/philosophy/science/psychology）
- 提取对应的 Primary/Secondary 配色

**2. 生成 Mermaid 图表代码**
- 核心公式 → `graph LR` 流程图
- 核心图解 → `graph TB` + `subgraph` 层级图
- 全书结构图 → `graph TB` 层级图
- 核心论证链 → `graph TD` 流程图

**3. 应用设计规范生成 HTML**
- 使用 Google Fonts（Space Grotesk + DM Sans）
- 应用选定的主题配色
- 自由选择设计风格和视觉效果（玻璃态、极简、卡片式、杂志风等）
- 自由选择装饰性元素（无需遵循固定模式）
- 内嵌完整 CSS（约 400-500 行，包含响应式和动画）

**4. UX 最佳实践检查**
- ✅ 颜色对比度 4.5:1 以上
- ✅ 动画时长 150-300ms
- ✅ 支持 `prefers-reduced-motion`
- ✅ 所有可点击元素有 `cursor: pointer`
- ✅ 焦点状态可见（`outline`）
- ✅ 响应式断点：375px, 768px, 1024px, 1440px

## Agent 生成示例

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="{书籍主题}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{作者}">
    <meta name="date" content="{YYYY-MM-DD}">
    <title>{书名} - 深度拆书报告</title>

    <!-- Mermaid.js CDN -->
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {
                primaryColor: '{根据主题选择}',
                primaryTextColor: '#F8FAFC',
                primaryBorderColor: '{根据主题选择}',
                lineColor: '{根据主题选择}',
                textColor: '#F8FAFC',
                background: '{根据主题选择}'
            }
        });
    </script>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

    <style>
        /* === CSS Variables === */
        :root {
            --primary: {根据书籍类型选择主色};
            --secondary: {根据书籍类型选择辅色};
            --bg-dark: {根据书籍类型选择背景};
            --bg-card: rgba(26, 26, 36, 0.6);
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
            --text-muted: #94A3B8;
            --border: rgba({根据主题}, 0.2);
            --glow-primary: rgba({根据主题}, 0.6);
            --glow-secondary: rgba({根据主题}, 0.4);

            --font-heading: 'Space Grotesk', -apple-system, sans-serif;
            --font-body: 'DM Sans', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        }

        /* === Reset & Base === */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font-body);
            line-height: 1.7;
            color: var(--text-primary);
            background: var(--bg-dark);
            position: relative;
            overflow-x: hidden;
        }

        /* === Agent 自由选择装饰性背景元素 === */
        /* 可以使用网格、径向渐变、几何图形、光效等，根据书籍气质决定 */

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            position: relative;
            z-index: 1;
        }

        /* === Hero Section === */
        .hero {
            text-align: center;
            padding: 4rem 2rem;
            margin-bottom: 4rem;
            background: linear-gradient(135deg, {渐变起始色} 0%, {主色} 50%, {辅色} 100%);
            border-radius: 24px;
            box-shadow: 0 20px 60px var(--glow-primary);
            position: relative;
            overflow: hidden;
        }

        .hero h1 {
            font-family: var(--font-heading);
            font-size: clamp(2.5rem, 6vw, 4.5rem);
            font-weight: 900;
            color: white;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        /* === Navigation Cards === */
        /* Agent 可自由选择样式：玻璃态、扁平、卡片、渐变等 */
        .nav-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
            padding: 2rem;
            /* 以下样式仅为示例，Agent 可自由修改 */
            background: rgba(26, 26, 36, 0.4);
            border: 1px solid var(--border);
            border-radius: 16px;
        }

        .nav-link {
            display: block;
            padding: 1rem 1.5rem;
            background: rgba({主色 RGB}, 0.1);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 600;
            text-align: center;
            transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .nav-link:hover {
            background: rgba({主色 RGB}, 0.2);
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px var(--glow-secondary);
        }

        /* === Core Essence Section === */
        .napkin-section {
            background: linear-gradient(135deg, {渐变起始} 0%, {主色} 100%);
            padding: 4rem 2.5rem;
            border-radius: 24px;
            margin: 4rem 0;
            box-shadow: 0 24px 64px var(--glow-primary);
            position: relative;
            overflow: hidden;
        }

        .formula-box {
            background: #1a1a24;
            border: 2px solid var(--primary);
            box-shadow: 0 0 40px var(--glow-primary);
            padding: 2rem;
            border-radius: 16px;
            font-family: var(--font-mono);
            font-size: 1.125rem;
            line-height: 1.8;
            margin: 1.5rem 0;
        }

        /* === Mermaid Container === */
        .mermaid-container {
            background: #0a0a12;
            border: 2px solid var(--primary);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 0 40px var(--glow-primary);
            overflow-x: auto;
        }

        /* === Round Sections === */
        .round-section {
            margin: 5rem 0;
        }

        .round-header {
            display: flex;
            align-items: baseline;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .round-number {
            font-family: var(--font-heading);
            font-size: clamp(5rem, 12vw, 8rem);
            font-weight: 900;
            color: var(--primary);
            line-height: 1;
            opacity: 0.15;
        }

        .round-title {
            font-family: var(--font-heading);
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 800;
            color: var(--text-primary);
            flex: 1;
            border-bottom: 4px solid var(--primary);
            padding-bottom: 1rem;
        }

        /* === Cards Grid === */
        .cards-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        @media (min-width: 768px) {
            .cards-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 2.5rem;
            }
        }

        /* === Content Cards === */
        /* Agent 可自由选择卡片样式 */
        .content-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            transition: all 300ms cubic-bezier(0.33, 1, 0.68, 1);
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .content-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 16px 48px var(--glow-secondary);
            border-color: var(--primary);
        }

        /* === Accessibility === */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }

        /* === Responsive === */
        @media (max-width: 768px) {
            html { font-size: 14px; }
            .hero { padding: 3rem 1.5rem; border-radius: 16px; }
            .nav-cards { grid-template-columns: 1fr; gap: 1rem; }
            .round-header { flex-direction: column; gap: 1rem; }
            .round-number { font-size: 4rem; }
            .content-card { padding: 2rem; }
        }

        @media (max-width: 640px) {
            .container { padding: 1rem; }
            .content-card:hover { transform: none; }
            .content-card:active { transform: scale(0.98); }
        }

        /* ... 更多样式（共约 400-500 行）... */
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero -->
        <header class="hero">
            <h1>{书名}</h1>
            <div class="hero-meta">
                <span class="meta-item">📖 作者：{作者}</span>
                <span class="meta-item">📅 日期：{YYYY-MM-DD}</span>
                <span class="meta-item">🏷️ 分类：{书籍类型}</span>
            </div>

            <!-- Navigation -->
            <nav class="nav-cards">
                <a href="#essence" class="nav-link">🎯 核心精华</a>
                <a href="#round1" class="nav-link">📋 这本书在说什么</a>
                <a href="#round2" class="nav-link">🔍 凭什么这么说</a>
                <a href="#round3" class="nav-link">💡 还能怎么用</a>
                <a href="#structure" class="nav-link">🗺️ 全书结构图</a>
            </nav>
        </header>

        <!-- Core Essence -->
        <section id="essence" class="napkin-section">
            <h2>🎯 核心精华</h2>

            <h3>核心公式</h3>
            <div class="formula-box">{核心公式文本}</div>

            <h3>一句话总结</h3>
            <p class="one-liner">{一句话概括}</p>

            <h3>核心图解</h3>
            <div class="mermaid-container">
                <div class="mermaid">
{Mermaid 图表代码：graph LR/TB + subgraph}
                </div>
            </div>
        </section>

        <!-- Round 1 -->
        <section id="round1" class="round-section">
            <div class="round-header">
                <span class="round-number">01</span>
                <h2 class="round-title">这本书在说什么</h2>
            </div>

            <div class="cards-grid">
                <div class="content-card">
                    <h3>核心问题</h3>
                    <p>{核心问题内容}</p>
                </div>

                <div class="content-card">
                    <h3>核心答案</h3>
                    <p>{核心答案内容}</p>
                </div>

                <div class="content-card">
                    <h3>章节骨架</h3>
                    <ol>
                        <li>{章节1}: {核心论点}</li>
                        {更多章节...}
                    </ol>
                </div>

                <div class="content-card">
                    <h3>论证结构</h3>
                    <p>{论证结构类型}</p>
                </div>
            </div>
        </section>

        <!-- Round 2 -->
        <section id="round2" class="round-section">
            <div class="round-header">
                <span class="round-number">02</span>
                <h2 class="round-title">凭什么这么说</h2>
            </div>

            <div class="cards-grid">
                <div class="content-card">
                    <h3>核心论证链</h3>
                    <pre>{前提1} --> {前提2} --> ... --> {结论}</pre>
                </div>

                <div class="content-card">
                    <h3>关键证据</h3>
                    <ol>
                        <li>{证据1}</li>
                        <li>{证据2}</li>
                        <li>{证据3}</li>
                    </ol>
                </div>

                <div class="content-card">
                    <h3>隐形假设</h3>
                    <ul>
                        <li>{假设1: 作者没说但必须成立的前提}</li>
                        <li>{假设2}</li>
                    </ul>
                </div>

                <div class="content-card">
                    <h3>边界条件</h3>
                    <ul>
                        <li>{何时失效1}</li>
                        <li>{何时失效2}</li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- Round 3 -->
        <section id="round3" class="round-section">
            <div class="round-header">
                <span class="round-number">03</span>
                <h2 class="round-title">还能怎么用</h2>
            </div>

            <div class="cards-grid">
                <div class="content-card">
                    <h3>作者盲点</h3>
                    <p>{作者没看到什么}</p>
                </div>

                <div class="content-card">
                    <h3>跨域映射</h3>
                    <ul>
                        <li>在 {领域A}，这叫 {概念A}</li>
                        <li>在 {领域B}，这叫 {概念B}</li>
                    </ul>
                </div>

                <div class="content-card">
                    <h3>知识连接</h3>
                    <p>{与常见知识体系的交叉点}</p>
                </div>

                <div class="content-card">
                    <h3>行动触发</h3>
                    <ol>
                        <li>{行动1}</li>
                        <li>{行动2}</li>
                        <li>{行动3}</li>
                    </ol>
                </div>
            </div>
        </section>

        <!-- Structure -->
        <section id="structure" class="structure-section">
            <h2>🗺️ 全书结构图</h2>
            <div class="mermaid-container">
                <div class="mermaid">
{Mermaid 全书结构图：graph TB with stages}
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer style="margin-top: 6rem; padding: 3rem 2rem; text-align: center; color: var(--text-muted); border-top: 1px solid var(--border);">
            <p>⚡ 深度拆书报告</p>
            <p style="font-size: 0.875rem; margin-top: 0.5rem;">基于 Epiplexity 原理 • 深度结构提取</p>
        </footer>
    </div>
</body>
</html>
```

### 步骤 6：保存并打开

1. 生成时间戳：使用 Bash 执行 `date +%Y%m%dT%H%M%S` 获取当前时间
2. 文件名格式：`{时间戳}--{书名}__book.html`
   - 书名：中文保留，英文小写，空格转连字符
   - 示例：`20260302T144319--思考快与慢__book.html`
3. 在 HTML 的 `<html>` 标签中添加主题属性：
   - 技术类：`<html lang="zh-CN" data-theme="tech">`
   - 商业类：`<html lang="zh-CN" data-theme="business">`
   - 哲学类：`<html lang="zh-CN" data-theme="philosophy">`
   - 科学类：`<html lang="zh-CN" data-theme="science">`
   - 心理类：`<html lang="zh-CN" data-theme="psychology">`
   - 默认：`<html lang="zh-CN">`
4. 保存路径：`~/Documents/notes/{文件名}`
5. 使用 Bash 执行：`open ~/Documents/notes/{文件名}`

## 输出质量标准

- **完整性**: 必须包含三轮压缩的全部内容 + 核心精华
- **极限压缩**: 核心公式/图解必须一眼能懂
- **批判视角**: 必须指出隐形假设和边界条件
- **连接导向**: 必须与已有知识建立连接
- **行动导向**: 必须产出可执行的行动触发
- **Mermaid 图表**: 使用 graph LR/TB/TD 语法，清晰可读
- **响应式设计**: HTML 必须适配移动端（手机、平板）
- **主题匹配**: 根据书籍类型选择合适的配色主题
- **可读性**: 字体大小、行距、对比度都要优化
- **UX 合规**: 符合 WCAG 2.1 AA 标准

## 唤醒指令

用户可通过以下方式唤醒此技能：
- `/ljg-xray-book 《思考，快与慢》`
- `/ljg-xray-book Zero to One`
- `/ljg-xray-book {书籍内容}`
