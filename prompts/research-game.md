# Pinball Streaming Quick Reference Researcher

Research the following pinball machine for a one-page live-commentary quick reference.

GAME:

{{GAME}}

You are the research stage of a version-controlled publishing workflow. Produce a fact-checked, semi-structured research brief that will later be transformed into a printable one-page commentator reference.

The audience is an experienced pinball commentator who may know pinball well but may not know this particular machine. During live tournament play, the page should let them answer three questions almost immediately:

1. What is the player trying to accomplish?
2. Why are they shooting that shot right now?
3. What could cause the score or match position to change dramatically?

A commentator should be able to understand the game's primary tournament strategy in roughly 30 seconds.

## Research priorities

Prioritize, in this order:

1. The primary tournament scoring objective.
2. The normal progression required to reach it.
3. Why a player chooses one important shot over another.
4. Scoring leverage: multipliers, stacks, jackpots, bonuses, or other features capable of materially changing the match.
   1. Always include any verified scoring opportunity whose value is large enough to plausibly swing a tournament game, even if it is not part of the dominant strategy.
5. Risk/reward decisions when playing ahead versus behind.
6. Visible or audible game-state cues a commentator can recognize on stream.
7. Dangerous feeds, rejects, rebounds, and control problems that commonly precede drains.
8. Game-specific terminology and useful spoken commentary language.
9. Brief verified historical or design trivia for dead air.

Do **not** create a comprehensive rulesheet. Do not enumerate every mode, award, shot, or scoring value. Omit rules that do not materially help explain competitive play.

Prefer a few specific, high-leverage facts over exhaustive detail.

## Research and evidence standards

Distinguish clearly between:

* **Confirmed rule** — directly supported by reliable rules documentation or authoritative evidence.
* **Observed strategy** — a tournament approach documented or repeatedly demonstrated by strong players or expert sources.
* **Strategic inference** — a reasonable conclusion derived from verified rules but not directly documented as established strategy.

Never present a strategic inference as a confirmed rule or established tournament consensus.

When sources are available, prioritize roughly in this order:

1. Manufacturer manuals, official rulesheets, code/update notes, and official technical documentation.
2. Statements from the game's designer, programmer, or manufacturer.
3. Detailed community rules documentation from reputable pinball sources.
4. Tournament footage, tutorials, strategy articles, or commentary from experienced competitive players.
5. Other secondary sources.

Manufacturer marketing material is useful for identity, credits, hardware, and feature descriptions but should not automatically be treated as a complete or current rules reference.

Assign sources identifiers such as `[S1]`, `[S2]`, etc. Cite consequential factual claims inline using those identifiers. The final Sources section must resolve every identifier to a direct URL.

If reliable sources conflict, describe the conflict rather than silently choosing one.

If a claim cannot be verified, label it **uncertain** or omit it. Never fill a factual gap with a guess.

## Version and configuration sensitivity

Be particularly careful about:

* rules changed by software revision
* Pro/Premium/LE or other model differences
* competition/tournament mode
* extra balls being disabled or converted to points
* factory versus venue adjustments
* ball count
* ball-save settings where strategically significant
* progressive jackpots or values that depend on adjustments
* features that persist between balls
* features that persist between games
* player-specific versus globally shared state
* physical mechanisms that behave differently between editions
* manufacturer, year, designer, programmer, artist, and production facts
* similarly named or remade games

For modern software-driven games, state the latest rules/code version you were able to verify and the date or source of that information when possible.

Do not catalog every possible operator adjustment. Mention an adjustment only if changing it would materially alter tournament strategy or what a commentator should say.

## Output requirements

Return concise Markdown.

Target **no more than about 1,500 words**, excluding the source ledger and human questions. Shorter is preferred when the game is strategically simple.

Use exactly the following heading structure.

## Identity and versions

Include:

* canonical game name
* manufacturer and year
* designer and other major credited creators when verified
* hardware/platform/era when useful
* relevant models or editions
* important edition differences
* latest rules/code revision actually verified, when applicable
* number and names of major multiballs only when useful for commentary

Do not turn this into a complete credits list.

## Thirty-second game plan

Explain the game's dominant tournament approach in **3–5 short steps**.

Include:

* the primary setup
* the primary scoring payoff or cash-out
* the major scoring multiplier or leverage mechanism, if any
* the central setup-versus-cash-out decision
* one materially viable alternate strategy, if the game genuinely has one

The reader should understand from this section alone what a strong tournament player is generally trying to do.

## Core rules and persistence

Include only rules needed to correctly interpret competitive play.

Prioritize:

* qualification requirements
* important timers
* stacking rules
* scoring multipliers
* jackpot progression
* mode interactions
* locks
* carryover between balls
* resets at end of ball
* player-specific versus shared state
* significant end-of-ball bonus behavior

Explicitly identify anything that is easy for a commentator to misunderstand.

## What to watch

Give **up to four** visible or audible tells that reveal game state or likely player intent.

Prefer cues a commentator can actually detect on a live stream, such as:

* insert or arrow state
* physical locks or mechanisms
* display callouts
* mode or multiball music
* jackpot lighting
* multiplier indicators
* obvious qualification progress

For each cue, explain briefly what it means strategically.

## Important shots

Give **up to six** important named shots.

For each include:

| Field    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| Shot     | Common name                                                   |
| Position | Approximate left-to-right playfield location                  |
| Advances | What rule, mode, lock, jackpot, or resource it advances       |
| Why now? | Why a tournament player would choose it in the relevant state |
| Risk     | Important reject, rebound, feed, or drain danger              |

Prefer shots that explain player decisions rather than merely listing major playfield features.

## Match strategy

Give concise guidance for:

**Playing ahead:**
What safer scoring, control, cash-out, or risk-reduction choices become attractive?

**Playing behind:**
What higher-variance stacks, multipliers, modes, or aggressive choices become attractive?

**Key recurring decision:**
Describe the single decision that most often explains why two good players may choose different shots.

If there are multiple recognized tournament strategies, distinguish them rather than pretending one route is universally optimal.

## Danger zones

Give **up to five** game-specific dangerous situations.

Examples include:

* common shot rejects
* center-drain rebounds
* dangerous ramp returns
* orbit feeds
* pop-bumper exits
* scoop kickouts
* failed control attempts
* physical mechanisms known to produce risky feeds

Explain the consequence in one short line each.

Favor dangers that help a commentator recognize *why a drain just became likely*.

## Spoken commentary cues

Give **up to six** short game-specific commentary templates or phrases.

These should sound natural during tournament commentary and help explain the rules, for example:

* a qualification milestone
* a stack becoming available
* a multiplier being brought into play
* a dangerous return
* a cash-out decision
* a major scoring opportunity being lost

Avoid generic lines that could apply to any pinball machine.

Explain an abbreviation before using it.

## Trivia

Give **up to five** short, verified facts useful during dead air.

Prefer:

* unusual design history
* theme or production context
* designer/programmer/art connections
* distinctive mechanisms
* meaningful differences from another edition

Do not include folklore unless clearly identified as such.

## Questions for the humans

Only include questions whose answers could materially change the final commentator page.

Prefer multiple-choice questions so venue staff can answer quickly.

### Tournament and venue checks

Ask about unresolved physical-game or event configuration issues such as:

* exact edition/model
* installed software revision
* competition mode
* extra-ball behavior
* significant operator adjustments
* unusually short or long ball save
* tilt sensitivity when unusually relevant
* known setup-specific feeds or rejects

Do not ask about a setting merely because it exists.

### Uncertainties and conflicts

List claims that remain:

* uncertain
* edition-specific
* revision-specific
* adjustment-dependent
* disputed between reliable sources

Include the competing interpretations and source identifiers when applicable.

Write `None found` if there are no material unresolved issues.

## Sources

Provide a compact source ledger.

For each source give:

* source identifier (`S1`, `S2`, etc.)
* title
* publisher or author
* direct URL
* source type
* which claims or sections it supports

Use direct URLs, not search-result URLs.

Prefer primary and technically detailed sources over large numbers of redundant sources.
