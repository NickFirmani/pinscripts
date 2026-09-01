## Identity and versions

* **Speakeasy** — Bally Manufacturing, **August 1982**, model **1273**; Bally MPU **AS-2518-35**, two-player solid-state game. Design: **George Christian**; software: **Rehman Merchant**; art: **Greg Freres**; **3,000 produced**. [S1][S4]  ([Pinside][1])
* Signature mechanisms: five **Flyaway Targets** (10-through-Ace of Spades), an under-playfield **roulette wheel**, unusual crossover return lanes, and the player-operated **Sacrifice button**. No multiball. [S1][S4] ([PinWiki][2])
* It is an **Add-A-Ball** game: the ball counter can increase—and the roulette can even **subtract a ball**. This is fundamental to tournament configuration. [S1][S3] ([Skill Shot][3])
* Bally also produced **Speakeasy 4**, a four-player version using separate ROM E877-4. The requested machine is the standard two-player Speakeasy. [S5] ([Action Pinball][4])
* Verified two-player ROMs: **E877-2 = Version 1; E877-3 = Version 2**. I found no reliable human-readable changelog explaining gameplay differences; E877-3 is the commonly listed later two-player ROM. [S5] ([PinRepair][5])

## Thirty-second game plan

1. **Build Bonus X aggressively.** Completing all five Flyaway Targets—even out of order—advances the multiplier; repeated upper-card completions also raise it. The multiplier ladder reaches **10×**. **Observed strategy.** [S1][S3] ([Skill Shot][3])
2. **Work the 5–9 Hearts lanes in sequence.** A proper sequence earns **two added balls**; progress persists between balls, making this potentially more valuable than raw score. [S2][S3] ([vgpavilion.com][6])
3. The center **10–Ace Flyaways** are the other core route: sequence completion awards an added ball; any-order completion still improves Bonus X, spinner value and chip-value progression. [S2][S3] ([Atari Compendium][7])
4. Once Bonus X is high, maximize the **persistent base bonus** and exploit spinner/roulette scoring. The detailed competitive source reports **119K maximum bonus ×10 = 1.19M** at end of ball. [S3] ([Skill Shot][8])
5. Central decision: **play for deterministic bonus/multiplier versus chasing added balls**. If added balls are live, survival can dominate everything else.

## Core rules and persistence

* **Hearts 5–9:** top rollovers must be completed sequentially for the two-ball award. They **remain lit between balls**, but the sequence detector resets each ball—a strange rule that can turn prior out-of-order progress into a successful sequence on the following ball. [S3] ([Skill Shot][8])
* Operator switch 21 determines whether the valid top-card sequence is **5→9 only** or **5→9 / 9→5**. [S6] ([Pinside][9])
* **Spades 10–Ace Flyaways:** targets swing upward and lock when hit from the front; all five reset once completed. Sequential completion adds a ball; any completion advances multiplier/spinner/chip progression. They reset each ball. [S2][S3] ([Pinside][10])
* Bonus multiplier lamps are explicitly **2×, 3×, 5×, 10×**. [S1] ([PinWiki][11])
* Competitive documentation reports the **base bonus persists between balls** and tops at **119K**; multiplier-building is treated as a per-ball priority. [S3] ([Skill Shot][3])
* **Roulette scoring is multiplied by Bonus X**, so the 10× state affects more than end-of-ball bonus. [S3]
* Easy commentator trap: this is not merely “score poker hands.” **Sequence order matters**, and a wrong card can poison an otherwise nearly-complete Add-A-Ball sequence.

## Skill shots

**None found.** No separately named/coded plunge skill shot was verified.

The plunge is still strategically important: players want the **next legal 5–9 Heart lane** because completing that sequence is worth **two added balls**. Do not call this a formal skill shot; describe it as sequence placement. [S2][S3]

## Secondary features

* **Sacrifice button:** available at the beginning of a ball; removes cards made out of sequence at a cost of **25K per cancelled card**. It exists specifically to repair a damaged sequence. [S1][S2] ([PinWiki][2])
* **Roulette wheel:** lit side saucers spin the physical wheel; outcomes include point awards, **Add-A-Ball**, and **Subtract-A-Ball**. It also spins at end of ball if the player did not tilt. [S1][S3] ([Skill Shot][3])
* **Jokers:** right-side Joker lane advances one Joker; **four Jokers = Add-A-Ball**. The right saucer conveniently feeds this lane. [S3]
* **Specials:** stock game allows one replay; subsequent Specials reportedly become Add-A-Ball awards. Several Special routes exist, making Specials strategically relevant rather than merely cosmetic if stock rules are used. [S3]
* Maximum balls-to-play is operator adjustable to **6, 7, 8 or 9**, which can cap the runaway Add-A-Ball strategy. [S6] ([Pinside][9])
* No ball saver, kickback, video mode or mystery feature.

## What to watch

* **2× / 3× / 5× / 10× lamp:** immediately tells you the scoring leverage; at 10×, roulette and EOB values become huge.
* **5–9 Hearts lamps:** a nearly complete sequence can mean **two extra balls on one plunge/top feed**.
* **Flyaway targets physically standing up:** shows progress toward another multiplier advance / Spade sequence completion.
* **Balls-to-Play display:** unlike normal pinball, this can increase or decrease during the game. A roulette spin can visibly change the entire match.

## Important shots

| Shot                   | Position     | Advances                                 | Why now?                                | Risk                                        |
| ---------------------- | ------------ | ---------------------------------------- | --------------------------------------- | ------------------------------------------- |
| Hearts 5–9             | Top          | 2-ball sequence; multiplier              | Biggest survival payoff                 | Mostly uncontrolled top-lane access         |
| Flyaway bank           | Center       | Bonus X, spinner, chip value, Add-A-Ball | Core deterministic progression          | Direct target rebounds                      |
| Left spinner           | Left         | Value rises with Flyaway progress        | Strong scoring at high multiplier/value | Orbit/feed can return fast                  |
| Right saucer           | Right-center | Roulette; feeds Joker lane               | Wheel chance + easy Joker progress      | Roulette may **subtract a ball**            |
| Left saucer            | Left-center  | Roulette                                 | Wheel scoring / possible added ball     | Same random downside                        |
| Right orbit/Joker lane | Far right    | Jokers, Special progression              | Repeatable route to extra balls         | Crossover return geometry is unconventional |

## Match strategy

**Playing ahead:** Favor **deterministic Bonus X and controlled scoring**. A roulette spin is unusual because it can literally reduce remaining balls; avoid unnecessary wheel exposure if the lead is already enough. **Strategic inference.**

**Playing behind:** Added-ball routes become enormously valuable: sequence the Hearts for +2 balls, finish Spades in sequence, complete Jokers, and accept roulette variance. One successful endurance loop can turn a nearly finished game into several more balls. **Observed strategy.** [S3]

**Key recurring decision:** **Points versus balls.** Spending 25K on Sacrifice, shooting a low-value sequence lane, or risking roulette can look irrational on score alone but be correct if it repairs or creates another ball.

## Danger zones

* **Center Flyaway bank:** repeated direct attacks create rebounds through the open middle.
* **Crossover return lanes:** the lower-playfield geometry is counterintuitive; balls can arrive on the opposite side from where a commentator expects. Owner reports specifically call this a major control challenge. **Observed physical behavior.** ([Pinside][12])
* **Roulette saucers:** not necessarily dangerous physically, but strategically hazardous because the random result can remove a remaining ball.
* **Pop-bumper exits:** upper-card work feeds three widely spaced pops before returning to the flippers.
* **Right-side lane/outlane complex:** Joker/Special progress draws players toward the side of the playfield where an uncontrolled feed can become an outlane drain.

## Spoken commentary cues

* “This is an Add-A-Ball game—the number on the backglass is literally how many balls they still have.”
* “Those Hearts have to be made in sequence; finish all five correctly and that's **two more balls**.”
* “All five Flyaways are down—that raises the bonus multiplier even if they weren't hit in order.”
* “He's at ten-times bonus now; that's the scoring state Speakeasy players are trying to build.”
* “Sacrifice costs twenty-five thousand, but he's paying it to repair the card sequence.”
* “This roulette spin is not automatically good news—it can add a ball **or take one away**.”

## Trivia

* Speakeasy's playfield is a **green composite material rather than conventional plywood**. [S4] ([Pinside][1])
* The five center **Flyaway Targets** are unusual hinged targets: they disappear upward rather than dropping vertically. Bally reused the concept on *Grand Slam*. [S3] ([Pinside][10])
* The dedicated **Sacrifice button** is one of the stranger cabinet controls of its era: pressing it intentionally subtracts score to repair rules progress. [S1]
* Contemporary 1982 coverage specifically marketed the game around **sequential poker-card play**, not just the roulette gimmick. [S2] ([Atari Compendium][7])
* Bally made a separate **four-player Speakeasy 4**, while the normal Speakeasy is an unusual two-player Bally solid-state title. [S4][S5]

## Questions for the humans

### Tournament and venue checks

1. Which machine is actually present?
   A. **Two-player Speakeasy**
   B. Speakeasy 4
   C. Unknown

2. Which ROM is installed?
   A. **E877-3 / two-player Version 2**
   B. E877-2 / Version 1
   C. E877-4 / four-player
   D. Replacement/custom ROM
   E. Unknown

3. How will **Add-A-Balls** be handled?
   A. **Stock — all added/subtracted balls count**
   B. Added balls must be plunged/drained
   C. Added balls ignored/removed by tournament official
   D. Other
   E. Unknown

4. What is the configured maximum Balls to Play?
   A. 6
   B. 7
   C. 8
   D. 9
   E. Unknown

5. Which Hearts sequence adjustment is active?
   A. **5→9 only**
   B. 5→9 or 9→5
   C. Unknown

6. Is the roulette mechanism operating reliably?
   A. Yes
   B. Sometimes fails to spin/register
   C. Disabled
   D. Unknown

### Uncertainties and conflicts

* **Maximum bonus 119K:** this is explicitly reported by the tournament-focused Skill Shot guide [S3], and the factory-derived lamp chart [S1] confirms extensive bonus lamps through 60K plus 10× multiplier, but I did not obtain a readable Bally rule sheet that independently explains the exact **119K** arithmetic. Treat 119K as well-documented competitive guidance, not primary-source confirmed.
* **Bonus-X persistence:** [S3] clearly says base bonus persists and recommends achieving 10× “on each ball,” strongly implying multiplier reset each ball; I did not independently verify that reset behavior in a primary manual.
* **ROM Version 1 vs Version 2:** E877-2 and E877-3 are verified factory two-player ROM revisions [S5], but no trustworthy change log was found describing rule differences.
* **Tournament Add-A-Ball handling** is more consequential here than on almost any ordinary game. If added balls are disabled manually, the dominant stock strategy above changes substantially.
* Crossover-lane, saucer and pop feeds are highly setup-dependent.

## Human resolutions

1. Which machine is actually present?
   A. **Two-player Speakeasy**
   B. Speakeasy 4
   C. Unknown
   **Human answer:** A. **Two-player Speakeasy**

2. Which ROM is installed?
   A. **E877-3 / two-player Version 2**
   B. E877-2 / Version 1
   C. E877-4 / four-player
   D. Replacement/custom ROM
   E. Unknown
   **Human answer:** E. Unknown

3. How will **Add-A-Balls** be handled?
   A. **Stock — all added/subtracted balls count**
   B. Added balls must be plunged/drained
   C. Added balls ignored/removed by tournament official
   D. Other
   E. Unknown
   **Human answer:** E. Unknown

4. What is the configured maximum Balls to Play?
   A. 6
   B. 7
   C. 8
   D. 9
   E. Unknown
   **Human answer:** E. Unknown

5. Which Hearts sequence adjustment is active?
   A. **5→9 only**
   B. 5→9 or 9→5
   C. Unknown
   **Human answer:** e

6. Is the roulette mechanism operating reliably?
   A. Yes
   B. Sometimes fails to spin/register
   C. Disabled
   D. Unknown
   **Human answer:** A. Yes

## Sources

* **[S1] *Speakeasy technical charts* — PinWiki, transcribed from Bally documentation.** Lamps/switches, Bonus X values, card switches, Balls-to-Play display, roulette Add/Subtract-A-Ball and Sacrifice control.
  [PinWiki — Speakeasy](https://pinwiki.com/wiki/index.php/Speakeasy?utm_source=chatgpt.com)

* **[S2] *“Two-Player Pinball Game Has Card Game Theme” / Electronic Games contemporary coverage* — Bally marketing-derived 1982 sources.** 5–9 and 10–Ace sequences, Sacrifice cost, multiplier/spinner/chip progression, Joker lane and roulette.
  [Arcade Express contemporary text](https://vgpavilion.com/mags/1982/10/24ae/text/?utm_source=chatgpt.com)
  [Electronic Games February 1983 PDF](https://www.ataricompendium.com/archives/magazines/electronic_games/electronic_games_feb83.pdf?utm_source=chatgpt.com)

* **[S3] *Learn to Love Speakeasy* — Jawn Wakefield / Skill Shot, 2011.** Tournament-focused strategy; Add-A-Ball routes, sequence persistence, roulette behavior, Specials, 119K bonus, 10× strategy and multiplier interaction.
  [Skill Shot strategy guide](https://skill-shot.com/learn-to-love-speakeasy/?utm_source=chatgpt.com)

* **[S4] *Speakeasy Game Archive* — Pinside / Kineticist.** August 1982, model 1273, 3,000 production, creators, two-player hardware, composite playfield and Speakeasy 4 distinction.
  [Pinside Speakeasy details](https://pinside.com/pinball/machine/speakeasy/details?utm_source=chatgpt.com)

* **[S5] *Bally ROM Part Number Chart* — Action Pinball / PinRepair.** E877-2 Version 1, E877-3 Version 2, E877-4 four-player ROM identification.
  [Action Pinball ROM chart](https://www.actionpinball.com/tech/bally_id.php?utm_source=chatgpt.com)

* **[S6] *Speakeasy Game Adjustments* — Pinside technical discussion transcribing Bally DIP settings.** Maximum balls 6–9, top sequence direction and other strategically relevant adjustments.
  [Speakeasy adjustment reference](https://pinside.com/pinball/forum/topic/speakeasy-game-adjustments?utm_source=chatgpt.com)

[1]: https://pinside.com/pinball/machine/speakeasy/details?utm_source=chatgpt.com "Speakeasy Pinball Machine (Bally, 1982) | Pinside Game Archive"
[2]: https://pinwiki.com/wiki/index.php/Speakeasy?utm_source=chatgpt.com "Speakeasy - PinWiki"
[3]: https://skill-shot.com/learn-to-love-speakeasy/?utm_source=chatgpt.com "Learn to love Speakeasy – Skill Shot"
[4]: https://www.actionpinball.com/tech/bally_id.php?utm_source=chatgpt.com "Action Pinball - Bally ROM Part Number ID Chart"
[5]: https://www.pinrepair.com/bally/ballyrom.htm?utm_source=chatgpt.com "Bally Pinball CPU board ROM/Jumper list"
[6]: https://vgpavilion.com/mags/1982/10/24ae/text/?utm_source=chatgpt.com "Text - Arcade Express Oct 24, 1982 - VideoGame Pavilion"
[7]: https://www.ataricompendium.com/archives/magazines/electronic_games/electronic_games_feb83.pdf?utm_source=chatgpt.com "THE PLAYERS GUIDE TO COMPUTER GAMES"
[8]: https://skill-shot.com/learn-to-love-speakeasy/ "Learn to love Speakeasy – Skill Shot"
[9]: https://pinside.com/pinball/forum/topic/speakeasy-game-adjustments?utm_source=chatgpt.com "Speakeasy game adjustments | Tech: Early solid state | Pinside.com"
[10]: https://pinside.com/pinball/forum/search/page/45?page=60%3Fq%3Dswing&q=swing&s=1&utm_source=chatgpt.com "Forum search | Pinside.com"
[11]: https://www.pinwiki.com/wiki/index.php/Speakeasy?utm_source=chatgpt.com "Speakeasy - PinWiki"
[12]: https://pinside.com/pinball/top-100/comments/page/1551?page=2556&utm_source=chatgpt.com "Pinside Pinball Top 100 » Rating comments | Pinside Top 100"
