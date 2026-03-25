---
name: word-card
description: "Interactive English word card with D3.js constellation map. Input a word, output an interactive HTML + PNG. Use when user says '/word-card', '词卡', or asks to create a word card."
user_invocable: true
version: "1.0.0"
---

# word-card: 词根星图词卡

单词进去，交互式 HTML + PNG 出来。5 元素内容框架 + D3.js 力导向星图。

## 资源路径

```
SKILL_DIR = <this skill's directory>
TEMPLATE  = SKILL_DIR/assets/word-card-template.html
D3_LOCAL  = SKILL_DIR/assets/d3.v7.min.js
CAPTURE   = SKILL_DIR/assets/capture.js
TONES     = SKILL_DIR/references/tones.md
GUIDE     = SKILL_DIR/references/content-guide.md
EXAMPLE   = SKILL_DIR/references/example-transcribe.json
```

## 执行流程

输入: 一个或多个英文单词
输出: 每个单词一个 HTML（交互式）+ 一个 PNG（截图）

### Step 1: 读取参考文件

读取以下三个文件，加载到工作记忆：
- `TONES` — 8 色调定义
- `GUIDE` — 5 元素内容生成规范
- `EXAMPLE` — Transcribe 示范数据（JSON）

### Step 2: 分析单词 → 产出内容

对每个单词，按 `GUIDE` 规范生成 5 元素内容：

1. **词根拆解**: 追溯拉丁/希腊语源，拆成构件
2. **核心汉字**: 一个字，意象提炼（不是翻译）
3. **画面描写**: 40-60 字具象场景
4. **金句**: 英文 + 中文，非直译，原创
5. **真实例句**: 真实语境，非教科书编造

同时生成 **星图数据**：
- 拆出词根（通常 2 个）
- 每个词根扩展 4 个同族常见词
- 组装成 `constellation_data` JSON（格式见 `GUIDE`）

参考 `EXAMPLE` 中 Transcribe 的数据作为质量基准。

### Step 3: 选择色调

根据 `TONES` 中的触发词匹配色调，得到 6 个 CSS 变量值：
- `BG_COLOR`, `ACCENT_COLOR`, `ACCENT_GLOW`, `MUTED_COLOR`, `TEXT_COLOR`, `TEXT_MUTED`

### Step 4: 填充模板 → 写入 HTML

1. 读取 `TEMPLATE` 文件内容
2. 替换所有模板变量：

| 变量 | 来源 |
|------|------|
| `{{BG_COLOR}}` | Step 3 色调 |
| `{{ACCENT_COLOR}}` | Step 3 色调 |
| `{{ACCENT_GLOW}}` | Step 3 色调 |
| `{{MUTED_COLOR}}` | Step 3 色调 |
| `{{TEXT_COLOR}}` | Step 3 色调 |
| `{{TEXT_MUTED}}` | Step 3 色调 |
| `{{REF_TAG}}` | Step 2 学科标签 |
| `{{WORD}}` | Step 2 带标记的单词 HTML（用 `<span class="prefix">` 和 `<span class="root">`） |
| `{{PHONETIC}}` | Step 2 音标 |
| `{{ZH_MEANING}}` | Step 2 中文释义 |
| `{{ETYMOLOGY_LINE}}` | Step 2 词根拆解行（含 `<span class="op">+</span>`） |
| `{{HANZI}}` | Step 2 核心汉字 |
| `{{SCENE_HTML}}` | Step 2 画面 HTML |
| `{{EXAMPLE_EN}}` | Step 2 英文例句（含 `<em>`） |
| `{{EXAMPLE_ZH}}` | Step 2 中文例句 |
| `{{EPIPHANY_EN}}` | Step 2 英文金句（含 `<span class="hi">`） |
| `{{EPIPHANY_ZH}}` | Step 2 中文金句（含 `<span class="hi">`） |
| `{{D3_PATH}}` | `D3_LOCAL` 的 `file:///` 绝对路径 |
| `{{CONSTELLATION_DATA}}` | Step 2 星图 JSON（直接内联，不要字符串化） |

3. 将结果写入 `/tmp/word_card_{word_lowercase}.html`

4. 用浏览器打开：`open /tmp/word_card_{word_lowercase}.html`

### Step 5: 截图 → PNG

```bash
node CAPTURE /tmp/word_card_{word}.html ~/Downloads/{Word}.png
```

- `{Word}` 首字母大写（如 `Transcribe.png`）
- capture.js 会自动等待 D3 渲染完成后截图
- 需要先确认 playwright 已安装：`cd SKILL_DIR && npm ls playwright`，未安装则 `npm install && npx playwright install chromium`

### Step 6: 报告结果

```
════ 词卡完成 ═══════════════════════
📖 {Word}
   🌐 /tmp/word_card_{word}.html
   🖼️ ~/Downloads/{Word}.png
```

## 多词并行

当输入多个单词时（如 `/word-card Resilience Entropy`）：

1. Step 1 只做一次（读参考文件）
2. Step 2-5 每个单词用一个 **subagent 并行执行**（使用 Task 工具）
3. Step 6 汇总所有结果

每个 subagent 的 prompt 包含：
- 完整的 5 元素规范（从 GUIDE 复制）
- 色调表（从 TONES 复制）
- 示范数据（从 EXAMPLE 复制）
- 模板文件路径
- 该 subagent 负责的单词

## 质量检查

生成内容后，逐项检查：

- [ ] 汉字不是直译，是意象升华
- [ ] 画面有人物、动作、环境，闭眼能「看见」
- [ ] 金句中英非直译，脱离语境仍有力量
- [ ] 例句来自真实语境
- [ ] 星图每族恰好 4 个词，都是常见词
- [ ] `constellation_data` JSON 格式正确，`hub` 在首位
- [ ] 所有模板变量已替换（无残留 `{{`）

## Credits

本 skill 的内容框架和视觉设计受 [李继刚](https://github.com/lijigang) 的 ljg-word / ljg-card / ljg-word-flow 系列 skill 启发。

- **ljg-word**: 单词深度解构方法论（汉字意象、词根拆解、金句）
- **ljg-card**: 信息图铸造系统（HTML → PNG 截图管线）
- **ljg-word-flow**: 解词 + 制卡编排流程

word-card 在此基础上做了以下演进：
- 5 元素内容框架（词根拆解 / 画面 / 金句 / 例句 / 词根家族）
- D3.js 力导向星图（可拖拽、tooltip、粒子动画）
- 响应式交互 HTML（手机适配、clamp() 字号）
- 独立 skill，不依赖 ljg-word/ljg-card
