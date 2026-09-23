# 配音工具与选择

## 工具用法

`scripts/narrate.py` 默认使用 ListenHub 云端引擎（`--engine listenhub`，需要 `LISTENHUB_API_KEY`，见下文），也可用无需密钥的 Edge TTS（`--engine edge-tts`）或本地离线的 Kokoro（`--engine kokoro`）。三种引擎输出同一种目录结构和 `manifest.json`，模板不区分引擎。需要 Python 3.10+ 和 PATH 中的 `ffmpeg` / `ffprobe`；ListenHub 只用标准库，Edge 需要 `edge-tts`。使用独立虚拟环境，避免改系统 Python。此工具已用 edge-tts 7.2.8 验证；实际生成前会查询当前可用音色。

```sh
python -m venv work/tts-env
work/tts-env/bin/python -m pip install 'edge-tts>=7.2.8,<8'
work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py --list-voices
```

输入 JSON（UTF-8）：

```json
{"scenes": [
  {"id": "hook", "text": "把这四块三角形挪一挪，空白部分的总面积会变大吗？先猜一下。", "pauseAfter": 1.5},
  {"id": "reveal", "text": "外框没变，四块三角形也没变。所以，空白的总面积没有变。"}
]}
```

`pauseAfter` 是可选的场景末思考停顿（秒），会计入该场景的 `durationFrames`、后续场景起点和 `captions.srt`；提问场景用它，不要另写脚本改时间线。为试听只提供一个短场景；完整旁白提供多个场景。使用同一份文字比较音色，若同时改了讲稿要明确说明。

```sh
work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py \
  --engine edge-tts --input work/narration.json --out work/narration \
  --voice yunxi --voice xiaoyi --rate=+0% --fps 30
```

输出目录需为新目录或空目录，避免旧时间线混用新音频。每个场景失败时自动重试 3 次（2、4 秒退避），最终失败会保留已完成片段、删除空的音色目录并以一行 `Error:` 说明；用新的工作目录重跑。结果包含每种音色的场景 MP3、原始句子边界、独立的 `captions.srt`，以及总 `manifest.json`。路径相对于 manifest。每个场景完整合成，起止帧由真实音频时长计算，默认前后各留 0.25 秒，再加该场景的 `pauseAfter`。单次合成尝试超过 `--timeout`（默认 60 秒）会中止并重试，避免无输出挂死。结果不包含完整混音或视频；在 Remotion 中根据场景 `audioStartFrame` 放置音频。

Edge 的句子边界来自服务，ListenHub 和 Kokoro 的句子边界由脚本按句拼接时计算；都只到句子一级，是字幕和动画定位的起点，不保证与人为划分的字幕段数一致。句内没有更细的时间信息，较长句要拆成两条字幕时按语义拆，并在讲稿里直接写成两句让服务分别返回边界；不能假定字数均匀对应时间。显示公式与口播文字不一致时，编辑显示字幕并保留时间信息。

## ListenHub 云端引擎（默认）

[ListenHub](https://listenhub.ai) 的 OpenAPI（`https://api.marswave.ai/openapi/v1`）提供几百个中文音色，包括豆包官方音色和社区克隆音色，多音字和语气无需词典即正确。密钥来自 ListenHub 控制台，只通过环境变量传入，按请求字符扣积分：

```sh
export LISTENHUB_API_KEY=lh_sk_…   # 只在当前 shell；不写进文件、工程或输出
work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py --list-voices
work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py \
  --input work/narration.json --out work/narration --voice houge
```

`--list-voices` 按行输出 `speakerId、名称、性别、中文描述`（2026-09 有 492 个中文音色）。`--voice` 接受下表简称或完整 speakerId：

| 简称 | 声音 ID | 试听印象 |
| --- | --- | --- |
| houge | doubao-official-zh_male_sunwukong_mars_bigtts | 男声，猴哥（孙悟空腔），默认；有趣、有表现力，学生向科普首选 |
| suzhe | suzhe-45bbbe54 | 男声，清晰明亮、语速中快；正经科普讲解 |
| yuanye | CN-Man-Beijing-V2 | 男声，沉稳磁性；叙事性内容 |
| gaoqing | gaoqing3-bfb5c88a | 女声，明亮有活力；专业讲解 |
| xiaoman | chat-girl-105-cn | 女声，温和亲切；知识分享 |

脚本按句（。！？）调用同步接口 `/tts`（mp3，32 kHz 单声道），裁掉每句首尾静音后统一留 0.5 秒句间停顿，句子边界按样本数计算。每句一次请求，约 100 秒旁白需 1–2 分钟；每次请求失败自动重试 3 次（超时按 `--timeout`），密钥无效或积分不足时立即报错。`--rate` 换算成语速倍率（`-3%` → 0.97，接口范围 0.5–2.0）。没有密钥时脚本提示改用 `--engine edge-tts` 或 `--engine kokoro`。ListenHub 还有异步的 FlowSpeech 接口（可自动改写讲稿、多角色对话），改写会偏离讲稿且字幕只到段落级，不适合本 skill 的逐句同步，未接入。

## Edge TTS 音色候选

以下标签来自 2026-09 的可用列表，用作初筛；适用人群是创作建议，不是效果保证：

| 简称 | 声音 ID | 标签与使用方向 |
| --- | --- | --- |
| yunxi | zh-CN-YunxiNeural | 男声，活泼阳光；初中科普优先试听 |
| xiaoyi | zh-CN-XiaoyiNeural | 女声，活泼；轻快探索式解说 |
| xiaoxiao | zh-CN-XiaoxiaoNeural | 女声，温暖；柔和清晰的讲解 |
| yunxia | zh-CN-YunxiaNeural | 男声，可爱；低龄动画可尝试 |
| yunyang | zh-CN-YunyangNeural | 男声，专业可靠；正式讲授 |
| yunjian | zh-CN-YunjianNeural | 男声，热情；适量用于激动的揭晓片段 |

工具也接受实时列表中的完整 ID，不限制用户只能选上述音色。

## Kokoro 本地引擎

[Kokoro-82M v1.1-zh](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh)（Apache 2.0）在 CPU 上离线合成，中文自然度接近 Edge，可作为无网络或不想依赖非官方端点时的选择。安装 `kokoro` 和 `misaki[zh]`（会带上 torch CPU 版，约 1 GB）并确保 PATH 中有 `ffmpeg`；已用 kokoro 0.9.4、misaki 0.9.4 验证：

```sh
work/tts-env/bin/python -m pip install 'kokoro>=0.9.4,<1' 'misaki[zh]>=0.9.4,<1'
```

首次运行从 Hugging Face 下载模型（约 330 MB）和所用音色文件；之后加 `HF_HUB_OFFLINE=1` 避免每次联网检查。Hugging Face 不可达时从 ModelScope 镜像 `hexgrad/Kokoro-82M-v1.1-zh` 取同名文件放进 HF 缓存目录。

音色只有编号：`zf_` 开头为女声（55 个），`zm_` 开头为男声（45 个）；`--engine kokoro --list-voices` 列出本机已缓存的音色。2026-09 试听过的候选：

| 声音 ID | 试听印象 |
| --- | --- |
| zm_066 | 男声，沉稳清晰，默认；讲解首选 |
| zm_010、zm_031 | 男声，语气平和，可作对比 |
| zm_020、zm_041 | 男声偏高、偏年轻 |
| zf_001、zf_018 | 女声清亮 |
| zf_079、zf_046 | 女声偏低、偏沉稳 |

生成前先查多音字，再合成：

```sh
HF_HUB_OFFLINE=1 work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py \
  --engine kokoro --check --input work/narration.json
HF_HUB_OFFLINE=1 work/tts-env/bin/python /path/to/student-explainer-video/scripts/narrate.py \
  --engine kokoro --input work/narration.json --out work/narration \
  --voice zm_066 --lexicon work/lexicon.json
```

`--check` 按场景列出讲稿里常见多音字实际会取的读音和备选读音，例如 `ladder	长	梯子长	chang2	备选 zhang3 chang2`；这一步不联网、几秒完成。Kokoro 的注音层按词典取读音，不看上下文：单字“地”默认 de，“长”在“多长”“边长”里默认 zhǎng，“的地得”结尾的词一律轻声。读音错时把带上下文的词写进项目词典 JSON（`{"梯子长": "ti1 zi5 chang2"}`，每字一个带声调数字的拼音，轻声用 5），用 `--lexicon` 传入；它会并入 `scripts/kokoro_lexicon.json` 里的默认词条，并写进 `manifest.json` 的 `lexicon` 字段。词条要写成分词后能整体命中的词组，单写“长”不起作用。改词典后重新 `--check` 确认，再合成。

Kokoro 与 ListenHub 一样按句（。！？）合成后拼接：它每句前后自带最长约 1 秒的静音，脚本裁掉后统一留 0.5 秒句间停顿，句子边界按样本数计算，比 Edge 的边界更准。`--rate` 换算成语速倍率（`-3%` → 0.97）。公式里的英文字母和 sin、cos 等词由 misaki 的英文词典注音，读作“A”“B”“sin”；词典没有的英文原样传给模型，很可能读错，讲稿里改写成中文。同一讲稿两次合成的音频不完全相同，重跑后重新取时间线。Apple Silicon CPU 上约 100 秒旁白用 30 秒合成，首次加载模型另需十几秒。

## 表现力与服务边界

Edge TTS 支持语速、音高、音量，不能直接套用 Azure 的 `cheerful` / `chat` 等自定义 SSML 风格。自然感按顺序来自连续语境、自然标点与可朗读公式；语速、音高只做小幅微调：用户要“活泼”“轻快”时用 `+0%` 到 `+5%`，要“沉稳”“慢一点”时用 `-3%` 到 `-5%`；中间生成的时间线随语速变化，改语速后重新生成。

用户要求更细的情绪表演时，可评估 MiniMax 或 Azure Speech：查看当前官方音色、模型及风格支持，再使用已有服务配置。不把密钥写进工程、命令参数或输出。所需服务不可用时说明现状并提供可用试听，不宣称已生成该引擎样本。

使用高级功能时核对当前官方资料：
- [ListenHub OpenAPI](https://listenhub.ai/docs/zh/openapi/api-reference/flowspeech)
- [Edge TTS](https://github.com/rany2/edge-tts)
- [Kokoro](https://github.com/hexgrad/kokoro) 与 [misaki 中文前端](https://github.com/hexgrad/misaki)
- [Azure 中文音色和风格支持](https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support)
- [MiniMax 同步语音合成](https://platform.minimax.cn/docs/api-reference/speech-t2a-http)

工作流灵感参考 [wshuyi/remotion-video-skill](https://github.com/wshuyi/remotion-video-skill/blob/main/README_CN.md)。本包工具独立实现，不要求安装该仓库。
