# Publishing in the user's Chrome: platform gotchas

Read before step 11. Everything here was hit for real (第四课 yellowstone, 2026-10-07).

## Upload files (all platforms)
- `file_upload` only accepts files **inside the session folders** and **≤ 10 MB per call**. Copy the MP4 and cover into `<cwd>/_upload/`. If the MP4 is over 10 MB, make a 2-pass copy that targets about 9.3 MB:
  ```bash
  src=x.mp4; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $src)
  vb=$(python3 -c "print(int((9.3*8*1024*1024/$d - 128000)/1000))")
  ffmpeg -y -v error -i $src -c:v libx264 -preset slow -b:v ${vb}k -pass 1 -an -f mp4 /dev/null && \
  ffmpeg -y -v error -i $src -c:v libx264 -preset slow -b:v ${vb}k -pass 2 -c:a aac -b:a 128k -movflags +faststart x-sm.mp4; rm -f ffmpeg2pass*
  ```
  A 52 s video comes out at 9.8 MB and looks the same on a phone.
- `file_upload` needs a `ref` from `find` or `read_page`. Never click the upload button: it opens the native picker.
- Never look in Keychain or Chrome's cookie store. Auto mode blocks it as credential exploration, and it isn't needed.
- If a tab id stops working, run `tabs_context_mcp` again, because tab groups can reset.

## 抖音
- The cover dialog has **several** file inputs. Use the "点击上传文件或拖拽文件到这里" input under 上传封面. Another input feeds the AI 生成参考图 box, and an auto-picked frame gets flagged 「封面不佳」.
- After 完成, a 设置横封面 popup appears. Choose 暂不设置.
- Check 内容管理 afterwards: 审核中 means it went through.

## 视频号 (channels.weixin.qq.com, wujie micro-frontend)
- The form lives in `document.querySelector('wujie-app').shadowRoot`, so `find`, `read_page` and `file_upload` can't see its inputs.
- To upload anyway, serve `_upload/` over CORS with `python3 $SK/cors_serve.py _upload` (127.0.0.1:8765, run in background, kill afterwards). Then fetch the file in JS and inject it. **Use the iframe's constructors**: main-window `DataTransfer`/`File` objects are silently ignored.
  ```js
  const root=document.querySelector('wujie-app').shadowRoot;
  const inp=[...root.querySelectorAll('input[type=file]')].find(e=>e.accept.includes('video')); // 'image' for the cover
  const w=document.querySelector('iframe').contentWindow;
  const b=await (await fetch('http://127.0.0.1:8765/x-sm.mp4')).blob();
  const dt=new w.DataTransfer(); dt.items.add(new w.File([b],'x.mp4',{type:b.type}));
  inp.files=dt.files; inp.dispatchEvent(new w.Event('change',{bubbles:true}));
  ```
  The page shows 「封面已更新」 when the cover is taken.
- Click 发表 from the shadow root, or click its on-screen coordinates (`getBoundingClientRect` gives CSS px; scale to the screenshot frame).
- **位置 auto-fills to the current city.** Point it out when confirming.

## 小红书
- The body is a tiptap/ProseMirror editor. **Don't press Enter to pick a topic**: only the first one sticks, and later keystrokes escape the editor. In our run they opened 原创声明, toggled it on, and swapped the cover twice. Instead, type `#tag`, wait 2 s, then click the suggestion with JS:
  ```js
  window.pick=t=>{const it=[...document.querySelectorAll('.item')].find(e=>e.innerText.split('\n')[0].trim()===t);
    if(!it)return 'MISS '+t;['mousedown','mouseup','click'].forEach(ev=>it.dispatchEvent(new MouseEvent(ev,{bubbles:true})));return 'ok '+t}
  ```
  Check that every tag became a real `[话题]` link, not plain text.
- Cover: click the cover thumbnail → 编辑封面 → `file_upload` to the 上传封面图片 input → 完成. It should pass 「封面效果评估通过」.
- Before confirming, re-check 原创声明, 可见范围, 定时发布, and any auto-linked 活动.
- 定时发布 is **Beijing time (GMT+8)**: the saved value is read as Beijing time, and 笔记管理 shows `(GMT+8:00 北京时间)`. The picker's 1-hour minimum is computed in browser local time, so don't infer the zone from it. For JST 18:00, enter **17:00**.

## Confirm step
When asking for the yes, offer three options: **I click 发布 / you click it yourself / 定时**. The user sometimes publishes themselves or schedules a post for the next day (小红书 第四课 was scheduled by the user).
