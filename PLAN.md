# AI Builders Digest 网站实施计划

## 核心判断

Fork digest-factory 模板，针对 ai-builders-brief 的 3 种数据源（推文/播客/博客）做外科手术式改造。不重新造轮子。

## 架构

```
公共 feed JSON (GitHub raw) → collect-feeds.js → remix-ai.js → translate-ai.js → SvelteKit 静态站
```

与 digest-factory 的区别：数据来源从 RSS 改为 3 个公共 JSON feed，内容组织从 2 区（featured/quickNews）改为 3 区（builderInsights/podcastHighlights/blogUpdates）。

## 项目位置

`/Users/wenping.wang/Documents/git/ai-builders-digest/`

## 实施步骤

### Step 1: 初始化项目
- 从 digest-factory 复制基础结构（frontend/、scripts/lib/、.github/）
- 删除不需要的文件：collect-rss.js、filter-ai.js、rss-parser.js、similarity.js、weekly 相关
- 创建 site.yaml（indigo 主题色，区别于其他 digest 站点）

### Step 2: 数据采集脚本 `scripts/collect-feeds.js`
- 从 3 个公共 URL 抓取 feed JSON：
  - `feed-x.json`（推文）
  - `feed-podcasts.json`（播客）
  - `feed-blogs.json`（博客）
- 合并输出到 `content/raw-feeds.json`
- ~50 行代码，纯 fetch + 写文件

### Step 3: AI 内容加工脚本 `scripts/remix-ai.js`
- 读取 raw-feeds.json + prompts 模板
- 对每位 builder 的推文调用 AI 生成摘要（跳过无实质内容的推文）
- 对播客 transcript 生成 200-400 字精华提炼
- 对博客文章生成 100-300 字摘要
- 输出 `content/remixed-articles.json`，包含 3 个数组
- ~200 行代码，复用 filter-ai.js 的 OpenAI 调用模式

### Step 4: 翻译脚本 `scripts/translate-ai.js`
- 从 digest-factory 的 translate-ai.js 改造
- 仅改数组名称：featured/quickNews → builderInsights/podcastHighlights/blogUpdates
- 输出 `content/{en,zh,ja}/{YYYY-MM-DD}.json`

### Step 5: Prompt 模板 `config/prompts/`
- 从 ai-builders-brief/prompts/ 复制并适配为 JSON 输出格式：
  - summarize-tweets.md
  - summarize-podcast.md
  - summarize-blogs.md
  - editorial.md（新建）

### Step 6: 前端组件
- **BuilderCard.svelte**（~80 行）：作者名+角色、AI 标题、摘要、推文链接+互动数据
- **PodcastCard.svelte**（~50 行）：播客名、集标题+YouTube链接、remix 摘要
- **BlogCard.svelte**（~50 行）：博客名、文章标题+链接、作者、摘要

### Step 7: 页面适配
- `+page.svelte`：从 2 区布局改为 3 区（Builder Insights → Podcast Highlights → Blog Updates）
- `about/+page.svelte`：更新管线描述和数据源列表
- RSS 路由：从 featured/quickNews 改为 3 个新数组

### Step 8: GitHub Actions
- daily.yml：每天 UTC 7:00 运行（上游 feed 6:00 生成）
- 流程：collect → remix → translate → build → commit → deploy to GitHub Pages

## 复用 vs 新建

| 复用 (原样) | 改造 | 新建 |
|------------|------|------|
| svelte.config.js | +page.svelte (3区) | collect-feeds.js |
| vite.config.js (主题插件) | translate-ai.js (数组名) | remix-ai.js |
| app.css / app.html | about/+page.svelte | BuilderCard.svelte |
| site-config.js | RSS 路由 | PodcastCard.svelte |
| SubscribeForm.svelte | daily.yml | BlogCard.svelte |
| +layout.svelte / +layout.js | | site.yaml |
| sitemap.xml | | prompt 模板 |

## 主题配色

Indigo (#818cf8) 作为主色调，与 golang (cyan)、ak-blog (orange) 区分。Cyber 风格不变。
