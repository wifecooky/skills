# 讲解动画模板

固定的部分：片头（片名、副标题、署名）、片尾（署名、致谢行）、字幕样式、配色、字体、背景音乐。全部在 `video.config.json` 里：`author`、`palette`、`font`、`caption`、`bgm` 由用户设置一次，之后每部视频只改 `title`、`subtitle`。`credits` 是片尾给观众看的行，例如学校、频道、参考教材，默认为空；配音引擎、音色、音乐来源这类制作信息写进交付说明，不上画面。`author` 是署名（默认 `thewang.net`）：片头底部、片尾标题下方各显示一次，讲解期间以小字常驻画面右上角；为空时三处都不显示。片头片尾用细边框、短分隔线和依次淡入上浮的排版，样式在 `src/Signature.tsx`、`TitleCard.tsx`、`EndCard.tsx`，字幕样式在 `Caption.tsx`。场景代码不写颜色值。

背景音乐：`bgm.file` 指向 `public/` 下的文件，自动循环，片头淡入、片尾淡出，旁白期间压到 `bgm.duck` 倍。自带的 `bgm/pad-loop.mp3` 是程序合成的和弦垫乐，可以直接用；换成真实曲子时确认许可，`bgm.file` 留空则无音乐。

每次视频只做三步：

1. `narrate.py` 的输出目录整个复制到 `public/narration/`（含 `manifest.json` 和各音色文件夹）。
2. 在 `src/scenes/` 里为 `narration.json` 的每个场景 id 写一个组件，并在 `src/scenes/index.tsx` 的 `SCENES` 里登记。组件收到 `scene` 和 `t`（音频开始后的秒数），视觉事件对齐句子边界：按句子文本在 `scene.boundaries` 里找到对应项再取 `startSeconds`，不要按下标，TTS 的分句可能与讲稿不同。颜色用 `objectColor("a")`、`PALETTE.line` 等。
3. 口播和字幕写法不同的句子写进 `src/captions-display.json`（口播原句 → 显示文本）。

命令：

```
npm install
npx tsc                                   # 类型检查
npx remotion render Explainer-<音色ID> out/video.mp4 --color-space=bt709
node scripts/make-srt.mjs out/video.srt [音色ID]
```

`manifest.json` 里每种音色生成一个 composition，id 为 `<config.id>-<音色ID 去掉非字母数字>`，例如 `Explainer-zh-CN-YunxiNeural`。时间线 = 片头 + `narrate.py` 时间线 + 片尾；SRT 由 `make-srt.mjs` 用同一个片头偏移生成，不要手工改帧号。没有配音时也能渲染，只有片头片尾，用来预览署名和配色。
