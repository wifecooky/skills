---
name: workreport
description: Use when the user asks for a work report — 報告 / 週報 / 作業報告 / 今週やったこと / /workreport — covering recent development work across one or more repos or PRs.
---

# Work Report(作業報告)

開発作業を日本語のビジネス報告にまとめる。読者は非エンジニアの上司・チーム。

## Input

すべて省略可(聞かずに進める):
- 対象期間(省略時: 今週月曜〜今日)
- リポジトリのパス / PR の URL(省略時: 自動スキャンで発見)

## Workflow

1. **対象リポジトリの自動発見**:
   ```bash
   for d in ~/Documents/git/*/; do
     [ -e "$d/.git" ] || continue
     n=$(git -C "$d" log --all --since=<期間開始> --author="$(git -C "$d" config user.email)" --oneline 2>/dev/null | wc -l | tr -d ' ')
     [ "$n" -gt 0 ] && echo "$n commits  $d"
   done
   ```
2. **事実収集**(リポジトリごとに並列で):
   - `git log --all --since=<期間開始> --author="$(git config user.email)" --pretty="%h %ad %s" --date=short`
   - GitHub remote があるリポジトリは PR も:
     `gh pr list --repo <owner/repo> --author "@me" --state all --search "updated:>=<期間開始>" --json number,title,state`
     該当 PR は `gh pr view` で詳細取得。ローカルコミットと同一内容の PR は重複報告しない(PR 側に寄せる)
2. **名称・仕組みは必ずリポジトリで検証してから書く**。README / コードを grep して確認する。
   コミットメッセージ中の略語(例: sycm)から製品名や API 名を推測で補完しない —
   過去に「sycm 方式」を「千牛 API」と誤記した実例あり。実際は鯨芽自体の webapi だった。
3. コミットをテーマ別に分類し、下の Output format で報告を書く。

## Output format

言語: **報告本文は日本語**(チームへそのまま貼れる形)。前後の説明コメントは中国語。

プロジェクトごとに:

```
### N. <プロジェクト名>          ← ユーザーの呼称を使う(下の Known projects 参照)

**データ取得/仕組み**(一文): ...   ← 必要な場合のみ。一文で

**機能一覧**
- 太字ラベル + 一行説明 × 最大7行   ← 分類見出しで細分化しない

**ROI(定量)**                    ← 数値ソースがある場合のみ
| 項目 | 数値 |  形式の表。回収期間と ROI 倍率まで計算する

**PR 状態**: レビュー中 / マージ済み等   ← PR が指定された場合のみ。無ければ行ごと省略
```

## Rules

- **技術用語を書かない**: AWS / CDK / S3 / SQLite / WASM / XHR / launchd 等は禁止。
  「どこからでも閲覧可能」「無人で自動実行」のように業務効果で言い換える
- **数値は実ソースのみ**: README・コミット・PR に書いてある数字だけ使う。創作しない。
  ROI は既存数値から計算(例: 開発1人日 ¥28,000 vs 年間削減 ¥406万 → 約145倍、2営業日で回収)
- **簡潔第一**: 機能は1行1機能。ユーザーは毎回「もっと簡潔に」と言う前提で最初から短く
- 最後に「合并成完整版要说一声」程度の一言を中国語で添える

## Known projects

| リポジトリ | 報告での呼称 |
|---|---|
| ~/Documents/git/jingya | 鯨芽商品掲載店舗モニタリングダッシュボード |
| ~/Documents/git/jam-bo(= novarca/juaimai-storefront-bo) | JAM Retail |
| ~/Documents/git/NovarcaBrandDiscovery | 日本コスメブランド発掘ダッシュボード(Novarca Brand Discovery) |
| ~/Documents/git/華僑PF | 華僑向けEC市場調査ツール(Yamibuy/Weee の日本商品・レビュー収集) |
| ~/orca/projects/ppt-translater(= novarca/ppt-translater) | PPT翻訳ツール |

注: ~/Documents/git/ 以外に ~/orca/projects/ にも仕事リポジトリがある。スキャン時は両方見る。

スキャンで新しいリポジトリを発見したら、報告後にこの表へ追記する。
