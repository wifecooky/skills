# Storyboard logic check

Run this before showing a storyboard to the user, and again after any scene is added, removed, or rewritten. The author can't see their own holes, so hand it to a **fresh subagent** that only gets `STORYBOARD.md` (plus the panel images if they exist) and this file. Fix every BLOCKER before the user sees the storyboard.

## Checklist

1. **Every payoff has a setup.** For each laugh, point to the earlier scene that set it up. If there isn't one, that's a BLOCKER.
2. **Every setup is paid off.** A planted detail (the "fat" gossip, a prop, a promise) must come back. If it's dropped, remove it or call back to it.
3. **The big reveal happens once.** The core gag (the arrival, the twist, the misunderstanding) must not be shown or confirmed before the climax. Showing it early halves the punchline.
4. **Causality.** Every entrance and every action has a trigger the viewer saw. Ask "why does X appear, know, or do this NOW?" If the only answer is "because the plot needs it", that's a BLOCKER.
5. **Knowledge state.** No one reacts to information they couldn't have. Track who saw and heard what in each scene.
6. **Character consistency.** Each line fits the cast card: personality, tone, and register. A deadpan character shouldn't suddenly gush.
7. **Escalation.** Beats grow toward the climax (rule of three). The strongest laugh comes last, or second-to-last before a tag.
8. **Panel matches line.** The speaker is drawn, the action in the line is visible, and no one is in frame who shouldn't be.
9. **Teaching point (lesson videos).** The target phrase is used correctly in context *before* the card. The card's meaning matches how it was used. Translations are idiomatic, not literal, unless the literal reading is the joke.
10. **Length.** About 30–45 s for Shorts. Cut any scene that neither sets up nor pays off.

## Output format

For each issue: `BLOCKER|MINOR — scene id — problem — concrete fix`. End with a one-line verdict: `PASS` or `FIX`.
