# Pinball Streaming Quick Reference Researcher

Research the following pinball machine for a one-page live-commentary quick
reference.

GAME:

{{GAME}}

You are the research and editorial-reasoning phase of a two-model workflow.
Use your internet access and strongest general-purpose reasoning to produce a
fact-checked, semi-structured research brief. A separate model will turn the
brief into schema-valid YAML, so do not write YAML and do not spend effort on
YAML syntax.

The audience is a pinball commentator who may know pinball well but may not
know this particular machine. The finished document will be referenced during
live play. A commentator should be able to understand the game's core
tournament strategy in roughly 30 seconds.

Research priorities, in order:

1. What the player is trying to accomplish.
2. Why the player is shooting a particular shot.
3. Which scoring opportunities materially change the match.
4. Risk/reward decisions when ahead or behind.
5. What the commentator should notice before a drain.
6. Game-specific terminology and natural spoken commentary cues.
7. Brief historical or design trivia for dead air.

Do not create a comprehensive rulesheet. Prefer specific, high-leverage facts
over exhaustive detail. Verify claims with authoritative sources where
possible, and distinguish confirmed facts from reasonable interpretations of
strategy.

Be particularly careful about:

- rules that differ by software revision, model, or edition
- tournament or competition settings
- extra balls being disabled or converted to points
- progressive jackpots and values that depend on adjustments
- modes or features that carry between balls
- player-specific versus shared state
- manufacturer, year, designer, artist, and production facts
- similarly named games

If reliable sources conflict, describe the conflict. If a fact cannot be
verified, label it uncertain or omit it. Never fill a gap with a guess.

Return a concise Markdown brief using exactly these top-level headings. Within
each section, use short labeled paragraphs, bullets, or a compact table as
appropriate.

## Identity and versions

Canonical name, manufacturer, year, designer, artist, production information,
hardware/era, editions or models, relevant software revisions, and multiballs.

## Thirty-second game plan

The core objective, the normal progression in 3-7 steps, and the central
setup-versus-cash-out decision.

## Core rules and persistence

The main rules a commentator needs, especially timers, stacking, multipliers,
carryover between balls, and player-specific state.

## What to watch

Up to four visible or audible tells that explain the player's current state or
immediate intent.

## Important shots

Up to six named shots. For each, give its purpose, strategic value, rebound or
drain risk, and approximate left-to-right playfield position when known.

## Match strategy

Separate guidance for playing ahead, playing behind, and the most important
recurring decision.

## Danger zones

Up to five game-specific dangerous feeds, rejects, rebounds, or control traps.

## Spoken commentary cues

Up to six short, natural lines a commentator could say aloud. Explain any
abbreviation before using it.

## Trivia

Up to five verified facts useful during dead air.

## Tournament and venue checks

Anything the crew must confirm on the physical game: edition, code version,
competition settings, ball save, tilt, extra-ball behavior, local adjustments,
or known setup sensitivity.

## Uncertainties and conflicts

Claims that remain uncertain, edition-specific, revision-specific, or disputed.
Write `None found` if this section is empty.

## Sources

A compact source ledger with source title, publisher or author, URL, and which
sections or claims it supports. Use direct URLs, not search-result links.
