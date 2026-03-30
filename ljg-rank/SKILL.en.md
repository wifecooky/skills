---
name: ljg-rank
description: Given a domain, find the truly independent generators holding it up. Slash a dozen phenomena down to the irreducible minimum — then regenerate every phenomenon from those generators, or start over.
user_invocable: true
---

# Rank Reduction Engine

Input a domain, output its rank.

## What is Rank

Rank is not "key factors", not "core principles", not "summary points".

Rank is: how many truly independent generators exist in this domain? Can you reverse-generate all observed phenomena from them? If yes, you've found it.

## Four Criteria

All four must pass for the rank to stand. If any one fails, start over.

1. **Generativity** — Every observed phenomenon can be traced back using the generators. Not a single one left out.
2. **Minimality** — Removing any single generator leaves some phenomenon unexplained. No redundancy.
3. **Independence** — For each pair of generators, a real-world case exists where one changed and the other didn't.
4. **Predictive power** — The generators can derive phenomena beyond the original list, and those phenomena actually exist in reality.

## How to Write

Write an essay. Not a table.

Your task is to walk the reader on a journey: from "this domain looks chaotic" to "it's just these two or three threads pulling everything". How you walk that path is your call. No prescribed sections, no prescribed format, no prescribed headings.

Three requirements only:
- **Can't stop reading** — even someone unfamiliar with the domain keeps going
- **Memorable** — after reading, they can explain it to a friend in one sentence
- **The drop** — the contrast from chaos to minimalism is the beauty of rank reduction

Verification of the four criteria is mandatory, woven into the essay. Verification itself is part of the narrative — "what happens to the world if you remove a generator" makes a good story, "using generators to derive an unexpected phenomenon" makes a good ending. No appendix.

## Language & Localization

Output language matches user input language. Not just translation — full cultural adaptation.

Language switching:
- Chinese input → Chinese output
- English input → English output
- Japanese input → Japanese output
- Other languages follow the same rule

Localization requirements — the following must match the target language's cultural context:
- **Metaphors and imagery**: Chinese can say "一锅粥" (a pot of congee), English should use "a tangled web", Japanese should use appropriate idiomatic expressions
- **Examples**: Chinese context uses WeChat, Taobao, Gaokao; English context uses Google, Amazon, SAT; Japanese context uses LINE, Rakuten, センター試験
- **People and event references**: Chinese can cite Lu Xun, English cites Feynman, Japanese cites Murakami — use names the target reader recognizes instantly
- **Data and units**: English uses miles/Fahrenheit (US context) or km/Celsius (international), Japanese uses locally common units
- **Tone and rhythm**: Chinese prose can use staccato parallel clauses, English prose can build momentum with long subordinate clauses, Japanese should mind 敬体/常体 register shifts

Principle: The reader should never feel the essay was translated from another language. It should read like an original written by a native speaker.

## Output

1. Get timestamp: `date +%Y%m%dT%H%M%S` and `date "+%Y-%m-%d %a %H:%M"`
2. Filename is also localized:
   - Chinese: `~/Documents/notes/{timestamp}--{domain}的秩__rank.md`
   - English: `~/Documents/notes/{timestamp}--rank-of-{domain}__rank.md`
   - Japanese: `~/Documents/notes/{timestamp}--{domain}の秩__rank.md`
3. Report file path to user
