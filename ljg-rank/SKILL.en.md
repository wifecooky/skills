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

## Language

Output language matches user input language:
- Chinese input → Chinese output
- English input → English output
- Japanese input → Japanese output
- Other languages follow the same rule

## Output

1. Get timestamp: `date +%Y%m%dT%H%M%S` and `date "+%Y-%m-%d %a %H:%M"`
2. Write to `~/Documents/notes/{timestamp}--rank-of-{domain}__rank.md`
3. Report file path to user
