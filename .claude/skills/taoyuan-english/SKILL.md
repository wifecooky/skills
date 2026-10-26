---
name: taoyuan-english
description: Use when making, voicing, publishing, exporting or reviewing metrics for an episode of 「桃园英语角」 (sanguo theme, 三国学英语), or any short video teaching English to Chinese viewers — Chinese-language copy for 抖音/视频号/小红书, the 桃园 feedback store and dashboards.
---

# 桃园英语角 (English for Chinese viewers)

**Pipeline:** `pipeline.md` in this skill (workflow, script.json fields, render). Scripts: `SK=~/.claude/skills/taoyuan-english/scripts`; theme pack in `themes/`. This skill is self-contained.

## Series
- Audience: Chinese speakers learning English. Dialogue is Chinese; only the taught English phrase is English.
- Theme pack `sanguo`. Recurring cast: L 刘备, G 关羽, Z 张飞, C 曹操, T Owen老师 (teacher/narrator, never drawn). Watermark `@桃园英语角`.
- Experiments run one variable at a time, per the 「实验规则」 section in `LEARNINGS.md` (feedback store below). Follow it when writing `script.json` (e.g. `"intro": false` while H4 is running).
- Card: `zh` = the English phrase, `py` = IPA, `en` = the Chinese idiom (`pipeline.md` `card`).
- Project dir: `~/git/taoyuan-english/videos/<YYYYMMDD-slug>/` (episodes up to 07 are in `~/Downloads/funny-short/videos/`). Brand assets (avatar, banners, `youtube-copy.md`, old covers): `~/git/taoyuan-english/videos/_brand/`. Cover: `renders/cover-epN-<slug>.jpg` (3:4), where `export_lesson.py` finds it.
- Topic log: `~/git/taoyuan-english/videos/选题记录.md` (append only: 日期 | 热点 | 英文表达 | 标题). No Drive copies.

## Guest cameo (occasional)
A famous figure drops in to help explain the phrase. The time-travel mismatch (关公战秦琼) is part of the joke.
- **Only when the guest has a real tie to the phrase**: its source (Shakespeare → break the ice, wild-goose chase, all that glitters is not gold), or the field it is about (华佗 → health phrases, 诸葛亮 → strategy, 李白 → drinking or mood). If no guest fits, skip the cameo. Aim for about 1 episode in 4–5.
- **Historical or public-domain figures only. Never a living real person** (no celebrities, influencers or entrepreneurs). AI likeness and voice raise portrait and voice rights and deep-synthesis labeling rules, and the series publishes without AI labels.
- **Where:** the card scene (with or instead of Owen) or the final twist. Try to keep the main part under 40 s (H3, not yet verified), and give the guest 1–2 lines.
- **How:** add a project `cast` entry, for example `"S": {name, chip, voice, look, persona}`.
  - `panels.py`/`voice.py` read only the project `script.json` (only `build.py` merges the pack). Copy the pack's full `cast` into the project, then add the guest. Why: ep23 (2026-10-25) had only the guest in `cast`, so voice.py died with KeyError 'C' and panels.py drew without the pack looks. Verify: `python3 -c "import json;print(list(json.load(open('script.json'))['cast']))"` lists L G Z C T plus the guest.
  - `look` names the era's garment (e.g. "Elizabethan doublet and ruff").
  - Pick a `voice` that is not used by any pack character.
  - The pack charsheet doesn't include the guest. Describe the guest fully in each panel's `art`, and exclude everyone not in that panel ("Only X is drawn; …").
- **Track it:** the first guest episode adds H6 to `LEARNINGS.md`: guest episodes beat the series median on 2-second bounce and completion. Note which episodes had a guest under 本集验证.

## Beauty cameo (adult audience, charm not skin)
The audience is adult, so a glamorous woman from the 三国 era can appear: 貂蝉 (美人计), 大乔/小乔 (铜雀台), 孙尚香 (martial, floors 张飞), 甄宓 (the 曹 family triangle).
- **The joke is the men's reaction, not her body.** For example: 张飞 gets heart eyes and steam from his ears (not a nosebleed: that manga gag points back at her body), 关羽's beard-stroking hand freezes, 刘备 stammers.
- **Charm, not exposure.** Use a period-accurate, ornate, form-fitting robe, plus an alluring gaze and pose. Don't show nudity, cleavage focus, sexual poses or innuendo-heavy lines.
  - Douyin, Xiaohongshu and Channels quietly throttle 擦边 content.
  - gpt-image-2 refuses or mangles revealing prompts.
  - The account is an English-learning brand.
- **Fit the phrase.** Use her when the lesson is about attraction or romance: drop-dead gorgeous, head over heels, out of my league, femme fatale, play hard to get.
- **How:** add a project `cast` entry (full pack cast first, as for guests).
  - Her `look` names the Han-dynasty garment (e.g. "Eastern Han layered silk ruqun, NOT a qipao").
  - Voice candidates: 谄媚女声, 撒娇学妹, 倾心少女. Let the user pick by ear on a real line.
  - Exclude her from panels she isn't in, as for guests.
  - Try it in 2–3 episodes before adding her to the `sanguo` pack. Adding her to the pack means redrawing the charsheet.
- **Track it:** the first such episode adds H7 to `LEARNINGS.md`: beauty-cameo episodes beat the series median on 2-second bounce and completion.

## Feedback (`feedback-loop.md`)
- Store `<S>`: `~/git/taoyuan-english/videos/_metrics/taoyuan`
- Public sources for `fetch`: `https://www.youtube.com/channel/UCyaiX1XN53OMXu-OMNAKQCg/shorts`
- Dashboards (step 2), in the user's Chrome, **read-only**:
  - **抖音** `https://creator.douyin.com/creator-micro/content/manage`. Every work lists 播放 点赞 评论 分享 收藏 完播率 2秒跳出率 吸粉量. Keep only works whose description has `#桃园英语角` or a 三国 hook; the account also holds old unrelated posts. Record each with
    `python3 $SK/metrics.py add <S> douyin <YYYY-MM-DDTHH:MM> published=<date> title=<短标题> views= likes= comments= shares= saves= completion=<x%> bounce2s=<x%> follows=`
    The id is the publish time shown on the card.
  - **小红书** `https://creator.xiaohongshu.com/new/note-manager?source=official`. It takes about 5 s to render. The five numbers under each note are, in order: 观看 评论 点赞 收藏 分享. Use `add <S> xhs <time> published= title= views= comments= likes= saves= shares=`.
  - **YouTube 地区** (from 2026-10-21; decides how much the 繁體 translation matters) `https://studio.youtube.com/channel/UCyaiX1XN53OMXu-OMNAKQCg/analytics/tab-build_audience/period-default` → Top geographies → See more (the table loads ~10 s later; read it with JS `innerText`). Record the 28-day window with
    `python3 $SK/metrics.py add <S> youtube-geo 28d-<window end date> views=<total> tw=<x%> hk=<x%> my=<x%> sg=<x%> other=<100 − listed>%`
    plus any other listed country by its two-letter code. YouTube hides small countries, so `other` is often large. VPN users from mainland China show up under the VPN's exit country.
  - **视频号** `https://channels.weixin.qq.com/platform/post/list` (wujie: read `document.querySelector('wujie-app').shadowRoot` text). If it redirects to `login.html`, skip it and say 「视频号需要扫码登录」 in the report.

## Publish
Chinese copy, rules in `publish-copy.md`. Never publish without an explicit go per platform (`pipeline.md` step 11).

## Content export
`EP=<NN>-<english-slug> python3 $SK/export_lesson.py` (NN = highest in `~/git/taoyuan-english/content/episodes/` + 1; slug e.g. `too-good-to-be-true`) → the `sanguo` pack's `site` (`~/git/taoyuan-english/content`). Rerun after publishing.
