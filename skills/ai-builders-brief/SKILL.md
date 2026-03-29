---
name: ai-builders-brief
description: "Daily AI industry digest: curates 25+ top AI builders on X/Twitter, 6 podcasts (Latent Space, No Priors, etc.), and official blogs (Anthropic, Claude) into one brief. EN/ZH/bilingual. Delivers via Telegram, email, or in-chat. Zero API keys needed. Use when user wants AI news, builder updates, podcast summaries, or invokes /ai."
---

# AI Builders Brief — Follow Builders, Not Influencers

> **Credits:** Original project by [Zara Zhang](https://github.com/zarazhangrui/follow-builders) ([@zarazhangrui](https://x.com/zarazhangrui)). Licensed under MIT.

You are an AI-powered content curator that tracks the top builders in AI — the people
actually building products, running companies, and doing research — and delivers
digestible summaries of what they're saying.

Philosophy: follow builders with original opinions, not influencers who regurgitate.

**No API keys or environment variables are required from users.** All content
(X/Twitter posts, YouTube transcripts, and blog articles) is fetched centrally and
served via a public feed. Users only need API keys if they choose Telegram or email delivery.

## Full Installation

This skill requires scripts and config files. Install the full version:

```bash
npx skills add wifecooky/ai-builders-brief
```

Or manually:
```bash
git clone https://github.com/wifecooky/ai-builders-brief.git ~/.claude/skills/ai-builders-brief
cd ~/.claude/skills/ai-builders-brief/scripts && npm install
```

Then say "set up ai builders brief" or invoke `/ai-builders-brief`.

## What You Get

A daily or weekly brief delivered to Telegram, email, or in-chat:

- Key posts and insights from 25 curated AI builders on X/Twitter
  (Karpathy, Swyx, Sam Altman, Guillermo Rauch, Amanda Askell, etc.)
- Summaries of new episodes from 6 top AI podcasts
  (Latent Space, No Priors, Training Data, Unsupervised Learning, etc.)
- Highlights from official AI blogs (Anthropic Engineering, Claude Blog)
- Available in English, Chinese, or bilingual
- All original source links included

## How It Works

1. A central feed is updated daily with the latest content from all sources
2. Your agent fetches the feed — one HTTP request, no API keys
3. Your agent remixes the raw content into a digestible brief using your preferences
4. The brief is delivered to your channel of choice

Source: https://github.com/wifecooky/ai-builders-brief
