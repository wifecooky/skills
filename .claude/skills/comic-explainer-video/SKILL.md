---
name: "comic-explainer-video"
description: "Make a 9:16 comic-style Chinese explainer video with voiceover and subtitles: research, script, HTML preview first, choose TTS voice, then render MP4. Phone safe-area layout by default; supports Chinese-English mixed voiceover for English-learning topics and publishing to 小红书/视频号/YouTube via Claude in Chrome."
---

# 漫画风竖屏科普解说视频（comic-explainer-video）

把一个知识点/新闻做成 **9:16 手机竖屏、漫画风、带配音字幕** 的科普解说视频。核心原则：**先交付可拖动的 HTML 预览，用户确认后再渲染 MP4**；配音可选、可换、可用用户自己的录音；生成的配音全部进项目包。

## 工作流

1. **澄清（必要时）**：主题、受众（默认“初等数学/中学水平”）、时长（默认 2–4 分钟）、语言（默认简体中文）。需求清楚就直接做。
2. **调研**：WebSearch/WebFetch 核实事实、数字、日期、人名；记下争议与限制（例如“弱化版 ≠ 原问题”“来源待核实”）；整理 3–6 条来源放片尾。不要夸大结论。
3. **准备工具包**：把本文件末尾「工具包文件」中的 15 个文件原样写入 `<工作目录>/kit/`（base_head.html、base_tail.html、runtime.js、tts.py、build.py、render.py、pack.py、edge_batch.py、gen_edge_mixed.py、render_resume.py、safe_check.py、polyphone_check.py、一键生成Edge配音.command（写入后 chmod +x）、env.example、README.md）。依赖：
   `pip install sherpa-onnx soundfile numpy pillow playwright edge-tts pypinyin --break-system-packages`，需要 ffmpeg 和 Chromium（云端沙箱已预装，勿运行 playwright install）。
4. **写台词** `proj/script.json`（见下方格式与写作规则），**同时写封面** `cover`（见「封面与发布」）。
   **多音字检查（必做）**：`python kit/polyphone_check.py proj` 列出含易错多音字的句子和 pypinyin 猜的读音（猜测也会错，如“教它”应为 jiāo），逐个对照语境；读音不对就给该句加 `say`，把多音字换成同音字（调 tiáo→条、长 zhǎng→掌、行 háng→航、重 chóng→虫、教 jiāo→交 等），字幕 `sub` 不变。用户反馈读错时同样处理，只重配改动的句子。
5. **写画面** `proj/scenes.html`（见组件速查）。每个场景一个 `<div class="scene" id="sN" data-chap="第N话 · 标题">`，动画用 `data-a` 绑定到台词行号，配音换了时间轴会自动对齐。
6. **生成配音 + 预览**：
   默认配音 = **微软 Edge 晓晓 + 云希**（用户认可；Kokoro/浏览器语音机器感强，不作默认，Kokoro 仅在 Edge 不可用时兜底）：
   `python kit/build.py proj --voice "files:proj/edge_voices/zh-CN-XiaoxiaoNeural=晓晓（微软 Edge）" --voice "files:proj/edge_voices/zh-CN-YunxiNeural=云希（微软 Edge）"`（Edge 逐句音频先生成：云端沙箱可直接跑 `timeout 280 python3 kit/edge_batch.py proj zh-CN-XiaoxiaoNeural zh-CN-YunxiNeural --rate 1.1`，tts.py 会自动改用系统证书过代理；超时就分声音多跑几次，已生成的句子会跳过。英语学习类视频有 `"en": true` 的英文句时改用 `python3 kit/gen_edge_mixed.py proj`：中文句晓晓/云希，英文句 Jenny/Guy 母语声音、稍慢语速。）
   兜底：`python kit/build.py proj --voice "kokoro:4@1.25=离线女声（Kokoro）"`。第一条 --voice 为预览默认配音；`--drop <spec>` 去掉某条。
   产出 `proj/build/preview.html`（音轨内嵌，单文件可离线打开）。逐句缓存：改台词后重跑只重配改动的句子。至少要有一个 --voice。2 核约 1.5 秒/句。
7. **自检**：`python kit/render.py proj --sheet` → Read `proj/build/sheet.png`（每场景末帧拼图），检查文字溢出、遮挡、字幕挡画面；需要时 `--at 12.3 45.6` 看中间帧；`--cover` 导出 `build/cover.png` 并 Read 检查封面。**手机安全区检查**：`python kit/safe_check.py proj/build/snap/at_XX.png` 把平台遮挡区画成红/橙色叠加层，Read 检查标题、画面、字幕都不在红区内。可选：用 sherpa-onnx paraformer 中文 ASR（GitHub release 的 sherpa-onnx-paraformer-zh-small-2024-03-09）抽查读音。
8. **先交付预览**：复制 preview.html 和 cover.png（命名 `封面_<标题>.png`）到输出目录并发送，说明可拖动/跳场景/切配音/导出台词和 SRT、页内「● 录制视频」（Chrome/Edge 选“此标签页”共享，实时录下竖屏区域并自动下载 MP4/WebM）与「高清渲染」按钮（复制一句话给 Claude），以及可导入或逐句录制自己的配音（见下方「用户自己的配音」）；请用户确认或提修改。按反馈改 → 重跑 6、7。
9. **确认后渲染（用户选定配音后主动做，不要等用户找按钮）**：`python kit/render.py proj --voice <id|spec|名称>` → `proj/build/<id>.mp4`（1080×1920，30fps，H.264+AAC，自动把 cover.png 写入文件缩略图）。可 `--start/--end` 先渲一段。2 核约 1 分钟渲染 15 秒视频。**单核或单条命令有时限（如 300 秒）时 render.py 会被杀掉**：先 `render.py proj --cover`，再反复运行 `timeout 290 python3 kit/render_resume.py proj --voice <名称> --budget 250 --upload` 直到打印 DONE（断点续截帧，约 8 帧/秒；帧齐后自动合成 MP4、写入封面缩略图；`--upload` 另出 ≤9.5MB 的 `<id>_upload.mp4`）。
10. **交付项目包（必须含生成的配音）**：`python kit/pack.py proj --out <输出目录>/<标题>_项目包.zip [--mp4 proj/build/<id>.mp4]`。包内含 kit、README、一键生成Edge配音.command、script.json、scenes.html、preview.html、时间轴，以及 **配音/<声音名>/**：完整配音_含音乐.mp3、纯人声.mp3、字幕.srt、逐句/NN_台词.mp3，另有 配音/台词.txt；逐句 mp3 同时充当 build 缓存（解压后重跑 build 不会重新合成）。检查 zip < 30MB（超了就不带 --mp4，视频单独发送）。

## script.json 格式
```json
{"title":"视频标题","badge":"数学漫画","footer":"本片为科普解说 · 细节已简化","watermark":"@频道名",
 "sources":"资料：……（可含 <sup>）",
 "cover":{"title":"其实只会<br>“猜下一个字”","kicker":"你每天用的 ChatGPT","sub":"3 分钟看懂大语言模型","badge":"AI 漫画科普","art":"<div class=\"abs\" …>角色/气泡</div>","dur":1.6},
 "timing":{"pre":0.8,"gap":0.28,"scene_gap":0.7,"tail":3.0},
 "music":{"on":true,"volume":0.10},
 "sfx":[{"type":"shot","line":3,"at":-0.25},{"type":"ding","line":39,"at":"end-0.3"}],
 "lines":[{"scene":"s1","sub":"字幕文字，关键词用“引号”会标红","say":"可选：给 TTS 的念法"}]}
```
英语学习类视频：英文例句一行一句，加 `"en": true`（gen_edge_mixed.py 用英语母语声音读），字幕只放英文、下一句给中文翻译；连读演示用 `"sub":"good at → goo-dat","say":"good at. good at.","en":true`。引用原视频/采访时只取词汇和表达，例句自己写，不逐字搬运原台词。
`watermark`（可选，频道名如 `"@双言两语"`，留空不显示）：顶部留白一处、底部留白一处大号淡水印，外加画面内一枚小水印，每换一个场景在左下/右下角之间换位置，防止被裁掉。首次做视频时问一次频道名，之后沿用。
sfx 类型：shot（狙击枪声）、ding（完成音）、pop、whoosh；`line` 为 0 起的行号，`at` 为相对该句开始的秒数，或 `"end±x"`。

**写作规则**：每句字幕 ≤ 28 字（手机两行内）；一句一个意思；用生活类比（贴牌、原子、门的宽窄）替代术语，术语第一次出现时点名并解释；数字写法给 `say`（如 `"4×10¹⁸"` → `"4乘10的18次方"`，`"1＋2"` → `"1加2"`）；英文专名直接写（kokoro 能读 GPT、Astra、AI），melo 引擎读不好时用 `say` 改写；开头 3 句内给悬念，结尾留问题；必须有“冷静一下/局限”场景；整片 50–60 句 ≈ 3.5 分钟。

## 封面与发布
- **封面必做**：分发平台需要封面；页内「录制视频」录出的文件浏览器无法写入缩略图，所以封面做成片头卡：`cover` 存在时视频前 `dur` 秒（默认 1.6）显示全屏封面（黄底放射线 + 白框大标题），正片第一句自动顺延，第一帧即封面。
- 字段：`badge` 左上角标、`kicker` 标题上方一行、`title` 主标题（`<br>` 换行，“引号”内标红，≤ 12 字两行最醒目）、`sub` 黑底副标题、`art` 下方插画区（舞台坐标 top 520 起、约 260 高，可用 `#kid` 等 symbol、`.bubble`、`.sfx`；右边缘留 40px 余量）。顶部 0–90、底部 780 以下会被平台界面遮挡，别放关键信息。
- 标题写法：反差悬念（“其实只会…”）＞ 数字承诺（“3 分钟看懂…”）＞ 痛点提问；与片中第一句呼应。用户要分发时，顺带给 3–4 组标题（悬念 / 干货 / 痛点 / 封面短标题）、一段可直接粘贴的简介（结尾抛问题引评论）和 5–8 个话题标签。
- 交付：`render.py --cover` 生成的 `cover.png` 单独交付，提醒用户在平台「上传封面」里使用。

## 发布到小红书 / 视频号 / YouTube（Claude in Chrome）
- 文案：每个平台单独写标题、简介、话题（小红书标题 ≤20 字；视频号短标题要短，约 6–16 字，长标题放简介首行；YouTube 时长 <3 分钟可发 Shorts，标题加 `#Shorts`）。用户说“你来定”就各给一个，不再列选项。
- 浏览器：先 `tabs_context_mcp` 确认扩展已连接；连不上就给安装链接 https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn 并请用户在侧边栏用同一账号登录。
- **登录由用户完成**（视频号助手微信扫码 / 快捷登录、小红书、YouTube），Claude 不输密码、不扫码、不过验证码。
- **上传文件由用户完成**：视频号助手发表页 `https://channels.weixin.qq.com/platform/post/create` 的表单在独立组件里，find/read_page 找不到文件框，file_upload 用不了；file_upload 单次也只能传 ≤10MB。所以让用户把视频（用高清版即可）和封面（「封面预览」→上传）拖进去，Claude 再接手。
- 视频号由 Claude 按截图坐标点击并输入：视频描述（简介 + `#话题 ` 空格结尾会变成话题）→ 短标题 → 位置选「不显示位置」→ 合集 → 视频标注选「含AI生成内容」（AI 配音/AI 生成画面时，按国内 AI 生成内容标识要求标注）→ 声明原创。描述框输入后会变高，下面的字段会下移，**每步后重新截图再点**。
- **必须停下来问用户的点**：声明原创弹窗要勾选同意《原创声明须知》《使用条款》（代用户同意条款，需用户明确说同意）；最后的「发表」按钮（用户明确说“发表”才点；不同平台分别确认）。合集、活动、链接等用户偏好项先问。
- 视频号发表后不能替换视频，只能删除重发（播放数据清零）——所以发布前先用 safe_check 和手机预览确认版式。发表后截图视频管理列表确认状态（如「原创审核中」）。

## 画面组件速查（舞台 540×960，渲染时 ×2）
- **手机安全区版式（默认，已内置于 base_head/base_tail）**：手机竖屏播放时，iPhone 等长屏会把 9:16 放大铺满（左右各裁约 25px），顶部被状态栏和返回/更多按钮盖住（0–86），底部被合集、作者提示、简介和按钮盖住（约 780 以下），小红书/YouTube Shorts 右侧还有点赞评论按钮（x>465、y 470–780）。所以：
  - 0–88 只放顶部水印（watermark）；顶栏 88–144（自动显示 data-chap）；进度条 144。
  - **场景区**：所有 `.scene` 自动包在 `#safe` 里，场景内坐标仍是 **0–540 × 0–585**，整体缩放 0.74 显示在 x 70–470、y 156–589。照旧按 540×585 写画面，但字号要比满屏时略大（正文 ≥22px、标题 ≥30px），否则手机上偏小。
  - 字幕框 604–736（左右各留 56px，自动）；**章节条** 744–776（自动：由各场景 data-chap「·」后的短标题生成胶囊，当前章节黄色高亮并居中，已播章节变暗，所以 data-chap 短标题控制在 8 字内）；页脚 782–960 只放一行小字和底部水印，**片尾资料来源在手机上会被遮挡**，同时要写进发布简介。
  - 改版式只改 base_head.html 的 CSS（#top/#prog/#safe/#subwrap/#chapbar/#foot/#cover），不要在 scenes.html 里再包一层 #safe。
- 类：`.panel`（白底粗黑框+投影，加 `.yel/.red/.blue`）、`.abs`、`.hd`（粗体）、`.num`、`.sfx`（黄字黑描边拟声词，如 砰！）、`.stampbox`（红色印章框）、`.bubble`（对话气泡）、`.tag`（黑底白字标签）、`.card`（112×150 卡片）、`.chip`（行内小色块）、`.speed`（放射速度线背景）、`.ok`（绿色）。
- SVG 符号 `<svg width=W height=H><use href="#id"/></svg>`：`astra`（机器人，200×250 比例，胸口 GPT-6/ASTRA，可改）、`kid`（小孩旁白 160×210）、`wig`（18 世纪假发学者 170×230，用 `style="--coat:#2f6fdb"` 换外套色）、`rifle`（300×70）、`target`（靶）、`cross`（准星）、`burst`（爆炸框）。需要新角色/道具时在 scenes.html 顶部自行加 `<svg><defs><symbol>`，保持粗黑描边+平涂；只画原创角色，不画已知 IP 角色。
- 动画：`data-a="名称@行号±秒 名称@行号±秒"`，行号 0 起；`@s` 表示场景开始。第一个动画决定出场前隐藏状态。名称：pop fade fadeout up down left right stamp stamp0 shake bob spin40 pulse2 flash flip count aim zoomin twinkle hl dim grow draw。叠加 transform 冲突时用外层 div 包一层（如入场 left + 内层 bob）。
- 示例（第 3–4 句出现靶子、第 4 句“砰”）：
```html
<div class="scene" id="s1" data-chap="序章 · AI 扛起狙击枪">
 <div class="speed" data-a="spin40@s"></div>
 <div class="abs" style="left:318px;top:160px;width:190px;height:190px" data-a="pop@2 shake@3+0.1"><svg width="190" height="190"><use href="#target"/></svg></div>
 <div class="abs" style="left:10px;top:285px;width:176px;height:220px" data-a="left@0+0.4"><div data-a="bob@s" style="width:100%;height:100%"><svg width="176" height="220"><use href="#astra"/></svg></div></div>
 <div class="panel yel hd" style="left:292px;top:362px;padding:6px 12px;font-size:27px" data-a="up@2+0.6">哥德巴赫猜想</div>
 <div class="sfx" style="left:330px;top:200px;font-size:58px;color:#ff4757" data-a="pop@3-0.2 fadeout@4">砰！</div>
</div>
```
- 场景内可放 `<script>` 生成重复元素（写 data-a 即可，在 runtime 初始化前执行）。
- 坑：不要用 emoji（渲染字体缺失）；上标用 `<sup>`；长文本给定宽度避免溢出；元素别超出 585 高度；每场景 3–6 个元素逐句出现，不要一次堆满。

## 配音引擎（build.py --voice 的写法；`@1.2`=语速，`=名字`=预览下拉里的显示名）
- `kokoro:<sid>` 离线兜底（云端可用，Edge 不可用时用；模型自动从 GitHub release 下载约 350MB）。4=女声，60=男声；3–57 中文女声，58+ 多为男声。默认语速偏慢，用 @1.2–1.25。
- `melo` 离线，较机械；`say:Tingting` macOS；`openai:alloy` 需 OPENAI_API_KEY；`files:<目录>` 用户自己的录音或外部生成的逐句音频 01.mp3、02.wav…（`files`/`edge`/`minimax`/`listenhub` 都会自动裁掉首尾静音）
- `edge:zh-CN-XiaoxiaoNeural`（[edge-tts](https://github.com/rany2/edge-tts)，微软神经网络语音，免费、质量最好）：常用 Xiaoxiao 晓晓、Yunxi 云希、Yunjian 云健、Xiaoyi 晓伊、Yunyang 云扬；可带音调/音量 `edge:zh-CN-YunxiNeural|+5Hz|+10%@1.1`；`python kit/tts.py --list-edge zh-CN` 列出声音。云端沙箱已验证可用（代理做 HTTPS 中间人，tts.py 在设置了 SSL_CERT_FILE 时自动让 edge-tts 用系统证书）；仍失败时见下方「微软 Edge 配音」。
- `minimax:<voice_id>`（MiniMax T2A v2，默认 speech-2.8-hd，可带情绪 `minimax:presenter_female|happy`；国内账号 `MINIMAX_API_HOST=https://api.minimaxi.com`；`--list-minimax`）、`listenhub:<speakerId>`（ListenHub 同步 TTS）、`flowspeech:<speakerId>`（ListenHub FlowSpeech，异步 direct 模式，build 时所有待合成句并行提交再轮询；<10 字的句子自动改走同步 TTS 同音色；`--list-listenhub zh`）。Key 放项目根目录 `.env`（模板 env.example；也读环境变量、kit/../.env、proj/.env、~/.config/comic-video/keys.env），**不要让用户把 Key 贴进聊天**；需在 Cowork 网络设置放行 api.minimax.io / api.minimaxi.com / api.marswave.ai（FlowSpeech 音频下载域名首次被拦时再告知用户放行）。
- 预览页已去掉浏览器/系统语音（用户嫌机器感强）；只保留已生成的配音、“我的配音”和静音。

## 微软 Edge 配音
- **首选：云端沙箱直接生成**（见工作流第 6 步；`speech.platform.bing.com` 需在网络白名单内）。
- **其次：Claude 在用户电脑的 Cowork 本地环境里生成**（需会话已连接用户文件夹、用户已在 Cowork 网络设置放行 `speech.platform.bing.com`）。tts.py 会自动把 HTTPS_PROXY 传给 edge-tts（aiohttp 默认不读代理变量，不传会 DNS 失败）。用 device_bash 在项目文件夹里**前台**逐个声音运行 `timeout 170 python3 kit/edge_batch.py proj zh-CN-XiaoxiaoNeural --rate 1.1`（nohup 后台进程会在调用结束时被杀；本地 VM 缺 edge-tts 就 `pip3 install --user edge-tts`），再在 device_bash 里把 `proj/edge_voices` 打成 zip 放到项目内隐藏目录，用 `device_stage_files` 拉到云端解压，然后按工作流第 6 步 build。
- 连接不了或域名未放行：让用户双击项目根目录 **`一键生成Edge配音.command`**（macOS；自动建 venv 装 edge-tts，交互选声音/语速），或 `pip install edge-tts` 后 `python kit/edge_batch.py proj zh-CN-XiaoxiaoNeural zh-CN-YunxiNeural --rate 1.1`；完成后同样拉回云端 build。
- 往用户文件夹写项目包：`device_commit_files` 单文件上限 20MB，超了先 `split -b 15M` 分片提交，再在 device_bash 里 `cat` 合并、python zipfile 解压（覆盖更新）、`chmod +x *.command`；device_bash 默认不能删除文件，临时分片放隐藏目录并告诉用户可删。聊天附件上限 30MB，超了只放文件夹。

## 用户自己的配音（预览页内置功能，交付时要告诉用户）
- **导入逐句文件**：“导入我的配音…”多选 `01.mp3、02.m4a…`（编号=台词序号，从 01 起，见“导出台词”），或选本页导出的 zip。自动裁掉首尾静音，时间轴按每句实际长度重排，画面自动对齐。
- **网页逐句录音**：“逐句录音”面板＝提词器：● 录制 / ■ 停止，自动下一句，可试听、重录（需 Chrome/Edge 打开下载后的 HTML 并允许麦克风）。
- **整段录音**：只选一个文件名不以数字开头的文件 → 按整段处理，沿用第一条内置配音的时间轴，“偏移”滑块对齐。
- **出视频**：逐句方式“导出我的配音 ZIP”→ 解压到 `proj/my_voice/` → `python kit/build.py proj --voice "files:proj/my_voice=我的配音"` → `python kit/render.py proj --voice 我的配音`；整段方式 `python kit/render.py proj --voice <内置id> --audio 录音.m4a --offset 秒`。
- 用户把录音或导出的 zip 发回来时，由你执行上述命令并交付视频和新项目包。注意：无头 Chromium 不支持 AAC/m4a 解码，测试导入时用 mp3/wav。

## 工具包文件（原样写入 kit/）

### kit/base_head.html
````html
<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{TITLE}}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{margin:0;background:#1d1d22}
#stage{width:540px;height:960px;overflow:hidden;position:relative;background:#fff8e6;font-family:"Noto Sans CJK SC","Noto Sans CJK JP","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;color:#141414;transform-origin:0 0}
#bg{position:absolute;inset:0;background:
  radial-gradient(circle,rgba(20,20,20,.09) 1.3px,transparent 1.8px) 0 0/11px 11px,#fff4d6}
#top{position:absolute;left:0;right:0;top:88px;height:56px;background:#141414;color:#fff;display:flex;align-items:center;padding:0 18px;gap:10px;z-index:20}
#top .pill{background:#ffd23f;color:#141414;font-weight:900;font-size:15px;padding:4px 10px;border-radius:6px;transform:rotate(-3deg)}
#chap{font-weight:900;font-size:21px;letter-spacing:1px}
#prog{position:absolute;left:0;top:144px;height:6px;background:#ff4757;z-index:21}
#progbg{position:absolute;left:0;right:0;top:144px;height:6px;background:#3a3a3a;z-index:20}
#safe{position:absolute;left:70px;top:156px;width:540px;height:585px;transform:scale(.74);transform-origin:0 0;z-index:5}
.scene{position:absolute;left:0;top:0;width:540px;height:585px;display:none;overflow:hidden;animation:sceneIn .45s cubic-bezier(.2,.9,.3,1.2) both}
@keyframes sceneIn{0%{clip-path:polygon(0 0,0 0,0 100%,0 100%);transform:scale(1.04)}100%{clip-path:polygon(0 0,100% 0,100% 100%,0 100%);transform:none}}
#subwrap{position:absolute;left:56px;right:56px;top:604px;height:132px;display:flex;align-items:flex-start;justify-content:center;z-index:15}
#sub{background:#ffd23f;border:4px solid #141414;box-shadow:6px 6px 0 #141414;padding:10px 14px;font-size:23px;font-weight:900;line-height:1.38;text-align:center;border-radius:4px;max-width:100%;transform-origin:50% 0}
#sub em{font-style:normal;color:#e8233a}
#chapbar{position:absolute;left:25px;right:25px;top:744px;height:32px;overflow:hidden;z-index:16}
#chapstrip{position:absolute;left:0;top:2px;display:flex;gap:6px;white-space:nowrap}
#chapstrip .cb{font-size:14px;font-weight:900;line-height:1;padding:6px 11px;border-radius:14px;border:2px solid #141414;background:#fff;color:#141414}
#chapstrip .cb.done{background:#141414;color:#fff;opacity:.45}
#chapstrip .cb.on{background:#ffd23f;box-shadow:2px 2px 0 #141414}
/* 水印（script.json "watermark"，留空则不显示）：顶部/底部留白各一处 + 画面内小水印（每换一个场景换一个角，防裁切） */
.wmk:empty{display:none}
#wmtop{position:absolute;left:0;right:0;top:34px;text-align:center;font-weight:900;font-size:22px;letter-spacing:2px;color:rgba(20,20,20,.38);z-index:3}
#wmbot{position:absolute;left:0;right:0;top:838px;text-align:center;font-weight:900;font-size:46px;letter-spacing:3px;color:rgba(20,20,20,.13);transform:rotate(-4deg);z-index:22}
#wm{position:absolute;font-weight:900;font-size:15px;color:rgba(20,20,20,.30);z-index:17;pointer-events:none}
#wm.c2{right:84px;top:574px}#wm.c3{left:84px;top:574px}
#foot{position:absolute;left:0;right:0;bottom:0;height:178px;background:
  repeating-linear-gradient(-45deg,rgba(20,20,20,.06) 0 8px,transparent 8px 16px);border-top:4px solid #141414}
#foot .tip{position:absolute;left:0;right:0;text-align:center;top:8px;font-size:13px;font-weight:700;color:#555}
.abs{position:absolute}
.panel{position:absolute;background:#fff;border:5px solid #141414;box-shadow:7px 7px 0 #141414}
.hd{font-weight:900}
.sfx{position:absolute;font-weight:900;font-style:italic;color:#ffd23f;-webkit-text-stroke:3px #141414;paint-order:stroke fill;text-shadow:5px 5px 0 #141414;letter-spacing:2px}
.stampbox{position:absolute;border:5px solid #e8233a;color:#e8233a;font-weight:900;padding:4px 12px;border-radius:8px;background:rgba(255,255,255,.85)}
.bubble{position:absolute;background:#fff;border:4px solid #141414;border-radius:26px;padding:10px 16px;font-weight:900;font-size:22px;box-shadow:4px 4px 0 #141414}
.tag{position:absolute;background:#141414;color:#fff;font-weight:900;padding:4px 12px;font-size:18px;border-radius:4px}
.big{font-size:44px}
.num{font-family:"Noto Sans CJK SC",sans-serif;font-weight:900}
.card{position:absolute;width:112px;height:150px;border:4px solid #141414;border-radius:12px;background:#fff;box-shadow:4px 4px 0 #141414;text-align:center}
.red{background:#ff4d5e!important;color:#fff}
.blue{background:#3a86ff!important;color:#fff}
.yel{background:#ffd23f}
.ok{color:#18a558}
.speed{position:absolute;left:50%;top:50%;width:1400px;height:1400px;margin:-700px 0 0 -700px;background:repeating-conic-gradient(rgba(20,20,20,.10) 0 3deg,transparent 3deg 9deg)}
svg{overflow:visible}

/* keyframes */
@keyframes pop{0%{opacity:0;transform:scale(.2) rotate(-8deg)}70%{opacity:1;transform:scale(1.12) rotate(2deg)}100%{opacity:1;transform:none}}
@keyframes fade{0%{opacity:0}100%{opacity:1}}
@keyframes fadeout{0%{opacity:1}100%{opacity:0}}
@keyframes up{0%{opacity:0;transform:translateY(60px)}100%{opacity:1;transform:none}}
@keyframes down{0%{opacity:0;transform:translateY(-80px)}100%{opacity:1;transform:none}}
@keyframes left{0%{opacity:0;transform:translateX(-340px)}100%{opacity:1;transform:none}}
@keyframes right{0%{opacity:0;transform:translateX(340px)}100%{opacity:1;transform:none}}
@keyframes stamp{0%{opacity:0;transform:scale(3.2) rotate(-14deg)}60%{opacity:1;transform:scale(.92) rotate(-6deg)}100%{opacity:1;transform:rotate(-6deg)}}
@keyframes shake{0%,100%{transform:none}20%{transform:translate(-8px,4px) rotate(-2deg)}40%{transform:translate(7px,-5px) rotate(2deg)}60%{transform:translate(-6px,3px)}80%{transform:translate(5px,-2px)}}
@keyframes bob{0%{transform:translateY(0)}100%{transform:translateY(-8px)}}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
@keyframes pulse{0%{transform:scale(1)}100%{transform:scale(1.08)}}
@keyframes flash{0%{opacity:0}15%{opacity:1}100%{opacity:0}}
@keyframes flip{0%{transform:rotateY(90deg);opacity:0}100%{transform:none;opacity:1}}
@keyframes grow{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
@keyframes zoomin{0%{opacity:0;transform:scale(2.4)}100%{opacity:1;transform:none}}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}
@keyframes aim{0%{transform:translate(-120px,60px) scale(1.5);opacity:0}60%{opacity:1}100%{transform:none;opacity:1}}
@keyframes draw{0%{stroke-dashoffset:var(--len,600)}100%{stroke-dashoffset:0}}
@keyframes dim{0%{opacity:1}100%{opacity:.25}}
@keyframes hl{0%{background:#fff;color:#141414}100%{background:#ffd23f;color:#141414;transform:scale(1.08)}}
@keyframes twinkle{0%{opacity:.3}100%{opacity:1}}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-300px)}}
@keyframes count{0%{transform:translateY(0)}100%{transform:translateY(-560px)}}
.chip{display:inline-block;border:3px solid #141414;border-radius:6px;padding:0 8px;font-size:20px;line-height:32px}
@keyframes stamp0{0%{opacity:0;transform:scale(3)}60%{opacity:1;transform:scale(.92)}100%{opacity:1;transform:none}}
.eye{transform-box:fill-box;transform-origin:center;animation:blink 3.2s linear infinite}
#cover{position:absolute;inset:0;z-index:40;background:#ffd23f;overflow:hidden;display:none}
#cover .cv-rays{position:absolute;left:50%;top:44%;width:1600px;height:1600px;margin:-800px 0 0 -800px;background:repeating-conic-gradient(rgba(20,20,20,.09) 0 4deg,transparent 4deg 12deg)}
#cover .cv-dots{position:absolute;inset:0;background:radial-gradient(circle,rgba(20,20,20,.10) 1.4px,transparent 1.9px) 0 0/12px 12px}
#cover .cv-badge{position:absolute;left:28px;top:100px;background:#141414;color:#ffd23f;font-weight:900;font-size:22px;padding:6px 14px;border-radius:6px;transform:rotate(-3deg)}
#cover .cv-kicker{position:absolute;left:0;right:0;top:170px;text-align:center;font-weight:900;font-size:30px;color:#141414}
#cover .cv-title{position:absolute;left:24px;right:24px;top:220px;background:#fff;border:6px solid #141414;box-shadow:10px 10px 0 #141414;padding:22px 18px;text-align:center;font-weight:900;font-size:58px;line-height:1.22;color:#141414;transform:rotate(-1.5deg)}
#cover .cv-title em{font-style:normal;color:#e8233a}
#cover .cv-sub{position:absolute;left:0;right:0;top:470px;text-align:center}
#cover .cv-sub span{display:inline-block;background:#141414;color:#fff;font-weight:900;font-size:30px;padding:8px 18px;border-radius:6px}
#cover .cv-art{position:absolute;left:0;right:0;top:520px;height:260px}
{{EXTRA_CSS}}
</style></head><body>
<div id="stage">
<svg width="0" height="0" style="position:absolute">
<defs>
 <symbol id="astra" viewBox="0 0 200 250">
  <line x1="100" y1="42" x2="100" y2="14" stroke="#141414" stroke-width="5"/>
  <polygon points="100,0 105,10 116,11 108,18 110,29 100,23 90,29 92,18 84,11 95,10" fill="#ffd23f" stroke="#141414" stroke-width="3"/>
  <rect x="36" y="40" width="128" height="96" rx="30" fill="#fff" stroke="#141414" stroke-width="5"/>
  <rect x="26" y="72" width="14" height="32" rx="6" fill="#ffd23f" stroke="#141414" stroke-width="4"/>
  <rect x="160" y="72" width="14" height="32" rx="6" fill="#ffd23f" stroke="#141414" stroke-width="4"/>
  <rect x="52" y="60" width="96" height="52" rx="20" fill="#1c2b4d" stroke="#141414" stroke-width="4"/>
  <ellipse class="eye" cx="80" cy="86" rx="10" ry="12" fill="#5ef2ff"/>
  <ellipse class="eye" cx="120" cy="86" rx="10" ry="12" fill="#5ef2ff"/>
  <circle cx="76" cy="81" r="3" fill="#fff"/><circle cx="116" cy="81" r="3" fill="#fff"/>
  <path d="M86 124 Q100 132 114 124" stroke="#141414" stroke-width="4" fill="none" stroke-linecap="round"/>
  <rect x="58" y="138" width="84" height="74" rx="20" fill="#ffd23f" stroke="#141414" stroke-width="5"/>
  <text x="100" y="170" text-anchor="middle" font-size="20" font-weight="900" fill="#141414">GPT-6</text>
  <text x="100" y="196" text-anchor="middle" font-size="16" font-weight="900" fill="#e8233a">ASTRA</text>
  <rect x="68" y="210" width="22" height="34" rx="8" fill="#fff" stroke="#141414" stroke-width="5"/>
  <rect x="110" y="210" width="22" height="34" rx="8" fill="#fff" stroke="#141414" stroke-width="5"/>
 </symbol>
 <symbol id="rifle" viewBox="0 0 300 70">
  <rect x="60" y="30" width="230" height="12" rx="3" fill="#3b3f4a" stroke="#141414" stroke-width="4"/>
  <rect x="284" y="26" width="16" height="20" rx="3" fill="#141414"/>
  <path d="M0 28 L70 26 L90 36 L90 52 L60 52 L20 64 L0 60 Z" fill="#8a5a33" stroke="#141414" stroke-width="4" stroke-linejoin="round"/>
  <rect x="100" y="6" width="120" height="20" rx="8" fill="#20242c" stroke="#141414" stroke-width="4"/>
  <circle cx="222" cy="16" r="11" fill="#5ef2ff" stroke="#141414" stroke-width="4"/>
  <rect x="140" y="24" width="10" height="10" fill="#20242c" stroke="#141414" stroke-width="3"/>
  <path d="M120 42 L130 60 L140 60 L136 42" fill="#3b3f4a" stroke="#141414" stroke-width="4"/>
 </symbol>
 <symbol id="kid" viewBox="0 0 160 210">
  <rect x="40" y="130" width="80" height="80" rx="24" fill="#3a86ff" stroke="#141414" stroke-width="5"/>
  <path d="M40 160 H120" stroke="#fff" stroke-width="8"/>
  <circle cx="80" cy="82" r="56" fill="#ffe1bf" stroke="#141414" stroke-width="5"/>
  <path d="M26 72 Q30 22 80 22 Q132 22 136 72 Q118 50 98 54 Q84 40 64 54 Q44 48 26 72 Z" fill="#2b2b2b" stroke="#141414" stroke-width="4"/>
  <path d="M86 26 Q86 4 104 4 Q120 4 118 18 Q116 28 104 30" fill="none" stroke="#2b2b2b" stroke-width="7" stroke-linecap="round"/>
  <ellipse class="eye" cx="60" cy="86" rx="9" ry="12" fill="#141414"/><ellipse class="eye" cx="100" cy="86" rx="9" ry="12" fill="#141414"/>
  <circle cx="57" cy="81" r="3" fill="#fff"/><circle cx="97" cy="81" r="3" fill="#fff"/>
  <circle cx="44" cy="106" r="8" fill="#ffb3b3"/><circle cx="116" cy="106" r="8" fill="#ffb3b3"/>
  <ellipse cx="80" cy="114" rx="10" ry="12" fill="#8b1c1c" stroke="#141414" stroke-width="3"/>
 </symbol>
 <symbol id="wig" viewBox="0 0 170 230">
  <path d="M40 150 Q85 130 130 150 L145 228 H25 Z" fill="var(--coat,#7b4bb3)" stroke="#141414" stroke-width="5" stroke-linejoin="round"/>
  <path d="M72 150 L85 180 L98 150" fill="#fff" stroke="#141414" stroke-width="4"/>
  <circle cx="30" cy="80" r="22" fill="#f4f4f4" stroke="#141414" stroke-width="4"/><circle cx="28" cy="112" r="22" fill="#f4f4f4" stroke="#141414" stroke-width="4"/>
  <circle cx="140" cy="80" r="22" fill="#f4f4f4" stroke="#141414" stroke-width="4"/><circle cx="142" cy="112" r="22" fill="#f4f4f4" stroke="#141414" stroke-width="4"/>
  <ellipse cx="85" cy="90" rx="46" ry="54" fill="#ffe1bf" stroke="#141414" stroke-width="5"/>
  <path d="M38 70 Q40 22 85 22 Q130 22 132 70 Q110 46 85 50 Q60 46 38 70Z" fill="#f4f4f4" stroke="#141414" stroke-width="4"/>
  <circle cx="68" cy="90" r="5" fill="#141414"/><circle cx="102" cy="90" r="5" fill="#141414"/>
  <path d="M60 78 L76 80 M94 80 L110 78" stroke="#141414" stroke-width="4" stroke-linecap="round"/>
  <path d="M85 94 Q80 108 88 110" stroke="#141414" stroke-width="3" fill="none"/>
  <path d="M72 122 Q85 130 98 122" stroke="#141414" stroke-width="4" fill="none" stroke-linecap="round"/>
 </symbol>
 <symbol id="burst" viewBox="0 0 200 200">
  <polygon points="100,0 118,62 176,24 140,80 200,100 140,120 176,176 118,138 100,200 82,138 24,176 60,120 0,100 60,80 24,24 82,62" fill="#ffd23f" stroke="#141414" stroke-width="6" stroke-linejoin="round"/>
 </symbol>
 <symbol id="target" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="96" fill="#fff" stroke="#141414" stroke-width="6"/>
  <circle cx="100" cy="100" r="74" fill="#e8233a" stroke="#141414" stroke-width="4"/>
  <circle cx="100" cy="100" r="52" fill="#fff" stroke="#141414" stroke-width="4"/>
  <circle cx="100" cy="100" r="30" fill="#e8233a" stroke="#141414" stroke-width="4"/>
 </symbol>
 <symbol id="cross" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="84" fill="none" stroke="#141414" stroke-width="7"/>
  <circle cx="100" cy="100" r="84" fill="none" stroke="#5ef2ff" stroke-width="3"/>
  <path d="M100 4 V70 M100 130 V196 M4 100 H70 M130 100 H196" stroke="#141414" stroke-width="7"/>
  <circle cx="100" cy="100" r="6" fill="#e8233a"/>
 </symbol>
</defs></svg>
<div id="bg"></div>
<div id="top"><span class="pill">{{BADGE}}</span><span id="chap"></span></div>
<div id="progbg"></div><div id="prog"></div>
<div id="safe">
````

### kit/base_tail.html
````html
</div><!-- /safe -->
<div id="wmtop" class="wmk">{{WATERMARK}}</div><div id="wm" class="wmk c2">{{WATERMARK}}</div>
<div id="chapbar"><div id="chapstrip"></div></div>
<div id="subwrap"><div id="sub"></div></div>
<div id="foot"><div class="tip">{{FOOTER}}</div>
 <div id="src" class="abs" style="left:20px;right:20px;top:40px;font-size:12.5px;line-height:1.55;color:#444;display:none">{{SOURCES}}</div></div>
<div id="wmbot" class="wmk">{{WATERMARK}}</div>
{{COVER}}
</div><!-- /stage -->
````

### kit/runtime.js
````js
/* comic-video runtime: timeline-driven animation + preview player.
   window.PROJECT = {title, lines:[{scene,sub,say}], sources, tracks:[{id,name,audio,timeline:{total,lines:[{start,end}],scenes:[{id,start,end}]}}]}
   URL params: ?render=1&voice=<trackId>  -> bare 540x960 stage, window.seek(t) for frame capture */
(function(){
const P = window.PROJECT, Q = new URLSearchParams(location.search), RENDER = Q.get('render')==='1';
const DEF = {
 pop:[.5,'cubic-bezier(.3,1.5,.5,1)'], fade:[.5,'ease'], fadeout:[.4,'ease',0,'forwards'],
 up:[.55,'cubic-bezier(.2,1.2,.4,1)'], down:[.55,'cubic-bezier(.2,1.2,.4,1)'], left:[.6,'cubic-bezier(.2,1.1,.4,1)'], right:[.6,'cubic-bezier(.2,1.1,.4,1)'],
 stamp:[.45,'ease-out'], stamp0:[.45,'ease-out'], shake:[.5,'linear',0,'none'], bob:[1.1,'ease-in-out',1],
 spin40:[40,'linear',1], pulse2:[.6,'ease-in-out',1,'none'], flash:[.6,'ease-out'], flip:[.5,'cubic-bezier(.3,1.4,.5,1)'],
 count:[3.2,'cubic-bezier(.5,0,.7,1)',0,'forwards'], aim:[1.0,'cubic-bezier(.2,.8,.3,1)'], zoomin:[.5,'cubic-bezier(.2,1.3,.4,1)'],
 twinkle:[1.4,'ease-in-out',1], hl:[.35,'ease-out',0,'forwards'], dim:[.4,'ease',0,'forwards'], grow:[.6,'ease-out'], draw:[1.2,'ease-in-out']
};
window.COMIC_DEF = DEF;
const $ = id => document.getElementById(id);
const stage=$('stage'), subEl=$('sub'), subW=$('subwrap'), chap=$('chap'), prog=$('prog'), src=$('src');
const cover=$('cover'), COVER=+(P.cover||0);
const lines = P.lines;

/* ---------- estimated timeline (no audio) ---------- */
function estimate(){ const tm=P.timing||{pre:.8,gap:.28,scene_gap:.7,tail:3};
  let t=tm.pre, prev=null; const L=[], S=[];
  lines.forEach(o=>{ if(prev&&o.scene!==prev) t+=tm.scene_gap;
    if(o.scene!==prev) S.push({id:o.scene,start:prev?t-tm.scene_gap/2:0});
    const d=Math.max(1.2,(o.say||o.sub).replace(/[，。！？、：；…“”—\s]/g,'').length*0.24);
    L.push({start:t,end:t+d}); t+=d+tm.gap; prev=o.scene; });
  const total=t+tm.tail; S.forEach((s,i)=>s.end=i+1<S.length?S[i+1].start:total);
  return {total,lines:L,scenes:S}; }

let TL=null, S={}, lastScene=null, lastSub=-1;
function applyTimeline(tl){
  TL=tl; S={}; tl.scenes.forEach(s=>S[s.id]=s); lastScene=null; lastSub=-1;
  document.querySelectorAll('.scene').forEach(e=>e.style.display='block');
  document.querySelectorAll('[data-a]').forEach(el=>{
    const sc=el.closest('.scene'); if(!sc||!S[sc.id]) return; const s0=S[sc.id].start; const parts=[];
    el.dataset.a.trim().split(/\s+/).forEach((tok,k)=>{
      const m=tok.match(/^(\w+)@(s|\d+)([+-][\d.]+)?$/); if(!m){console.error('bad data-a',tok);return;}
      const d=DEF[m[1]]; if(!d){console.error('no anim',m[1]);return;}
      const base=m[2]==='s'?0:(tl.lines[+m[2]].start-s0); const delay=base+(m[3]?parseFloat(m[3]):0);
      parts.push(`${m[1]} ${d[0]}s ${d[1]} ${delay.toFixed(3)}s${d[2]?' infinite alternate':''} ${k===0?'both':(d[3]||'forwards')}`);
    });
    el.style.animation='none'; void el.offsetWidth; el.style.animation=parts.join(', ');
  });
  document.querySelectorAll('.scene').forEach(e=>e.style.display='none');
}
function updChapBar(id){ const st=$('chapstrip'); if(!st) return;   // 画面内章节条：当前章节高亮并居中
  if(!st.children.length) TL.scenes.forEach(s=>{ const c=document.createElement('span'); c.className='cb'; c.dataset.id=s.id;
    c.textContent=($(s.id).dataset.chap||s.id).split('·').pop().trim(); st.appendChild(c); });
  let on=-1; [...st.children].forEach((c,i)=>{ const k=c.dataset.id===id; if(k) on=i; c.className='cb'+(k?' on':(on<0?' done':'')); });
  const wm=$('wm'); if(wm&&on>=0) wm.className='wmk c'+(2+on%2);
  const c=st.children[on]; if(c){ const W=st.parentNode.clientWidth; let x=W/2-(c.offsetLeft+c.offsetWidth/2);
    x=Math.min(0,Math.max(W-st.scrollWidth,x)); st.style.transform=`translateX(${x}px)`; } }
function esc(s){return s.replace(/“([^”]+)”/g,'<em>“$1”</em>')}
function seek(t){
  const sc=TL.scenes.find(s=>t>=s.start&&t<s.end)||TL.scenes[TL.scenes.length-1];
  if(sc!==lastScene){document.querySelectorAll('.scene').forEach(e=>e.style.display=e.id===sc.id?'block':'none');
    chap.textContent=$(sc.id).dataset.chap||''; lastScene=sc; updChapBar(sc.id);}
  const lt=(t-sc.start)*1000;
  $(sc.id).getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=Math.max(0,lt);});
  let li=-1; for(let i=0;i<lines.length;i++){ if(TL.lines[i].start<=t+0.05) li=i; }
  const show= li>=0 && lines[li].scene===sc.id && (li<lines.length-1 || t<TL.lines[li].end+1.2);
  subW.style.display=show?'flex':'none';
  if(show){ if(li!==lastSub){subEl.innerHTML=esc(lines[li].sub);lastSub=li;}
    const k=Math.min(1,(t-TL.lines[li].start+0.05)/0.18), s=0.85+0.15*(1-Math.pow(1-k,3));
    subEl.style.transform=`scale(${s}) rotate(${li%2?0.6:-0.6}deg)`; subEl.style.opacity=Math.min(1,k*1.6);}
  prog.style.width=(540*Math.min(1,t/TL.total))+'px';
  if(cover&&COVER>0){ cover.style.display=t<COVER?'block':'none'; cover.style.opacity=Math.min(1,Math.max(0,(COVER-t)/0.35)); }
  if(src) src.style.display = t>=TL.lines[lines.length-1].start ? 'block':'none';
  return li;
}
window.seek=seek;
const trackOf=id=>(P.tracks||[]).find(t=>t.id===id);
const baseTL=()=> (P.tracks&&P.tracks.length)?P.tracks[0].timeline:estimate();

if(RENDER){ applyTimeline((trackOf(Q.get('voice'))||{}).timeline||baseTL()); seek(0); window.TOTAL=TL.total; window.READY=true; return; }

/* ---------------- preview player ---------------- */
document.body.classList.add('player');
const ui=document.createElement('div'); ui.id='ui'; ui.innerHTML=`
<div class="row"><button id="pp">▶</button><span id="tm">0:00</span><input id="scrub" type="range" min="0" max="1000" value="0"><span id="tt"></span></div>
<div class="row" id="chips"></div>
<div class="row"><label>配音</label><select id="vsel"></select>
 <label id="rl" style="display:none">语速<input id="rate" type="range" min="0.7" max="1.5" step="0.05" value="1.05"></label>
 <label id="ol" style="display:none">偏移<input id="off" type="range" min="-5" max="5" step="0.05" value="0"><span id="ov">0.00s</span></label></div>
<div class="row small" id="hint"></div>
<div class="row"><button class="sm" id="bimp">导入我的配音…</button><button class="sm" id="brec">逐句录音</button><button class="sm" id="bexp" disabled>导出我的配音 ZIP</button>
 <input id="fimp" type="file" accept="audio/*,video/*,.zip" multiple style="display:none"></div>
<div id="recp" style="display:none">
 <div class="small" id="rinfo"></div><div id="rtext"></div>
 <div class="row"><button class="sm" id="rprev">◀ 上一句</button><button id="rgo">● 录制</button><button class="sm" id="rplay">▶ 试听</button><button class="sm" id="rnext">下一句 ▶</button><label class="small"><input type="checkbox" id="rauto" checked>停止后自动下一句</label></div></div>
<div class="row" id="recrow"><button id="brender">● 录制视频</button><button class="sm" id="bhq">高清渲染 1080×1920…</button><span class="small" id="rstat"></span></div>
<div class="row"><button class="sm" id="xtxt">导出台词 TXT</button><button class="sm" id="xsrt">导出字幕 SRT</button><button class="sm" id="xjson">导出时间轴</button></div>`;
document.body.appendChild(ui);
const css=document.createElement('style'); css.textContent=`
body.player{display:flex;flex-direction:column;align-items:center;min-height:100vh;padding:8px 0 16px;color:#eee;font-family:system-ui,"PingFang SC","Microsoft YaHei",sans-serif}
body.player #wrap{position:relative;overflow:hidden;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.5)}
#ui{width:min(560px,96vw);margin-top:10px;display:flex;flex-direction:column;gap:8px}
#ui .row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
#ui button{background:#ffd23f;color:#141414;border:0;border-radius:8px;font-weight:800;padding:8px 14px;cursor:pointer;font-size:15px}
#ui button.sm{background:#3a3a44;color:#eee;font-weight:600;padding:6px 10px;font-size:13px}
#ui button:disabled{opacity:.4;cursor:default}
#ui #rgo.on{background:#ff4757;color:#fff}
#ui #scrub{flex:1;min-width:120px;accent-color:#ff4757}
#ui select{flex:1;min-width:180px;padding:6px;border-radius:6px;background:#2a2a33;color:#eee;border:1px solid #555;font-size:14px}
#ui .chip{background:#2a2a33;color:#ddd;border:1px solid #444;border-radius:14px;padding:3px 9px;font-size:12px;cursor:pointer;white-space:nowrap}
#ui .chip.on{background:#ffd23f;color:#141414;border-color:#ffd23f}
#ui #chips{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}
#ui .small{font-size:12px;color:#aaa;line-height:1.5}
#ui label{font-size:14px;color:#ccc;display:flex;align-items:center;gap:6px}
#recp{background:#2a2a33;border:1px solid #444;border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:8px}
#rtext{font-size:20px;font-weight:800;color:#ffd23f;line-height:1.4}`;
document.head.appendChild(css);
const wrap=document.createElement('div'); wrap.id='wrap'; stage.parentNode.insertBefore(wrap,stage); wrap.appendChild(stage);
function fit(){ const s=Math.min((innerHeight-(ui.offsetHeight+40))/960,(innerWidth-16)/540,1.2); const k=Math.max(.3,s);
  stage.style.transform=`scale(${k})`; wrap.style.width=540*k+'px'; wrap.style.height=960*k+'px'; }
addEventListener('resize',fit);

const audio=new Audio(); audio.preload='auto';
let mode='mute', t=0, playing=false, last=0, speakIdx=0, speaking=false, curSpeak=-1, speechTimer=null, voices=[];
let actx=null, clips=[], srcs=[], fileURL=null, fileName='', offset=0;
const AC=()=>{ if(!actx) actx=new (window.AudioContext||window.webkitAudioContext)(); if(actx.state==='suspended') actx.resume(); return actx; };
let master=null, recDest=null, mediaSrc=null;
const OUT=()=>{ const c=AC(); if(!master){ master=c.createGain(); master.connect(c.destination); } return master; };
const fmt=x=>{x=Math.max(0,x);return Math.floor(x/60)+':'+String(Math.floor(x%60)).padStart(2,'0')};
const vsel=$('vsel'), hint=$('hint');

/* timeline from per-line durations (same rule as build.py) */
function tlFrom(durs){ const tm=P.timing||{pre:.8,gap:.28,scene_gap:.7,tail:3}; const est=estimate();
  let t=tm.pre, prev=null; const L=[], S=[];
  lines.forEach((o,i)=>{ if(prev&&o.scene!==prev) t+=tm.scene_gap;
    if(o.scene!==prev) S.push({id:o.scene,start:prev?t-tm.scene_gap/2:0});
    const d=durs[i]!=null?durs[i]:(est.lines[i].end-est.lines[i].start);
    L.push({start:t,end:t+d}); t+=d+tm.gap; prev=o.scene; });
  const total=t+tm.tail; S.forEach((s,i)=>s.end=i+1<S.length?S[i+1].start:total); return {total,lines:L,scenes:S}; }
const clipsTL=()=>tlFrom(lines.map((_,i)=>clips[i]?clips[i].duration:null));
const nClips=()=>clips.filter(Boolean).length;

function buildVoiceList(){
  const cur=vsel.value; vsel.innerHTML='';
  const g1=document.createElement('optgroup'); g1.label='已生成的配音（可直接渲染成视频）';
  (P.tracks||[]).forEach(tr=>g1.appendChild(new Option(tr.name,'track:'+tr.id)));
  if(g1.children.length) vsel.appendChild(g1);
  const g0=document.createElement('optgroup'); g0.label='我的配音';
  if(nClips()) g0.appendChild(new Option(`我的逐句配音（${nClips()}/${lines.length} 句）`,'clips'));
  if(fileURL) g0.appendChild(new Option(`我的整段配音：${fileName}`,'file'));
  if(g0.children.length) vsel.appendChild(g0);
  vsel.appendChild(new Option('静音（自己录音 / 剪映配音用）','mute'));
  if([...vsel.options].some(o=>o.value===cur)) vsel.value=cur;
  $('bexp').disabled=!nClips();
}
function setMode(v){
  stopAll(); const was=playing; playing=false;
  const firstId=(P.tracks&&P.tracks[0])?P.tracks[0].id:'';
  if(v.startsWith('track:')){ const tr=trackOf(v.slice(6)); mode='track'; audio.src=tr.audio; applyTimeline(tr.timeline);
    hint.textContent='内置配音：画面与这条配音的时间轴精确对齐，确认后可直接用同一配音渲染 MP4。'; }
  else if(v==='clips'){ mode='clips'; applyTimeline(clipsTL());
    hint.textContent=`我的逐句配音：时间轴已按你每句录音的实际长度重排，画面自动对齐。缺的句子按估算时长留空。出视频：点“导出我的配音 ZIP”，解压到 proj/my_voice，然后运行 python kit/build.py proj --voice "files:proj/my_voice=我的配音"，再 python kit/render.py proj --voice 我的配音。`; }
  else if(v==='file'){ mode='file'; audio.src=fileURL; applyTimeline(baseTL());
    hint.textContent=`我的整段配音：画面按${firstId?'第一条内置配音':'估算'}的时间轴播放，用“偏移”微调对齐（正数=配音晚开始）。出视频：python kit/render.py proj${firstId?' --voice '+firstId:''} --audio 你的录音文件 --offset ${offset.toFixed(2)}。想让画面跟着你的语速走，请用逐句录音或逐句文件。`; }
  else if(v.startsWith('speech:')){ mode='speech'; applyTimeline(baseTL());
    hint.textContent='浏览器语音：仅用于预览试听（逐句朗读，画面会等语音读完）。Edge 浏览器里有免费的“Microsoft 晓晓/云希 Online (Natural)”等自然音。要用它出视频，请在渲染时选择对应引擎（见 README）。'; }
  else { mode='mute'; applyTimeline(baseTL()); hint.textContent='静音：按时间轴播放，适合对着画面录整段配音，或导出台词/SRT 到剪映配音。'; }
  $('rl').style.display=mode==='speech'?'flex':'none'; $('ol').style.display=mode==='file'?'flex':'none';
  t=Math.min(t,TL.total); render(); fit(); if(was) play();
}
vsel.onchange=()=>setMode(vsel.value);
$('off').oninput=e=>{ offset=+e.target.value; $('ov').textContent=offset.toFixed(2)+'s'; if(mode==='file') setMode('file'); };

function stopSrcs(){ srcs.forEach(s=>{try{s.stop()}catch(e){}}); srcs=[]; }
function stopSpeech(){ if('speechSynthesis' in window) speechSynthesis.cancel(); speaking=false; curSpeak=-1; clearTimeout(speechTimer); }
function stopAll(){ stopSpeech(); stopSrcs(); audio.pause(); }
function scheduleClips(t0){ stopSrcs(); const c=AC(), now=c.currentTime+0.05;
  clips.forEach((b,i)=>{ if(!b) return; const L=TL.lines[i]; if(L.start+b.duration<=t0) return;
    const s=c.createBufferSource(); s.buffer=b; s.connect(OUT()); const st=L.start-t0;
    s.start(now+Math.max(0,st), Math.max(0,-st)); srcs.push(s); }); }
function syncFile(){ const at=t-offset; if(at<0||at>(audio.duration||1e9)){ audio.pause(); return; }
  if(Math.abs(audio.currentTime-at)>0.25) audio.currentTime=at; if(audio.paused) audio.play().catch(()=>{}); }
function speakLine(i){
  const v=voices[+vsel.value.slice(7)]; const u=new SpeechSynthesisUtterance(lines[i].say||lines[i].sub.replace(/[“”]/g,''));
  if(v){u.voice=v;u.lang=v.lang;} u.rate=+$('rate').value; speaking=true; curSpeak=i;
  const done=()=>{ if(curSpeak===i){speaking=false;curSpeak=-1;clearTimeout(speechTimer);} };
  u.onend=done; u.onerror=done;
  speechTimer=setTimeout(done,((lines[i].say||lines[i].sub).length*0.35/u.rate+4)*1000);
  speechSynthesis.speak(u);
}
function syncSpeechIdx(){ speakIdx=TL.lines.findIndex(l=>l.start>=t-0.05); if(speakIdx<0) speakIdx=lines.length; }
function play(){ if(t>=TL.total-0.05) t=0; playing=true; last=performance.now();
  if(mode==='track'){ audio.currentTime=t; audio.play().catch(e=>{hint.textContent='浏览器阻止了自动播放，请再点一次 ▶';playing=false;$('pp').textContent='▶';}); }
  if(mode==='clips') scheduleClips(t);
  if(mode==='file') syncFile();
  if(mode==='speech'){ const li=TL.lines.findIndex(l=>t>=l.start-0.05&&t<l.end); if(li>=0) t=TL.lines[li].start; syncSpeechIdx(); }
  $('pp').textContent='❚❚'; }
function pause(){ playing=false; stopAll(); $('pp').textContent='▶'; }
$('pp').onclick=()=>playing?pause():play();
addEventListener('keydown',e=>{ if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName)&&e.target.type!=='range') return;
  if(e.code==='Space'){e.preventDefault();playing?pause():play();}
  if(e.code==='ArrowRight'){jump(t+5)} if(e.code==='ArrowLeft'){jump(t-5)} });
function jump(x){ t=Math.max(0,Math.min(TL.total,x));
  if(mode==='track') audio.currentTime=t;
  if(mode==='clips'&&playing) scheduleClips(t);
  if(mode==='file'&&playing) syncFile();
  if(mode==='speech'){stopSpeech(); if(playing){const li=TL.lines.findIndex(l=>t>=l.start-0.05&&t<l.end); if(li>=0)t=TL.lines[li].start; syncSpeechIdx();}}
  render(); }
$('scrub').oninput=e=>jump(e.target.value/1000*TL.total);
function render(){ seek(t); $('tm').textContent=fmt(t); $('tt').textContent=fmt(TL.total);
  $('scrub').value=Math.round(t/TL.total*1000);
  document.querySelectorAll('#chips .chip').forEach(c=>c.classList.toggle('on',c.dataset.id===(lastScene&&lastScene.id))); }
function tick(now){ const dt=(now-last)/1000; last=now;
  if(playing){
    if(mode==='track'){ t=audio.currentTime; if(audio.ended){ t=TL.total; pause(); } }
    else { let nt=t+dt;
      if(mode==='speech'){
        if(speaking && nt>TL.lines[curSpeak].end) nt=Math.max(t,TL.lines[curSpeak].end);
        if(!speaking && speakIdx<lines.length && nt>=TL.lines[speakIdx].start){ nt=TL.lines[speakIdx].start; speakLine(speakIdx); speakIdx++; }
      }
      t=nt; if(mode==='file'&&audio.paused&&t-offset>=0&&t-offset<(audio.duration||0)) syncFile();
      if(t>=TL.total){ t=TL.total; pause(); } }
    render(); }
  requestAnimationFrame(tick); }

/* ---------- import my own voice ---------- */
async function decode(ab){ return await AC().decodeAudioData(ab.slice(0)); }
function trim(b){ // cut leading/trailing silence, keep 80ms pad
  const d=b.getChannelData(0), th=0.02, pad=Math.floor(b.sampleRate*0.08); let s=0,e=d.length-1;
  while(s<e&&Math.abs(d[s])<th) s++; while(e>s&&Math.abs(d[e])<th) e--;
  s=Math.max(0,s-pad); e=Math.min(d.length-1,e+pad); if(e-s<b.sampleRate*0.2) return b;
  const o=AC().createBuffer(1,e-s+1,b.sampleRate); const od=o.getChannelData(0);
  for(let c=0;c<b.numberOfChannels;c++){ const x=b.getChannelData(c); for(let i=s;i<=e;i++) od[i-s]+=x[i]/b.numberOfChannels; }
  return o; }
function unzipStore(buf){ const v=new DataView(buf), out=[]; let p=0;
  while(p+30<=buf.byteLength && v.getUint32(p,true)===0x04034b50){
    const meth=v.getUint16(p+8,true), csz=v.getUint32(p+18,true), nl=v.getUint16(p+26,true), xl=v.getUint16(p+28,true);
    const name=new TextDecoder().decode(new Uint8Array(buf,p+30,nl)); const s=p+30+nl+xl;
    if(meth!==0) throw new Error('zip 使用了压缩，请先解压再选择里面的音频文件');
    if(!name.endsWith('/')) out.push({name:name.split('/').pop(),data:buf.slice(s,s+csz)}); p=s+csz; }
  return out; }
$('bimp').onclick=()=>$('fimp').click();
$('fimp').onchange=async e=>{
  const fs=[...e.target.files]; e.target.value=''; if(!fs.length) return;
  try{
    let items=[];
    for(const f of fs){ if(/\.zip$/i.test(f.name)) items.push(...unzipStore(await f.arrayBuffer()).filter(x=>/\.(wav|mp3|m4a|aac|ogg|webm|flac)$/i.test(x.name)));
      else items.push({name:f.name,file:f}); }
    if(items.length===1 && !/^\d+/.test(items[0].name)){ // whole-track recording
      const it=items[0]; fileName=it.name; if(fileURL) URL.revokeObjectURL(fileURL);
      fileURL=URL.createObjectURL(it.file||new Blob([it.data])); buildVoiceList(); vsel.value='file'; setMode('file'); return; }
    const numbered=items.every(x=>/^\d+/.test(x.name));
    items.sort((a,b)=>numbered?parseInt(a.name)-parseInt(b.name):a.name.localeCompare(b.name,'zh'));
    hint.textContent='正在读取音频…'; let n=0;
    for(let k=0;k<items.length;k++){ const it=items[k]; const idx=numbered?parseInt(it.name)-1:k; if(idx<0||idx>=lines.length) continue;
      const ab=it.data||await it.file.arrayBuffer(); clips[idx]=trim(await decode(ab)); n++; }
    buildVoiceList(); vsel.value='clips'; setMode('clips'); hint.textContent=`已导入 ${n} 句。`+hint.textContent;
  }catch(err){ hint.textContent='导入失败：'+err.message; }
};

/* ---------- record line by line in the browser ---------- */
let recI=0, rec=null, stream=null;
function showRec(){ $('rinfo').textContent=`第 ${recI+1}/${lines.length} 句 · ${clips[recI]?'已录 '+clips[recI].duration.toFixed(1)+'s':'未录'} · 共已录 ${nClips()} 句`;
  $('rtext').innerHTML=esc(lines[recI].say&&lines[recI].say!==lines[recI].sub?lines[recI].sub+'<div class="small">念法：'+lines[recI].say+'</div>':lines[recI].sub);
  const T=TL; t=Math.max(T.lines[recI].start+0.3,T.lines[recI].end-0.15); render(); }
$('brec').onclick=()=>{ const p=$('recp'); const on=p.style.display==='none'; p.style.display=on?'flex':'none';
  if(on){ pause(); recI=Math.max(0,TL.lines.findIndex(l=>l.end>t)); showRec(); } fit(); };
$('rprev').onclick=()=>{ recI=Math.max(0,recI-1); showRec(); };
$('rnext').onclick=()=>{ recI=Math.min(lines.length-1,recI+1); showRec(); };
$('rplay').onclick=()=>{ if(!clips[recI]) return; stopSrcs(); const s=AC().createBufferSource(); s.buffer=clips[recI]; s.connect(OUT()); s.start(); srcs.push(s); };
$('rgo').onclick=async()=>{
  if(rec&&rec.state==='recording'){ rec.stop(); return; }
  try{ stream=stream||await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}}); }
  catch(e){ hint.textContent='无法使用麦克风：'+e.message+'（请用 Chrome/Edge 打开下载后的 HTML，并允许麦克风）'; return; }
  const chunks=[]; rec=new MediaRecorder(stream); rec.ondataavailable=e=>chunks.push(e.data);
  rec.onstop=async()=>{ $('rgo').textContent='● 录制'; $('rgo').classList.remove('on');
    clips[recI]=trim(await decode(await new Blob(chunks).arrayBuffer())); buildVoiceList();
    if(vsel.value==='clips') applyTimeline(clipsTL());
    if($('rauto').checked&&recI<lines.length-1) recI++; showRec(); };
  rec.start(); $('rgo').textContent='■ 停止'; $('rgo').classList.add('on');
};

/* ---------- export my clips as ZIP (01.wav …) for build.py files:<dir> ---------- */
function wav(b){ const d=b.getChannelData(0), n=d.length, buf=new ArrayBuffer(44+n*2), v=new DataView(buf); const w=(o,s)=>[...s].forEach((c,i)=>v.setUint8(o+i,c.charCodeAt(0)));
  w(0,'RIFF'); v.setUint32(4,36+n*2,true); w(8,'WAVE'); w(12,'fmt '); v.setUint32(16,16,true); v.setUint16(20,1,true); v.setUint16(22,1,true);
  v.setUint32(24,b.sampleRate,true); v.setUint32(28,b.sampleRate*2,true); v.setUint16(32,2,true); v.setUint16(34,16,true); w(36,'data'); v.setUint32(40,n*2,true);
  for(let i=0;i<n;i++) v.setInt16(44+i*2,Math.max(-1,Math.min(1,d[i]))*32767,true); return new Uint8Array(buf); }
const CRC=(()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}return t})();
const crc32=a=>{let c=0xFFFFFFFF;for(let i=0;i<a.length;i++)c=CRC[(c^a[i])&255]^(c>>>8);return (c^0xFFFFFFFF)>>>0};
function zip(files){ const enc=new TextEncoder(), parts=[], cen=[]; let off=0;
  files.forEach(f=>{ const nm=enc.encode(f.name), crc=crc32(f.data), h=new DataView(new ArrayBuffer(30));
    h.setUint32(0,0x04034b50,true); h.setUint16(4,20,true); h.setUint16(6,0x0800,true); h.setUint32(14,crc,true); h.setUint32(18,f.data.length,true); h.setUint32(22,f.data.length,true); h.setUint16(26,nm.length,true);
    parts.push(new Uint8Array(h.buffer),nm,f.data);
    const c=new DataView(new ArrayBuffer(46)); c.setUint32(0,0x02014b50,true); c.setUint16(4,20,true); c.setUint16(6,20,true); c.setUint16(8,0x0800,true); c.setUint32(16,crc,true);
    c.setUint32(20,f.data.length,true); c.setUint32(24,f.data.length,true); c.setUint16(28,nm.length,true); c.setUint32(42,off,true); cen.push(new Uint8Array(c.buffer),nm);
    off+=30+nm.length+f.data.length; });
  const cs=cen.reduce((a,b)=>a+b.length,0), e=new DataView(new ArrayBuffer(22)); e.setUint32(0,0x06054b50,true); e.setUint16(8,files.length,true); e.setUint16(10,files.length,true); e.setUint32(12,cs,true); e.setUint32(16,off,true);
  return new Blob([...parts,...cen,new Uint8Array(e.buffer)],{type:'application/zip'}); }
$('bexp').onclick=()=>{ const fs=[]; clips.forEach((b,i)=>{ if(b) fs.push({name:String(i+1).padStart(2,'0')+'.wav',data:wav(b)}); });
  const miss=lines.map((_,i)=>i+1).filter(i=>!clips[i-1]);
  fs.push({name:'说明.txt',data:new TextEncoder().encode(`我的配音（${fs.length}/${lines.length} 句）\n解压到 proj/my_voice/ 后运行：\n  python kit/build.py proj --voice "files:proj/my_voice=我的配音"\n  python kit/render.py proj --voice 我的配音\n`+(miss.length?`\n缺少的句子：${miss.join(', ')}（build 前需要补齐）\n`:''))});
  const a=document.createElement('a'); a.href=URL.createObjectURL(zip(fs)); a.download=(P.title||'my')+'_我的配音.zip'; a.click(); };

/* ---------- record the preview as a video file (screen capture of the stage + clean audio) ---------- */
let vrec=null, vstream=null;
function currentName(){ const o=vsel.options[vsel.selectedIndex]; return o?o.textContent.replace(/[\\/:*?"<>|（）()\s]+/g,''):'mute'; }
async function recordVideo(){
  if(vrec){ vrec.stop(); return; }
  if(!navigator.mediaDevices||!navigator.mediaDevices.getDisplayMedia){ $('rstat').textContent='此浏览器不支持录制，请用最新版 Chrome / Edge 打开。'; return; }
  pause(); t=0; render(); fit();
  let disp;
  try{ disp=await navigator.mediaDevices.getDisplayMedia({video:{frameRate:30},audio:false,preferCurrentTab:true,selfBrowserSurface:'include'}); }
  catch(e){ $('rstat').textContent='未开始录制：'+e.name+'（请在弹窗里选择“此标签页”并点“共享”）'; return; }
  const vt=disp.getVideoTracks()[0];
  try{ if(window.CropTarget&&vt.cropTo){ await vt.cropTo(await CropTarget.fromElement(wrap)); } }catch(e){}
  const c=AC(); if(!recDest) recDest=c.createMediaStreamDestination(); OUT().connect(recDest);
  if(!mediaSrc){ mediaSrc=c.createMediaElementSource(audio); mediaSrc.connect(OUT()); }
  const tracks=[vt,...recDest.stream.getAudioTracks()]; vstream=new MediaStream(tracks);
  const types=['video/mp4;codecs=avc1.640028,mp4a.40.2','video/mp4','video/webm;codecs=vp9,opus','video/webm'];
  const mime=types.find(x=>window.MediaRecorder&&MediaRecorder.isTypeSupported(x))||'';
  const chunks=[]; vrec=new MediaRecorder(vstream,{mimeType:mime,videoBitsPerSecond:10e6,audioBitsPerSecond:160e3});
  vrec.ondataavailable=e=>e.data.size&&chunks.push(e.data);
  vrec.onstop=()=>{ disp.getTracks().forEach(x=>x.stop()); try{OUT().disconnect(recDest)}catch(e){}
    const ext=mime.includes('mp4')?'mp4':'webm'; const a=document.createElement('a');
    a.href=URL.createObjectURL(new Blob(chunks,{type:mime||'video/webm'})); a.download=`${P.title||'video'}_${currentName()}.${ext}`; a.click();
    vrec=null; document.body.classList.remove('recording'); $('brender').textContent='● 录制视频'; $('rstat').textContent=`已保存 ${ext.toUpperCase()}（录制分辨率 = 画面在屏幕上的实际像素）。`; };
  vt.onended=()=>{ if(vrec) vrec.stop(); };
  document.body.classList.add('recording'); $('brender').textContent='■ 停止录制';
  $('rstat').textContent='录制中…请保持此标签页在前台，播完会自动保存。';
  await new Promise(r=>setTimeout(r,400)); vrec.start(500); play();
  const iv=setInterval(()=>{ if(!vrec){clearInterval(iv);return;} if(!playing&&t>=TL.total-0.01){ clearInterval(iv); setTimeout(()=>vrec&&vrec.stop(),600); } },200);
}
$('brender').onclick=recordVideo;
$('bhq').onclick=()=>{ const name=vsel.value.startsWith('track:')?(trackOf(vsel.value.slice(6))||{}).name:''; 
  const msg=name?`请用「${name}」配音渲染 1080×1920 MP4`:'请用我的配音渲染 1080×1920 MP4';
  const cmd=name?`python kit/render.py proj --voice "${name}"`:'（先导出我的配音 ZIP，见说明）';
  if(navigator.clipboard) navigator.clipboard.writeText(msg).catch(()=>{});
  $('rstat').innerHTML=`高清渲染在 Claude 或本机完成：已复制“${msg}”，粘贴给 Claude 即可；自己渲染：<code>${cmd}</code>`; };
const rcss=document.createElement('style'); rcss.textContent=`body.recording #wrap{cursor:none;outline:3px solid #ff4757} #ui #brender{background:#ff4757;color:#fff} body.recording #ui .row:not(:first-child):not(#recrow){opacity:.35;pointer-events:none} #ui code{background:#111;padding:2px 6px;border-radius:4px;color:#ffd23f}`;
document.head.appendChild(rcss);

// chips
const chips=$('chips');
(baseTL().scenes).forEach(s=>{ const c=document.createElement('span'); c.className='chip'; c.dataset.id=s.id;
  c.textContent=($(s.id).dataset.chap||s.id).split('·').pop().trim(); c.onclick=()=>{ const i=lines.findIndex(l=>l.scene===s.id); jump(i>=0?TL.lines[i].start:S[s.id].start+0.01); if(!playing) play(); }; chips.appendChild(c); });
// exports
function dl(name,text){ const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'})); a.download=name; a.click(); }
const srtT=x=>{const ms=Math.round(x*1000);const h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,s=Math.floor(ms/1000)%60;return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`};
const plain=s=>s.replace(/<[^>]+>/g,'');
$('xtxt').onclick=()=>dl((P.title||'script')+'_台词.txt', lines.map((l,i)=>`${String(i+1).padStart(2,'0')} [${l.scene}] ${plain(l.sub)}`).join('\n'));
$('xsrt').onclick=()=>dl((P.title||'subs')+'.srt', lines.map((l,i)=>`${i+1}\n${srtT(TL.lines[i].start+(mode==='file'?0:0))} --> ${srtT(i+1<lines.length?Math.min(TL.lines[i+1].start,TL.lines[i].end+0.6):TL.lines[i].end+1)}\n${plain(l.sub)}\n`).join('\n'));
$('xjson').onclick=()=>dl((P.title||'timeline')+'_timeline.json', JSON.stringify(TL,null,1));
buildVoiceList(); vsel.value=vsel.options[0].value; setMode(vsel.value); fit(); requestAnimationFrame(t0=>{last=t0;requestAnimationFrame(tick)});
window.__player={get clips(){return clips}, setMode, get TL(){return TL}};
window.READY=true;
})();
````

### kit/tts.py
````python
"""Pluggable TTS engines. Voice spec strings:
  kokoro:<sid>      offline (sherpa-onnx Kokoro v1.1 zh+en, 103 speakers; e.g. 4 = female, 60 = male)
  melo              offline (sherpa-onnx MeloTTS zh_en)
  edge:<voice>      Microsoft Edge online neural voices via https://github.com/rany2/edge-tts (free, needs internet; pip install edge-tts)
                    e.g. edge:zh-CN-XiaoxiaoNeural  edge:zh-CN-YunxiNeural  edge:zh-CN-YunjianNeural  edge:zh-CN-XiaoyiNeural
                    pitch/volume: edge:zh-CN-YunxiNeural|+5Hz|+10%@1.1 ; list voices: python tts.py --list-edge zh
  minimax:<voice_id>        MiniMax T2A v2 (needs MINIMAX_API_KEY). e.g. minimax:female-shaonv  minimax:presenter_male
                    optional emotion: minimax:presenter_female|happy ; env MINIMAX_MODEL (default speech-2.8-hd),
                    MINIMAX_API_HOST (default https://api.minimax.io ; mainland China accounts: https://api.minimaxi.com)
                    list voices: python tts.py --list-minimax
  listenhub:<speakerId>     ListenHub TTS (sync /v1/tts, needs LISTENHUB_API_KEY)
  flowspeech:<speakerId>    ListenHub FlowSpeech (async /v1/flow-speech/episodes, mode=direct; lines submitted in parallel)
                    list voices: python tts.py --list-listenhub zh
  API keys: environment variables, or KEY=VALUE lines in ./.env , <project>/.env , ~/.config/comic-video/keys.env
  say:<voice>       macOS built-in `say`, e.g. say:Tingting  say:Meijia
  openai:<voice>    OpenAI TTS (needs OPENAI_API_KEY), e.g. openai:alloy ; model via OPENAI_TTS_MODEL (default gpt-4o-mini-tts)
  files:<dir>       your own recordings: <dir>/01.wav|mp3|m4a ... numbered from 01 in script order
Optional suffix @<speed> e.g. kokoro:4@1.1 , edge:zh-CN-YunxiNeural@1.1
Every engine writes a mono WAV and returns its duration in seconds."""
import os, sys, subprocess, shutil, tempfile, json, urllib.request, urllib.error, tarfile
CACHE = os.path.expanduser(os.environ.get('COMIC_TTS_CACHE', '~/.cache/comic-video'))
REL = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/'


# 沙箱/公司代理会做 HTTPS 中间人：让 edge-tts（用 certifi）改用系统证书，云端也能直连 Edge 配音
if os.environ.get('SSL_CERT_FILE') and os.path.exists(os.environ['SSL_CERT_FILE']):
    try:
        import certifi; certifi.where = lambda: os.environ['SSL_CERT_FILE']
    except ImportError: pass

def _dl_model(name):
    d = os.path.join(CACHE, name)
    if os.path.isdir(d): return d + '/'
    os.makedirs(CACHE, exist_ok=True)
    tb = os.path.join(CACHE, name + '.tar.bz2')
    print(f'[tts] downloading {name} ...', file=sys.stderr)
    urllib.request.urlretrieve(REL + name + '.tar.bz2', tb)
    with tarfile.open(tb) as t: t.extractall(CACHE)
    os.remove(tb); return d + '/'

def _to_wav(src, out):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', '24000', out], check=True)

def _trim(path, th=0.012, pad=0.06):
    """Cut leading/trailing silence (edge-tts adds ~0.2s + ~0.6-0.9s; recordings often more)."""
    import soundfile as sf, numpy as np
    a, sr = sf.read(path)
    if a.ndim > 1: a = a.mean(1)
    nz = np.where(np.abs(a) > th)[0]
    if len(nz) == 0: return
    s0 = max(0, nz[0] - int(pad * sr)); e0 = min(len(a), nz[-1] + int(pad * sr) + 1)
    sf.write(path, a[s0:e0], sr)

def _dur(path):
    import soundfile as sf
    i = sf.info(path); return i.frames / i.samplerate

_sherpa = {}
def _sherpa_tts(kind):
    if kind in _sherpa: return _sherpa[kind]
    import sherpa_onnx as so
    if kind == 'kokoro':
        d = _dl_model('kokoro-multi-lang-v1_1')
        m = so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(model=d+'model.onnx', voices=d+'voices.bin', tokens=d+'tokens.txt',
              data_dir=d+'espeak-ng-data', dict_dir=d+'dict', lexicon=d+'lexicon-us-en.txt,'+d+'lexicon-zh.txt'), num_threads=os.cpu_count() or 2)
        fst = f'{d}date-zh.fst,{d}phone-zh.fst,{d}number-zh.fst'
    else:
        d = _dl_model('vits-melo-tts-zh_en')
        m = so.OfflineTtsModelConfig(vits=so.OfflineTtsVitsModelConfig(model=d+'model.onnx', lexicon=d+'lexicon.txt', tokens=d+'tokens.txt', dict_dir=d+'dict'), num_threads=os.cpu_count() or 2)
        fst = f'{d}date.fst,{d}phone.fst,{d}number.fst,{d}new_heteronym.fst'
    _sherpa[kind] = so.OfflineTts(so.OfflineTtsConfig(model=m, rule_fsts=fst)); return _sherpa[kind]

def _proxy():   # aiohttp ignores *_PROXY env vars, so pass them explicitly (needed behind sandbox/corporate proxies)
    for k in ('EDGE_TTS_PROXY', 'HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy'):
        if os.environ.get(k): return os.environ[k]
    return None

def _edge(text, voice, speed, path):
    """Microsoft Edge online neural voices via edge-tts (free, needs internet; WebSocket to speech.platform.bing.com).
    Voice may carry pitch/volume: zh-CN-YunxiNeural|+5Hz|+0%   env: EDGE_TTS_PROXY (http proxy), EDGE_TTS_PITCH, EDGE_TTS_VOLUME"""
    import asyncio, time
    try: import edge_tts
    except ImportError: raise SystemExit('edge 引擎需要: pip install edge-tts')
    parts = voice.split('|'); voice = parts[0]
    pitch = parts[1] if len(parts) > 1 else os.environ.get('EDGE_TTS_PITCH', '+0Hz')
    volume = parts[2] if len(parts) > 2 else os.environ.get('EDGE_TTS_VOLUME', '+0%')
    rate = f'{round((speed - 1) * 100):+d}%'
    async def run():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume, proxy=_proxy()).save(path)
    for k in range(4):
        try:
            asyncio.run(run())
            if os.path.getsize(path) > 0: return
        except Exception as e:
            if k == 3: raise RuntimeError(f'edge-tts 失败（需要能连上 speech.platform.bing.com 的 WebSocket）：{e}')
        time.sleep(1.5 * (k + 1))

def list_edge(prefix='zh'):
    import asyncio, edge_tts
    vs = asyncio.run(edge_tts.list_voices(proxy=_proxy()))
    for v in sorted(vs, key=lambda v: v['ShortName']):
        if v['Locale'].lower().startswith(prefix.lower()):
            tag = v.get('VoiceTag', {}); pers = ','.join(tag.get('VoicePersonalities', []))
            print(f"edge:{v['ShortName']:<28} {v['Gender']:<7} {pers}")

def _key(name):
    if os.environ.get(name): return os.environ[name]
    here = os.path.dirname(os.path.abspath(__file__))
    for f in ('.env', os.path.join(here, '..', '.env'), os.path.join(here, '..', 'proj', '.env'), os.path.expanduser('~/.config/comic-video/keys.env')):
        if os.path.exists(f):
            for ln in open(f, encoding='utf-8'):
                k, _, v = ln.strip().partition('=')
                if k.strip() == name and v.strip(): return v.strip().strip('"').strip("'")
    raise SystemExit(f'缺少 {name}：设为环境变量，或写入项目根目录 .env（{name}=...）')

def _http(url, key, body=None, method=None, raw=False, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method or ('POST' if data else 'GET'),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    import time
    for k in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read(); return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if e.code in (429, 500, 502, 503, 504) and k < 3: time.sleep(2 * (k + 1)); continue
            raise RuntimeError(f'{url} -> HTTP {e.code}: {msg}')
        except urllib.error.URLError as e:
            if k < 3: time.sleep(2 * (k + 1)); continue
            raise

# ---------- MiniMax T2A v2 ----------
def _minimax(text, voice, speed, path):
    key = _key('MINIMAX_API_KEY'); host = os.environ.get('MINIMAX_API_HOST', 'https://api.minimax.io').rstrip('/')
    voice, _, emotion = voice.partition('|')
    vs = {'voice_id': voice or 'female-shaonv', 'speed': speed, 'vol': 1, 'pitch': 0}
    if emotion: vs['emotion'] = emotion
    body = {'model': os.environ.get('MINIMAX_MODEL', 'speech-2.8-hd'), 'text': text, 'stream': False,
            'language_boost': 'Chinese', 'output_format': 'hex', 'voice_setting': vs,
            'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1}}
    r = _http(host + '/v1/t2a_v2', key, body)
    br = r.get('base_resp', {})
    if br.get('status_code', 0) != 0: raise RuntimeError(f"MiniMax 错误 {br.get('status_code')}: {br.get('status_msg')}")
    open(path, 'wb').write(bytes.fromhex(r['data']['audio']))

def list_minimax():
    key = _key('MINIMAX_API_KEY'); host = os.environ.get('MINIMAX_API_HOST', 'https://api.minimax.io').rstrip('/')
    r = _http(host + '/v1/get_voice', key, {'voice_type': 'all'})
    for group in ('system_voice', 'voice_cloning', 'voice_generation'):
        for v in r.get(group) or []:
            print(f"minimax:{v.get('voice_id'):<48} {v.get('voice_name', '')}  {' '.join(v.get('description') or [])[:60]}")

# ---------- ListenHub (TTS / FlowSpeech) ----------
LH = os.environ.get('LISTENHUB_API_BASE', 'https://api.marswave.ai/openapi/v1').rstrip('/')
def _listenhub_tts(text, speaker, speed, path):
    b = _http(LH + '/tts', _key('LISTENHUB_API_KEY'), {'input': text, 'voice': speaker, 'response_format': 'mp3', 'speed': speed}, raw=True)
    open(path, 'wb').write(b)

def _download(url, path):
    with urllib.request.urlopen(url, timeout=300) as r, open(path, 'wb') as f: f.write(r.read())

def _flowspeech_one(text, speaker, speed, path, poll=4, max_wait=900):
    import time
    key = _key('LISTENHUB_API_KEY')
    if len(text) < 10:                       # FlowSpeech needs >= 10 chars; short lines use the same voice via /tts
        return _listenhub_tts(text, speaker, speed, path)
    r = _http(LH + '/flow-speech/episodes', key, {'sources': [{'type': 'text', 'content': text}], 'speakers': [{'speakerId': speaker}],
                                                  'language': 'zh', 'mode': 'direct', 'speed': speed})
    if r.get('code', 0) != 0: raise RuntimeError(f'FlowSpeech 提交失败: {r}')
    eid = r['data']['episodeId']; t0 = time.time()
    while time.time() - t0 < max_wait:
        time.sleep(poll)
        d = _http(f'{LH}/flow-speech/episodes/{eid}', key).get('data', {})
        st = d.get('processStatus')
        if st == 'success': return _download(d['audioUrl'], path)
        if st == 'fail': raise RuntimeError(f'FlowSpeech 生成失败: episode {eid}')
    raise TimeoutError(f'FlowSpeech 超时: episode {eid}')

_prefetched = {}
def prefetch(spec, jobs):
    """jobs: [(index, text)] still to synthesize. FlowSpeech is async (1–2 min per episode), so submit all lines in parallel."""
    speed = 1.0
    if '@' in spec: spec, sp = spec.rsplit('@', 1); speed = float(sp)
    eng, _, arg = spec.partition(':')
    if eng != 'flowspeech' or not jobs: return
    import tempfile, concurrent.futures as cf
    tmpd = tempfile.mkdtemp(prefix='flowspeech_')
    def one(job):
        i, text = job; p = os.path.join(tmpd, f'{i:03d}.mp3'); _flowspeech_one(clean(text), arg, speed, p); return i, p
    with cf.ThreadPoolExecutor(int(os.environ.get('LISTENHUB_PARALLEL', '6'))) as ex:
        for n, (i, p) in enumerate(ex.map(one, jobs), 1):
            _prefetched[(spec, i)] = p; print(f'  [flowspeech] {n}/{len(jobs)} 完成', file=sys.stderr, flush=True)

def list_listenhub(lang='zh'):
    r = _http(f'{LH}/speakers/list?language={lang}', _key('LISTENHUB_API_KEY'))
    for v in (r.get('data') or {}).get('items', []):
        prof = v.get('profile') or {}
        print(f"listenhub:{v.get('speakerId'):<36} {v.get('name', '')}  {v.get('gender', '')}  {(prof.get('descriptionLocalized') or prof.get('description') or '')[:50]}")

def clean(text):
    """Punctuation some engines drop -> pauses they understand."""
    return (text.replace('：', '，').replace('；', '。').replace('——', '，').replace('…', '。')
                .replace('“', '').replace('”', '').replace('＋', '加').replace('＝', '等于').replace('×', '乘'))

def synth(spec, text, out, index=None):
    speed = 1.0
    if '@' in spec: spec, sp = spec.rsplit('@', 1); speed = float(sp)
    eng, _, arg = spec.partition(':')
    text = clean(text)
    if eng in ('kokoro', 'melo'):
        import soundfile as sf
        tts = _sherpa_tts(eng); sid = int(arg or 0)
        a = tts.generate(text, sid=sid, speed=speed); sf.write(out, a.samples, a.sample_rate)
    elif eng == 'edge':   # https://github.com/rany2/edge-tts
        tmp = out + '.mp3'; _edge(text, arg or 'zh-CN-XiaoxiaoNeural', speed, tmp); _to_wav(tmp, out); os.remove(tmp); _trim(out)
    elif eng == 'say':
        tmp = out + '.aiff'; cmd = ['say', '-o', tmp, '-r', str(int(190*speed))]
        if arg: cmd += ['-v', arg]
        subprocess.run(cmd + [text], check=True); _to_wav(tmp, out); os.remove(tmp)
    elif eng == 'minimax':
        tmp = out + '.mp3'; _minimax(text, arg, speed, tmp); _to_wav(tmp, out); os.remove(tmp); _trim(out)
    elif eng == 'listenhub':
        tmp = out + '.mp3'; _listenhub_tts(text, arg, speed, tmp); _to_wav(tmp, out); os.remove(tmp); _trim(out)
    elif eng == 'flowspeech':
        p = _prefetched.pop((spec, index), None)
        if not p: p = out + '.mp3'; _flowspeech_one(text, arg, speed, p)
        _to_wav(p, out); os.remove(p); _trim(out)
    elif eng == 'openai':
        key = os.environ['OPENAI_API_KEY']; tmp = out + '.mp3'
        body = json.dumps({'model': os.environ.get('OPENAI_TTS_MODEL', 'gpt-4o-mini-tts'), 'voice': arg or 'alloy', 'input': text,
                           'speed': speed, 'response_format': 'mp3',
                           'instructions': os.environ.get('OPENAI_TTS_INSTRUCTIONS', '用自然、活泼的普通话讲解科普视频')}).encode()
        req = urllib.request.Request('https://api.openai.com/v1/audio/speech', data=body, headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r, open(tmp, 'wb') as f: f.write(r.read())
        _to_wav(tmp, out); os.remove(tmp)
    elif eng == 'files':
        n = f'{index+1:02d}'
        for ext in ('wav', 'mp3', 'm4a', 'aac', 'flac', 'ogg'):
            p = os.path.join(arg, f'{n}.{ext}')
            if os.path.exists(p): _to_wav(p, out); _trim(out); break
        else: raise FileNotFoundError(f'recording {n}.* not found in {arg}')
    else:
        raise ValueError('unknown engine ' + eng)
    return _dur(out)

if __name__ == '__main__':
    if sys.argv[1:2] == ['--list-minimax']:
        list_minimax()
    elif sys.argv[1:2] == ['--list-listenhub']:
        list_listenhub(sys.argv[2] if len(sys.argv) > 2 else 'zh')
    elif sys.argv[1:2] == ['--list-edge']:          # python tts.py --list-edge zh   (zh / zh-CN / zh-TW / zh-HK / ja / en ...)
        list_edge(sys.argv[2] if len(sys.argv) > 2 else 'zh')
    else:
        spec, text, out = sys.argv[1:4]           # python tts.py edge:zh-CN-XiaoxiaoNeural@1.1 "你好" test.wav
        print(synth(spec, text, out))
````

### kit/build.py
````python
"""Build voice tracks + preview.html for a comic-video project.
usage: python build.py <project_dir> [--voice "kokoro:4=女声（离线）" --voice "edge:zh-CN-YunxiNeural=云希"] [--drop <spec>] [--no-embed]
project_dir contains script.json and scenes.html. Outputs in <project_dir>/build/ :
  voices/<id>/NN.wav (cached per line text), <id>.wav (final mix), <id>.timeline.json, preview.html
Voices accumulate in build/voices.json; with no --voice, rebuilds every registered voice (cached lines are reused).
A packaged project (pack.py) ships line clips as mp3 (under 配音/); meta.json points to them, so no re-synthesis is needed."""
import os, sys, json, hashlib, argparse, base64, subprocess, re
import numpy as np, soundfile as sf
KIT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, KIT)

def vid(spec): return re.sub(r'[^A-Za-z0-9_-]+', '_', spec).strip('_')

def synth_lines(proj, spec, lines):
    import tts
    d = os.path.join(proj, 'build', 'voices', vid(spec)); os.makedirs(d, exist_ok=True)
    mf = os.path.join(d, 'meta.json'); meta = json.load(open(mf)) if os.path.exists(mf) else {}
    todo = []
    for i, o in enumerate(lines):   # batch engines (FlowSpeech) submit all missing lines at once
        text = o.get('say') or re.sub(r'<[^>]+>', '', o['sub'])
        h = hashlib.md5((spec + '|' + text).encode()).hexdigest()
        if meta.get(str(i), {}).get('h') != h: todo.append((i, text))
    if todo and hasattr(tts, 'prefetch'): tts.prefetch(spec, todo)
    durs = []
    for i, o in enumerate(lines):
        text = o.get('say') or re.sub(r'<[^>]+>', '', o['sub'])
        h = hashlib.md5((spec + '|' + text).encode()).hexdigest(); p = os.path.join(d, f'{i:02d}.wav')
        if meta.get(str(i), {}).get('h') == h:
            alt = os.path.normpath(os.path.join(d, meta[str(i)].get('mp3', f'{i:02d}.mp3')))   # clip shipped by pack.py
            if not os.path.exists(p) and os.path.exists(alt):
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', alt, '-ac', '1', '-ar', '24000', p], check=True)
            if os.path.exists(p): durs.append(meta[str(i)]['d']); continue
        dur = tts.synth(spec, text, p, index=i); meta[str(i)] = {'h': h, 'd': dur}; durs.append(dur)
        print(f'  [{spec}] {i+1}/{len(lines)} {dur:.1f}s {text[:24]}', flush=True)
        json.dump(meta, open(mf, 'w'))
    return d, durs

def timeline(lines, durs, tm):
    t = tm['pre']; prev = None; L = []; S = []
    for o, d in zip(lines, durs):
        if prev and o['scene'] != prev: t += tm['scene_gap']
        if o['scene'] != prev: S.append({'id': o['scene'], 'start': round(t - tm['scene_gap']/2, 3) if prev else 0})
        L.append({'start': round(t, 3), 'end': round(t + d, 3)}); t += d + tm['gap']; prev = o['scene']
    total = round(t + tm['tail'], 3)
    for i, s in enumerate(S): s['end'] = S[i+1]['start'] if i+1 < len(S) else total
    return {'total': total, 'lines': L, 'scenes': S}

def mix(proj, d, cfg, TL, out):
    sr = 24000; N = int(TL['total'] * sr); voice = np.zeros(N)
    for i, l in enumerate(TL['lines']):
        a, r = sf.read(os.path.join(d, f'{i:02d}.wav'))
        if a.ndim > 1: a = a.mean(1)
        if r != sr: a = np.interp(np.arange(0, len(a), r/sr), np.arange(len(a)), a)
        s = int(l['start'] * sr); e = min(N, s + len(a)); voice[s:e] += a[:e-s]
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.89
    sf.write(out[:-4] + '.voice.wav', voice, sr)          # pure narration (no music/sfx), for re-editing
    out_a = voice.copy()
    mc = cfg.get('music', {'on': True, 'volume': 0.1})
    if mc.get('on', True):
        bpm = mc.get('bpm', 96); step = 60/bpm/2; tt = np.arange(int(sr*0.9))/sr
        chords = [[60,64,67,72],[57,60,64,69],[53,57,60,65],[55,59,62,67]]; music = np.zeros(N)
        def note(m, amp):
            f = 440*2**((m-69)/12); env = np.exp(-tt*5)*(1-np.exp(-tt*200))
            return amp*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt)+0.1*np.sin(6*np.pi*f*tt))
        k = 0; pos = 0.0
        while pos < TL['total']:
            ch = chords[(k//8) % 4]; m = ch[[0,2,1,3,2,1,3,2][k % 8]] + 12; s = int(pos*sr)
            for x in [note(m, .5)] + ([note(ch[0]-12, .7)] if k % 8 == 0 else []):
                e = min(N, s+len(x)); music[s:e] += x[:e-s]
            k += 1; pos += step
        music = music/np.abs(music).max()*mc.get('volume', 0.1)
        env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(sr*.3))/(sr*.3), 'same')
        music *= 1 - 0.55*np.clip(env*3, 0, 1)
        fi = int(sr*1.5); music[:fi] *= np.linspace(0, 1, fi); fo = int(sr*2.5); music[-fo:] *= np.linspace(1, 0, fo)
        out_a += music
    rng = np.random.RandomState(1)
    def sfx(kind):
        n = int(sr*0.7); x = np.arange(n)/sr
        if kind == 'shot': return 0.5*rng.randn(n)*np.exp(-x*14) + 0.8*np.sin(2*np.pi*70*x)*np.exp(-x*8)
        if kind == 'ding': return 0.35*np.exp(-x*6)*(np.sin(2*np.pi*1318*x)+0.5*np.sin(2*np.pi*1976*x))
        if kind == 'pop':  return 0.5*np.exp(-x*30)*np.sin(2*np.pi*(600+900*np.exp(-x*25))*x)
        if kind == 'whoosh': return 0.4*rng.randn(n)*np.sin(np.pi*x/0.7)**2*np.exp(-x*2)
        return np.zeros(n)
    for c in cfg.get('sfx', []):
        l = TL['lines'][c['line']]; at = c.get('at', 0)
        if isinstance(at, str) and at.startswith('end'): t0 = l['end'] + float(at[3:] or 0)
        else: t0 = l['start'] + float(at)
        x = sfx(c['type'])*0.6; s = max(0, int(t0*sr)); e = min(N, s+len(x)); out_a[s:e] += x[:e-s]
    out_a = out_a / max(1, np.abs(out_a).max()/0.97)
    sf.write(out, out_a, sr)

def cover_html(cv):
    """Title card shown for the first cover.dur seconds (also the video's first frame / thumbnail).
    script.json: "cover": {"title": "AI 只会<br>“猜下一个字”", "kicker": "…", "sub": "…", "badge": "…", "art": "<svg…>", "dur": 1.6}"""
    if not cv: return ''
    em = lambda x: re.sub(r'“([^”]+)”', r'<em>\1</em>', x)
    return ('<div id="cover"><div class="cv-rays"></div><div class="cv-dots"></div>'
            + (f'<div class="cv-badge">{cv["badge"]}</div>' if cv.get('badge') else '')
            + (f'<div class="cv-kicker">{cv["kicker"]}</div>' if cv.get('kicker') else '')
            + f'<div class="cv-title">{em(cv.get("title", ""))}</div>'
            + (f'<div class="cv-sub"><span>{cv["sub"]}</span></div>' if cv.get('sub') else '')
            + f'<div class="cv-art">{cv.get("art", "")}</div></div>')

def preview(proj, cfg, tracks, embed=True):
    head = open(os.path.join(KIT, 'base_head.html'), encoding='utf-8').read()
    tail = open(os.path.join(KIT, 'base_tail.html'), encoding='utf-8').read()
    rt = open(os.path.join(KIT, 'runtime.js'), encoding='utf-8').read()
    scenes = open(os.path.join(proj, 'scenes.html'), encoding='utf-8').read()
    extra = cfg.get('extra_css', '')
    P = {'title': cfg.get('title', ''), 'lines': cfg['lines'], 'timing': cfg['timing'], 'tracks': []}
    cv = cfg.get('cover'); P['cover'] = cv.get('dur', 1.6) if cv else 0
    for tr in tracks:
        mp3 = os.path.join(proj, 'build', tr['id'] + '.mp3')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(proj, 'build', tr['id'] + '.wav'), '-ac', '1', '-b:a', '96k', mp3], check=True)
        audio = ('data:audio/mpeg;base64,' + base64.b64encode(open(mp3, 'rb').read()).decode()) if embed else tr['id'] + '.mp3'
        P['tracks'].append({'id': tr['id'], 'name': tr['name'], 'audio': audio, 'timeline': tr['timeline']})
    html = (head.replace('{{TITLE}}', cfg.get('title', '')).replace('{{BADGE}}', cfg.get('badge', '漫画科普')).replace('{{EXTRA_CSS}}', extra)
            + scenes + tail.replace('{{COVER}}', cover_html(cv)).replace('{{FOOTER}}', cfg.get('footer', '')).replace('{{SOURCES}}', cfg.get('sources', '')).replace('{{WATERMARK}}', cfg.get('watermark', ''))
            + '<script>window.PROJECT=' + json.dumps(P, ensure_ascii=False) + ';</script>\n<script>' + rt + '</script>\n</body></html>')
    out = os.path.join(proj, 'build', 'preview.html'); open(out, 'w', encoding='utf-8').write(html); return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('--voice', action='append', default=[])
    ap.add_argument('--no-embed', action='store_true'); ap.add_argument('--drop', action='append', default=[]); a = ap.parse_args()
    proj = os.path.abspath(a.proj); cfg = json.load(open(os.path.join(proj, 'script.json'), encoding='utf-8'))
    cfg.setdefault('timing', {'pre': .8, 'gap': .28, 'scene_gap': .7, 'tail': 3.0})
    if cfg.get('cover'): cfg['timing']['pre'] = max(cfg['timing']['pre'], cfg['cover'].get('dur', 1.6) + 0.5)   # first line starts after the cover
    os.makedirs(os.path.join(proj, 'build'), exist_ok=True)
    reg_f = os.path.join(proj, 'build', 'voices.json'); reg = json.load(open(reg_f)) if os.path.exists(reg_f) else []
    specs = [(r['spec'], r['name']) for r in reg]
    for v in a.voice:
        sp, nm = (v.split('=', 1) + [v])[:2]
        specs = [x for x in specs if x[0] != sp] + [(sp, nm)]
    for sp in a.drop: specs = [x for x in specs if x[0] != sp]
    tracks = []
    for spec, name in specs:
        d, durs = synth_lines(proj, spec, cfg['lines']); TL = timeline(cfg['lines'], durs, cfg['timing']); i = vid(spec)
        mix(proj, d, cfg, TL, os.path.join(proj, 'build', i + '.wav'))
        json.dump(TL, open(os.path.join(proj, 'build', i + '.timeline.json'), 'w'), indent=1)
        tracks.append({'id': i, 'name': name, 'spec': spec, 'timeline': TL}); print(f'[build] {name}: {TL["total"]:.1f}s')
    json.dump([{'spec': t['spec'], 'name': t['name'], 'id': t['id']} for t in tracks], open(reg_f, 'w'), ensure_ascii=False, indent=1)
    print('[build] preview ->', preview(proj, cfg, tracks, not a.no_embed))

if __name__ == '__main__': main()
````

### kit/render.py
````python
"""Render MP4 (1080x1920) or a contact sheet from build/preview.html.
usage:
  python render.py <project_dir> --voice <trackId|spec|name> [--fps 30] [--workers N] [--start S --end E] [--out file.mp4]
  python render.py <project_dir> --sheet          # PNG contact sheet: last frame of every scene (layout check)
  python render.py <project_dir> --at 12.5 40     # single frames as PNG
  python render.py <project_dir> --cover          # cover.png 1080x1920 (the title card, for platform upload)
  python render.py <project_dir> --voice <id> --audio my_full.m4a --offset 0.3   # your own full-length recording on that voice's timeline
Needs: pip install playwright && playwright install chromium ; ffmpeg on PATH."""
import os, sys, json, argparse, asyncio, subprocess, shutil, re, multiprocessing as mp

def vid(spec): return re.sub(r'[^A-Za-z0-9_-]+', '_', spec).strip('_')

async def _frames(url, times, outdir, scale=2, fmt='jpeg'):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 540, 'height': 960}, device_scale_factor=scale)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(url); await pg.wait_for_function('window.READY===true', timeout=120000)
        await pg.evaluate('document.fonts.ready')
        for name, t in times:
            await pg.evaluate(f'seek({t})')
            kw = {'type': 'jpeg', 'quality': 92} if fmt == 'jpeg' else {'type': 'png'}
            await pg.screenshot(path=os.path.join(outdir, name), **kw)
        await b.close()
        if errs: print('page errors:', errs, file=sys.stderr)

def _worker(args): asyncio.run(_frames(*args))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('--voice'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--workers', type=int, default=max(1, min(8, os.cpu_count() or 2))); ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float); ap.add_argument('--out'); ap.add_argument('--sheet', action='store_true'); ap.add_argument('--at', type=float, nargs='*'); ap.add_argument('--cover', action='store_true', help='save cover.png (1080x1920, frame at t=0)')
    ap.add_argument('--audio', help='use your own full recording instead of the voice track'); ap.add_argument('--offset', type=float, default=0, help='seconds; + = audio starts later')
    a = ap.parse_args(); proj = os.path.abspath(a.proj); bd = os.path.join(proj, 'build')
    reg = json.load(open(os.path.join(bd, 'voices.json')))
    tr = next((r for r in reg if a.voice in (r['id'], r['spec'], r['name'])), reg[0]) if a.voice else reg[0]
    TL = json.load(open(os.path.join(bd, tr['id'] + '.timeline.json')))
    url = 'file://' + os.path.join(bd, 'preview.html') + f'?render=1&voice={tr["id"]}'
    def save_cover():
        od = os.path.join(bd, 'snap_cover'); os.makedirs(od, exist_ok=True)
        asyncio.run(_frames(url, [('cover.png', 0.0)], od, scale=2, fmt='png'))
        shutil.move(os.path.join(od, 'cover.png'), os.path.join(bd, 'cover.png')); shutil.rmtree(od); return os.path.join(bd, 'cover.png')
    if a.cover:
        print(save_cover()); return
    if a.sheet or a.at is not None:
        from PIL import Image
        times = [(f's_{i:02d}.png', s['end'] - 0.3) for i, s in enumerate(TL['scenes'])] if a.sheet else [(f'at_{t:07.2f}.png', t) for t in a.at]
        od = os.path.join(bd, 'snap'); shutil.rmtree(od, ignore_errors=True); os.makedirs(od)
        asyncio.run(_frames(url, times, od, scale=1, fmt='png'))
        if a.sheet:
            ims = [Image.open(os.path.join(od, n)) for n, _ in times]; cols = 5; rows = (len(ims)+cols-1)//cols
            sh = Image.new('RGB', (540*cols, 960*rows), 'white')
            for i, im in enumerate(ims): sh.paste(im, ((i % cols)*540, (i//cols)*960))
            sh.save(os.path.join(bd, 'sheet.png')); print(os.path.join(bd, 'sheet.png'))
        else: print(od)
        return
    end = min(a.end or TL['total'], TL['total']); n0 = int(a.start*a.fps); n1 = int(end*a.fps)
    fd = os.path.join(bd, 'frames'); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
    allt = [(f'{f-n0:06d}.jpg', f/a.fps) for f in range(n0, n1)]
    jobs = [(url, allt[w::a.workers], fd) for w in range(a.workers)]
    print(f'[render] {tr["name"]}: {len(allt)} frames, {a.workers} workers ...', flush=True)
    with mp.Pool(a.workers) as pool: pool.map(_worker, jobs)
    out = a.out or os.path.join(bd, f'{tr["id"]}.mp4')
    aud = a.audio or os.path.join(bd, tr['id'] + '.wav')
    if not os.path.exists(aud): aud = os.path.join(bd, tr['id'] + '.mp3')
    af = (f'atrim=start={-a.offset},asetpts=PTS-STARTPTS,' if a.offset < 0 else '') + \
         (f'adelay={int(a.offset*1000)}:all=1,' if a.offset > 0 else '') + \
         f'apad,atrim=start={a.start}:end={end},asetpts=PTS-STARTPTS'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', os.path.join(fd, '%06d.jpg'),
                    '-i', aud, '-af', af,
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', '-movflags', '+faststart', out], check=True)
    cv = save_cover(); tmp = out[:-4] + '.tmp.mp4'      # embed cover.png as the MP4 thumbnail (Finder / players / some platforms)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-i', cv, '-map', '0', '-map', '1', '-c', 'copy', '-c:v:1', 'mjpeg',
                    '-disposition:v:1', 'attached_pic', '-movflags', '+faststart', tmp], check=True); os.replace(tmp, out)
    shutil.rmtree(fd); print('[render] ->', out)

if __name__ == '__main__': main()
````

### kit/pack.py
````python
"""Package a comic-video project into one zip, INCLUDING all generated voice audio.
usage: python pack.py <project_dir> [--out 项目包.zip] [--mp4 build/xxx.mp4 ...]
Zip layout:
  README.md, kit/*                               tools
  proj/script.json, proj/scenes.html             sources
  proj/build/preview.html, voices.json, *.timeline.json, <id>.mp3 (full mix, used by render.py)
  proj/build/voices/<id>/meta.json               build cache index -> points at 配音/<名称>/逐句/*.mp3 (no re-synthesis)
  配音/<名称>/完整配音_含音乐.mp3                   full track with music + sfx (what the video uses)
  配音/<名称>/纯人声.mp3                           narration only, same timing (for re-editing / 剪映)
  配音/<名称>/字幕.srt                             subtitles on that voice's timing
  配音/<名称>/逐句/01_台词开头.mp3 ...               one clip per line
  视频/*.mp4                                     rendered videos passed with --mp4
Keeps the zip small (mp3, mono) so it stays under upload limits."""
import os, sys, json, re, argparse, subprocess, zipfile, tempfile, shutil
KIT = os.path.dirname(os.path.abspath(__file__))

def mp3(src, dst, br='64k'):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-b:a', br, dst], check=True)

def srt_time(x):
    ms = int(round(x * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'

def safe(s, n=12):
    s = re.sub(r'<[^>]+>', '', s); s = re.sub(r'[\\/:*?"<>|\s，。！？、：；…“”—（）()]+', '', s); return s[:n]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('--out'); ap.add_argument('--mp4', nargs='*', default=[])
    a = ap.parse_args(); proj = os.path.abspath(a.proj); bd = os.path.join(proj, 'build')
    cfg = json.load(open(os.path.join(proj, 'script.json'), encoding='utf-8')); lines = cfg['lines']
    reg = json.load(open(os.path.join(bd, 'voices.json'), encoding='utf-8'))
    title = safe(cfg.get('title', 'project'), 30) or 'project'
    out = a.out or os.path.join(os.path.dirname(proj), f'{title}_项目包.zip')
    tmp = tempfile.mkdtemp(); root = os.path.join(tmp, title)
    def add(src, rel):
        dst = os.path.join(root, rel); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst)
    for f in os.listdir(KIT):
        if f.endswith(('.py', '.js', '.html')): add(os.path.join(KIT, f), 'kit/' + f)
    if os.path.exists(os.path.join(KIT, 'README.md')): add(os.path.join(KIT, 'README.md'), 'README.md')
    for f in os.listdir(KIT):
        if f.endswith('.command'): add(os.path.join(KIT, f), f); os.chmod(os.path.join(root, f), 0o755)
    if os.path.exists(os.path.join(KIT, 'env.example')): add(os.path.join(KIT, 'env.example'), '.env.example')
    for f in ('script.json', 'scenes.html'): add(os.path.join(proj, f), 'proj/' + f)
    for f in ['preview.html', 'voices.json'] + [r['id'] + '.timeline.json' for r in reg]: add(os.path.join(bd, f), 'proj/build/' + f)
    for r in reg:
        vid, name = r['id'], safe(r['name'], 20) or r['id']
        TL = json.load(open(os.path.join(bd, vid + '.timeline.json')))
        vdir = os.path.join(bd, 'voices', vid); meta = os.path.join(vdir, 'meta.json')
        full = os.path.join(root, 'proj/build', vid + '.mp3'); mp3(os.path.join(bd, vid + '.wav'), full, '96k')
        human = os.path.join(root, '配音', name); os.makedirs(os.path.join(human, '逐句'), exist_ok=True)
        shutil.copy(full, os.path.join(human, '完整配音_含音乐.mp3'))
        vw = os.path.join(bd, vid + '.voice.wav')
        if os.path.exists(vw): mp3(vw, os.path.join(human, '纯人声.mp3'), '96k')
        # per-line clips live once, in 配音/<名称>/逐句/ ; meta.json (build cache) points there -> no re-synthesis after unzip
        m = json.load(open(meta)); os.makedirs(os.path.join(root, f'proj/build/voices/{vid}'), exist_ok=True)
        for i, o in enumerate(lines):
            fn = f'{i+1:02d}_{safe(o["sub"])}.mp3'; mp3(os.path.join(vdir, f'{i:02d}.wav'), os.path.join(human, '逐句', fn))
            if str(i) in m: m[str(i)]['mp3'] = f'../../../../配音/{name}/逐句/{fn}'
        json.dump(m, open(os.path.join(root, f'proj/build/voices/{vid}/meta.json'), 'w'), ensure_ascii=False)
        with open(os.path.join(human, '字幕.srt'), 'w', encoding='utf-8') as f:
            for i, o in enumerate(lines):
                s = TL['lines'][i]['start']; e = TL['lines'][i]['end']
                e = min(TL['lines'][i+1]['start'], e + 0.6) if i + 1 < len(lines) else e + 1
                f.write(f'{i+1}\n{srt_time(s)} --> {srt_time(e)}\n{re.sub(r"<[^>]+>", "", o["sub"])}\n\n')
    with open(os.path.join(root, '配音', '台词.txt'), 'w', encoding='utf-8') as f:
        for i, o in enumerate(lines): f.write(f'{i+1:02d} [{o["scene"]}] {re.sub(r"<[^>]+>", "", o["sub"])}\n')
    for m in a.mp4: add(m, '视频/' + os.path.basename(m))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for dp, _, fs in os.walk(root):
            for f in fs: p = os.path.join(dp, f); z.write(p, os.path.relpath(p, tmp))
    shutil.rmtree(tmp); print(f'[pack] -> {out}  ({os.path.getsize(out)/1e6:.1f} MB)')

if __name__ == '__main__': main()
````

### kit/edge_batch.py
````python
"""Batch-generate Microsoft Edge neural voices (https://github.com/rany2/edge-tts) for a project, one mp3 per line.
Runs on YOUR computer (needs internet access to speech.platform.bing.com; cloud sandboxes usually block it).
usage: python edge_batch.py <project_dir> zh-CN-XiaoxiaoNeural zh-CN-YunxiNeural [--rate 1.1] [--pitch +0Hz] [--volume +0%]
output: <project_dir>/edge_voices/<voice>/01.mp3 02.mp3 ...   (only changed lines are regenerated)
then:   python build.py <project_dir> --voice "files:<project_dir>/edge_voices/zh-CN-XiaoxiaoNeural=晓晓（Edge）"
        (or hand the folder back to Claude, which runs build/render for you)"""
import os, sys, json, re, argparse, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tts

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('voices', nargs='+')
    ap.add_argument('--rate', type=float, default=1.1); ap.add_argument('--pitch', default='+0Hz'); ap.add_argument('--volume', default='+0%')
    a = ap.parse_args(); proj = os.path.abspath(a.proj)
    lines = json.load(open(os.path.join(proj, 'script.json'), encoding='utf-8'))['lines']
    for v in a.voices:
        d = os.path.join(proj, 'edge_voices', v); os.makedirs(d, exist_ok=True)
        mf = os.path.join(d, 'texts.json'); done = json.load(open(mf, encoding='utf-8')) if os.path.exists(mf) else {}
        print(f'== {v}  语速 {a.rate}  ({len(lines)} 句)', flush=True)
        for i, o in enumerate(lines):
            text = tts.clean(o.get('say') or re.sub(r'<[^>]+>', '', o['sub']))
            key = hashlib.md5(f'{text}|{a.rate}|{a.pitch}|{a.volume}'.encode()).hexdigest()
            out = os.path.join(d, f'{i+1:02d}.mp3')
            if done.get(str(i)) == key and os.path.exists(out) and os.path.getsize(out) > 0: continue
            tts._edge(text, f'{v}|{a.pitch}|{a.volume}', a.rate, out)
            done[str(i)] = key; json.dump(done, open(mf, 'w', encoding='utf-8'), ensure_ascii=False)
            print(f'  {i+1:02d}/{len(lines)} {text[:30]}', flush=True)
    print('\n完成：', os.path.join(proj, 'edge_voices'))

if __name__ == '__main__': main()
````

### kit/gen_edge_mixed.py
````python
"""中英混合 Edge 配音（英语学习类视频）：普通句用中文声音，script.json 里标了 "en": true 的句子用英语母语声音。
usage: python kit/gen_edge_mixed.py proj [--pair 中文声音:英文声音 ...] [--zh-rate 1.1] [--en-rate 0.92]
默认两套：晓晓+Jenny、云希+Guy。输出 proj/edge_voices/<中文声音>/01.mp3 …，再按 files: 方式 build。逐句缓存，改台词只重配改动的句子。"""
import os, sys, json, re, hashlib, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tts
ap = argparse.ArgumentParser(); ap.add_argument('proj')
ap.add_argument('--pair', action='append', help='zh-CN-XiaoxiaoNeural:en-US-JennyNeural')
ap.add_argument('--zh-rate', type=float, default=1.1); ap.add_argument('--en-rate', type=float, default=0.92)
a = ap.parse_args()
pairs = [p.split(':') for p in (a.pair or ['zh-CN-XiaoxiaoNeural:en-US-JennyNeural', 'zh-CN-YunxiNeural:en-US-GuyNeural'])]
lines = json.load(open(os.path.join(a.proj, 'script.json'), encoding='utf-8'))['lines']
for zh, en in pairs:
    d = os.path.join(a.proj, 'edge_voices', zh); os.makedirs(d, exist_ok=True)
    mf = os.path.join(d, 'texts.json'); done = json.load(open(mf, encoding='utf-8')) if os.path.exists(mf) else {}
    for i, o in enumerate(lines):
        text = tts.clean(o.get('say') or re.sub(r'<[^>]+>', '', o['sub']))
        v, r = (en, a.en_rate) if o.get('en') else (zh, a.zh_rate)
        key = hashlib.md5(f'{text}|{v}|{r}'.encode()).hexdigest(); out = os.path.join(d, f'{i+1:02d}.mp3')
        if done.get(str(i)) == key and os.path.exists(out) and os.path.getsize(out) > 0: continue
        tts._edge(text, f'{v}|+0Hz|+0%', r, out); done[str(i)] = key
        json.dump(done, open(mf, 'w', encoding='utf-8'), ensure_ascii=False); print(zh, i + 1, text[:30], flush=True)
````

### kit/render_resume.py
````python
"""可断点续跑的渲染（单核/有单次命令时限的环境用；render.py 一口气渲染可能被杀掉）。
usage: python kit/render_resume.py proj --voice <id|名称> [--budget 250] [--upload]
每次运行最多截帧 budget 秒，已截的帧会跳过；反复运行直到打印 DONE（帧齐后自动合成 MP4 并写入封面缩略图）。
先跑 render.py --cover 生成 build/cover.png（会写入缩略图）。输出 proj/build/<id>.mp4；--upload 另出 <id>_upload.mp4（≤9.5MB，给 Claude in Chrome 上传工具用，单次上限 10MB）。"""
import os, sys, json, asyncio, time, argparse, subprocess, shutil
ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('--voice', required=True)
ap.add_argument('--budget', type=float, default=250); ap.add_argument('--upload', action='store_true'); a = ap.parse_args()
bd = os.path.abspath(os.path.join(a.proj, 'build')); fps = 30
reg = json.load(open(f'{bd}/voices.json', encoding='utf-8'))
tr = next((r for r in reg if a.voice in (r['id'], r['name'], r['spec'])), None) or sys.exit('voice not found: ' + a.voice)
TL = json.load(open(f'{bd}/{tr["id"]}.timeline.json', encoding='utf-8'))
fd = f'{bd}/frames_{tr["id"]}'; os.makedirs(fd, exist_ok=True); N = int(TL['total'] * fps)
todo = [f for f in range(N) if not os.path.exists(f'{fd}/{f:06d}.jpg')]
print('frames', N, 'remaining', len(todo), flush=True)
async def grab():
    from playwright.async_api import async_playwright
    t0 = time.time(); n = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 540, 'height': 960}, device_scale_factor=2)
        await pg.goto('file://' + bd + '/preview.html?render=1&voice=' + tr['id'])
        await pg.wait_for_function('window.READY===true', timeout=120000); await pg.evaluate('document.fonts.ready')
        for f in todo:
            if time.time() - t0 > a.budget: break
            await pg.evaluate(f'seek({f / fps})'); tmp = f'{fd}/tmp.jpg'
            await pg.screenshot(path=tmp, type='jpeg', quality=92); os.replace(tmp, f'{fd}/{f:06d}.jpg'); n += 1
        await b.close()
    print('grabbed', n, 'in', round(time.time() - t0), 's', flush=True)
if todo: asyncio.run(grab())
if any(not os.path.exists(f'{fd}/{f:06d}.jpg') for f in range(N)): sys.exit(print('NOT DONE — run again'))
def ff(*args): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)
end = f'{N / fps:.3f}'; out = f'{bd}/{tr["id"]}.mp4'; tmp = f'{bd}/_tmp.mp4'; cover = f'{bd}/cover.png'
ff('-framerate', str(fps), '-i', f'{fd}/%06d.jpg', '-i', f'{bd}/{tr["id"]}.wav', '-af', f'apad,atrim=start=0:end={end},asetpts=PTS-STARTPTS',
   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', tmp)
def with_cover(src, dst):
    if os.path.exists(cover):
        ff('-i', src, '-i', cover, '-map', '0', '-map', '1', '-c', 'copy', '-c:v:1', 'mjpeg', '-disposition:v:1', 'attached_pic', '-movflags', '+faststart', dst); os.remove(src)
    else: shutil.move(src, dst)
if a.upload and os.path.getsize(tmp) <= 9.5 * 1024 * 1024:   # 原片已够小：直接复制一份当上传版
    shutil.copy(tmp, f'{bd}/_up.mp4'); with_cover(f'{bd}/_up.mp4', f'{bd}/{tr["id"]}_upload.mp4')
elif a.upload:   # 目标 ≤9.5MB：按时长算码率
    vk = max(200, int(9.5 * 8 * 1024 / (N / fps)) - 96 - 20)
    ff('-i', tmp, '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', f'{vk}k', '-maxrate', f'{int(vk*1.35)}k',
       '-bufsize', f'{vk*3}k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', f'{bd}/_up.mp4')
    with_cover(f'{bd}/_up.mp4', f'{bd}/{tr["id"]}_upload.mp4')
with_cover(tmp, out); shutil.rmtree(fd); print('DONE', out)
````

### kit/safe_check.py
````python
"""把手机平台的遮挡区画到截图上，检查关键内容有没有被挡（舞台坐标 540×960）。
usage: python kit/safe_check.py proj/build/snap/at_0030.00.png [out.jpg]
红：状态栏/顶部按钮(0–86)、底部简介与按钮(780+)、iPhone 等长屏左右裁切(各25)；橙：小红书/Shorts 右侧按钮(x>465, y 470–780)。"""
import sys
from PIL import Image, ImageDraw
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit('.', 1)[0] + '_safe.jpg'
im = Image.open(src).convert('RGBA'); W, H = im.size; s = W / 540
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); red = (255, 0, 0, 70)
d.rectangle([0, 0, W, 86 * s], fill=red); d.rectangle([0, 780 * s, W, H], fill=red)
d.rectangle([0, 0, 25 * s, H], fill=red); d.rectangle([W - 25 * s, 0, W, H], fill=red)
d.rectangle([W - 75 * s, 470 * s, W, 780 * s], fill=(255, 120, 0, 70))
Image.alpha_composite(im, ov).convert('RGB').save(out, quality=88); print(out)
````

### kit/polyphone_check.py
````python
"""上线前扫多音字：列出台词（优先 say）里 TTS 容易读错的多音字，附 pypinyin 按上下文猜的读音，供人工判断。
usage: python kit/polyphone_check.py proj      (需要 pip install pypinyin)
读错时不改字幕，只在该句加 "say"，把多音字换成同音字，例如：
  调 tiáo→条（调一调/调教/调整）  长 zhǎng→掌（长这样/长大）  行 háng→航（排行/银行）  重 chóng→虫（重新/重复）
  还 huán→环（还书）  觉 jiào→叫（睡觉）  数 shǔ→属（数一数）  得 děi→（换说法“必须”）  地 de 一般不用改
改完重跑 Edge 配音（只重配改动的句子）→ build。"""
import sys, os, json, re
from pypinyin import pinyin, Style
RISK = set('调长还行重数觉得弹处种降藏传冲当干假将教卷空乐累率模宁强曲塞散省盛似宿吐吓兴血载扎涨曾差朝称乘奇缝供恶背薄剥参创')
L = json.load(open(os.path.join(sys.argv[1], 'script.json'), encoding='utf-8'))['lines']
n = 0
for i, o in enumerate(L):
    t = o.get('say') or re.sub(r'<[^>]+>', '', o['sub'])
    hits = [(j, c) for j, c in enumerate(t) if c in RISK]
    if not hits: continue
    py = pinyin(t, style=Style.TONE, errors=lambda x: [[c] for c in x])
    flat = [p[0] for p in py]
    ctx = '  '.join(f"{c}={flat[j] if j < len(flat) else '?'}" for j, c in hits)
    print(f'{i+1:02d}  {ctx}\n    {t}'); n += 1
print(f'— {n} 句含易错多音字；逐个对照语境，读音不对的句子加 "say"。')
````

### kit/一键生成Edge配音.command
````bash
#!/bin/bash
# 双击运行（macOS）：用微软 Edge 神经网络语音（edge-tts）为本项目逐句生成配音。只需 Python3 + 联网。
cd "$(dirname "${BASH_SOURCE[0]}")"
VENV="$HOME/.cache/comic-video/venv"
PY=$(command -v python3) || { echo "需要 Python3：终端运行 xcode-select --install 或 brew install python 后再试"; read -p "按回车关闭"; exit 1; }
[ -x "$VENV/bin/python" ] || "$PY" -m venv "$VENV" || exit 1
echo "准备 edge-tts ..."; "$VENV/bin/pip" install -q --upgrade pip edge-tts || { read -p "安装失败，按回车关闭"; exit 1; }
echo; echo "可用的普通话声音："; "$VENV/bin/python" kit/tts.py --list-edge zh-CN
DEF="zh-CN-XiaoxiaoNeural zh-CN-YunxiNeural"
echo; read -p "要生成哪些声音（空格分隔，回车=默认 $DEF）：" VOICES; VOICES=${VOICES:-$DEF}
read -p "语速（1.0=原速，回车=1.1）：" RATE; RATE=${RATE:-1.1}
"$VENV/bin/python" kit/edge_batch.py proj $VOICES --rate "$RATE" || { read -p "生成失败，按回车关闭"; exit 1; }
echo; echo "✅ 完成！配音在 proj/edge_voices/ 。"
echo "回到 Claude 对话说一声“Edge 配音好了”，我会用它生成新的预览和视频。"
read -p "按回车关闭"
````

### kit/env.example
````bash
MINIMAX_API_KEY=
# 国内账号取消下一行注释
# MINIMAX_API_HOST=https://api.minimaxi.com
LISTENHUB_API_KEY=
````

### kit/README.md
````markdown
# 漫画风竖屏科普视频工具包

```
kit/                     通用工具
  base_head.html         漫画样式 + 角色/道具 SVG（机器人 astra、小孩 kid、假发学者 wig、靶子、准星、爆炸框、狙击枪）
  base_tail.html         字幕框、页脚
  runtime.js             时间轴动画引擎 + 预览播放器
  tts.py                 配音引擎（可插拔）
  build.py               生成配音、时间轴、预览页 build/preview.html
  render.py              渲染 MP4 / 检查用拼图
  pack.py                打包项目（含全部生成的配音）
proj/                    一个视频 = 一个项目
  script.json            台词（唯一需要改文案的地方）
  scenes.html            画面（每个场景一个 .scene）
  build/                 生成物（可删，除 voices 缓存）
```

## 环境（本机运行时）
```bash
pip install sherpa-onnx soundfile numpy pillow playwright edge-tts
playwright install chromium        # 以及系统里要有 ffmpeg
```

## 微软 Edge 配音（推荐）
Claude 的云端环境连不上微软语音服务。若在 Cowork 网络设置里放行了 `speech.platform.bing.com`，Claude 可以在你电脑上的 Cowork 环境里直接生成；否则在你的电脑上生成：
1. 双击项目根目录的 **`一键生成Edge配音.command`**（首次会自动建虚拟环境并安装 edge-tts；只需要 Python3 和网络）。
2. 按提示选声音（默认晓晓 + 云希）和语速，逐句生成到 `proj/edge_voices/<声音>/01.mp3…`，改台词后再跑只重做改动的句子。
3. 回到 Claude 说“Edge 配音好了”，由 Claude 生成预览和视频；或自己运行
   `python kit/build.py proj --voice "files:proj/edge_voices/zh-CN-XiaoxiaoNeural=晓晓（Edge）"`。
   已装齐依赖时也可以直接：`python kit/build.py proj --voice "edge:zh-CN-XiaoxiaoNeural@1.1=晓晓"`。
> 首次双击若提示“无法验证开发者”：右键 → 打开；或终端里 `chmod +x 一键生成Edge配音.command`。

## 封面
`script.json` 里加 `"cover": {"title": "其实只会<br>“猜下一个字”", "kicker": "你每天用的 ChatGPT", "sub": "3 分钟看懂大语言模型", "badge": "AI 漫画科普", "art": "<div …>可放角色/气泡</div>", "dur": 1.6}`：
视频开头先显示 1.6 秒封面（第一帧就是封面，页内录制的视频也一样），正片自动顺延。
`python kit/render.py proj --cover` 导出 `build/cover.png`（1080×1920，发布时上传为封面）；高清渲染的 MP4 会自动把封面写进文件缩略图。

## 在预览页里出视频
- **● 录制视频**：在 Chrome / Edge 中打开 preview.html → 选好配音 → 点“录制视频”→ 弹窗里选“此标签页”并共享。会从头实时播放并只录下竖屏画面区域，播完自动下载（Chrome 为 MP4，其他为 WebM）。分辨率 = 画面在屏幕上的实际像素（Mac Retina 屏上把窗口拉高即可接近 1080×1920），录制时保持标签页在前台。
- **高清渲染 1080×1920…**：逐帧渲染、画质最好。点按钮会复制一句话，粘贴给 Claude 即可；或自己运行 `python kit/render.py proj --voice "晓晓（微软 Edge）"`。

## 用自己的配音（预览页里操作）
- **逐句文件**：点“导入我的配音…”，一次选中多条录音，文件名以句子序号开头：`01.mp3`、`02.m4a`……（序号见“导出台词”）。也可以直接选一个 zip（本页导出的那种）。
  时间轴会按你每句的实际长度重排，画面自动对齐；首尾静音会自动裁掉。
- **网页里逐句录音**：点“逐句录音”→ 看着提词区读，● 录制 / ■ 停止，自动跳下一句，可试听、重录。需在 Chrome/Edge 中打开并允许麦克风。
- **整段录音**：只选一个文件（文件名不以数字开头）即按整段处理，画面沿用内置配音的时间轴，用“偏移”滑块对齐。
- **出视频**：逐句方式点“导出我的配音 ZIP”，解压到 `proj/my_voice/`：
  `python kit/build.py proj --voice "files:proj/my_voice=我的配音"` → `python kit/render.py proj --voice 我的配音`
  整段方式：`python kit/render.py proj --voice <内置配音id> --audio 我的录音.m4a --offset 0.3`

## 常用流程
```bash
# 1) 生成配音 + 预览（可同时生成多种声音，预览里下拉切换）
python kit/build.py proj --voice "kokoro:4@1.25=离线女声" --voice "edge:zh-CN-YunxiNeural@1.1=云希"
#    → 用浏览器打开 proj/build/preview.html：拖动进度条、点场景跳转、切换配音、导出台词/SRT

# 2) 确认没问题后渲染
python kit/render.py proj --voice edge_zh-CN-YunxiNeural_1_1      # 用 voices.json 里的 id / spec / 名称都行
python kit/render.py proj --voice 云希 --start 60 --end 80         # 只渲染一段试看
python kit/render.py proj --sheet                                  # 每个场景最后一帧拼成一张图
python kit/pack.py proj --mp4 proj/build/xxx.mp4                   # 打包：工具+项目+全部配音（完整/纯人声/逐句/SRT）+视频
```
改了 `script.json` 台词后重跑第 1 步：只有改动的句子会重新配音（按句缓存）。只改 `scenes.html` 画面时也重跑第 1 步（很快）。

## 配音引擎（--voice 的写法，`@1.2` 为语速，`=名字` 为显示名）
| 写法 | 说明 |
|---|---|
| `kokoro:<编号>` | 离线，免费。4 = 女声，60 = 男声（共 103 个音色，3–57 为中文女声，58 以后多为中文男声）。首次自动下载模型约 350MB |
| `melo` | 离线，音色较机械 |
| `edge:zh-CN-XiaoxiaoNeural` | 微软 Edge 神经网络语音（[edge-tts](https://github.com/rany2/edge-tts)），免费、质量最好，需联网。常用：Xiaoxiao 晓晓、Yunxi 云希、Yunjian 云健、Xiaoyi 晓伊、Yunyang 云扬；台湾 zh-TW-HsiaoChenNeural。可带音调/音量：`edge:zh-CN-YunxiNeural\|+5Hz\|+10%@1.1`；列出全部声音：`python kit/tts.py --list-edge zh` |
| `minimax:<voice_id>` | [MiniMax 语音](https://platform.minimax.io/docs/api-reference/speech-t2a-http)（T2A v2，默认模型 speech-2.8-hd），需 `MINIMAX_API_KEY`。可带情绪：`minimax:presenter_female\|happy@1.1`；国内账号设 `MINIMAX_API_HOST=https://api.minimaxi.com`；列出声音：`python kit/tts.py --list-minimax` |
| `listenhub:<speakerId>` | [ListenHub](https://listenhub.ai/docs/zh/openapi/api-reference/flowspeech) 同步 TTS，需 `LISTENHUB_API_KEY`；列出中文声音：`python kit/tts.py --list-listenhub zh` |
| `flowspeech:<speakerId>` | ListenHub FlowSpeech（异步 direct 模式，逐句并行提交，每句约 1–2 分钟；少于 10 字的句子自动改走同步 TTS，同一音色） |
| `say:Tingting` | macOS 自带语音 |
| `openai:alloy` | 需要 `OPENAI_API_KEY`；可设 `OPENAI_TTS_INSTRUCTIONS` 控制语气 |
| `files:我的录音目录` | 自己录：按句子编号放 `01.wav`、`02.m4a`……（编号见预览页“导出台词”）|

**API Key 放哪里**：环境变量，或在项目根目录新建 `.env` 文件（不要发给别人）：
```
MINIMAX_API_KEY=...
LISTENHUB_API_KEY=...
```
读音不对时，在 `script.json` 那一句加 `"say": "念法"`（字幕仍显示 `sub`），例如 `"sub":"GPT-6 Astra","say":"G P T 6 Astra"`。

## 手机安全区 / 断点渲染 / 中英配音
- 版式默认避开手机平台遮挡（顶部状态栏、底部简介、右侧按钮）；检查：`python kit/safe_check.py proj/build/snap/at_0030.00.png`。
- 电脑配置低或渲染中途被打断：反复运行 `python kit/render_resume.py proj --voice 晓晓（微软 Edge） --upload` 直到显示 DONE。
- 多音字读错：`python kit/polyphone_check.py proj` 找出来，在那一句加 `"say"`（同音字替换，字幕不变），再重新生成配音。
- 英语学习类视频（台词里有 `"en": true` 的句子）：`python kit/gen_edge_mixed.py proj` 生成中英混合配音。
````