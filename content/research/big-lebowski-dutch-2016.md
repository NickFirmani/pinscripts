## Identity and versions

* **The Big Lebowski** — Dutch Pinball, **2016**. Design: **Barry Driessen and Koen Heltzel**; software: Heltzel; art: **Freek van Haagen and Jean-Paul de Win**. Multimorphic P3-ROC architecture, LCD, three flippers, upper mini-playfield and physical 10-pin bowling alley. [S1][S5] ([Dutch Pinball][1])
* This brief covers the **original Dutch Pinball production game**, not the later Jesus Edition. [S5]
* **Rules basis: `code` — v1.15, November 2024.** Dutch Pinball distributes gameplay updates by internet download/USB. The official changelog does **not publish an exact day**, so a `YYYY-MM-DD` release date cannot be responsibly supplied. v1.15 fixed a crash in *The Dude Abides* introduced in v1.14. [S1][S2] ([Dutch Pinball][2])
* The most important competitive multiballs are **Character Multiball** and the normal three-lock **Multiball**. **Nihilist Showdown** and the final **The Dude Abides** also contain major multiball scoring. [S2][S4]
* Research scope follows the supplied commentator-reference specification.

## Thirty-second game plan

1. **Observed/officially recommended strategy:** qualify **several characters before starting Character Multiball**. Dutch Pinball explicitly recommends starting it with as many qualified characters as possible: each adds scoring leverage and another ball, up to five balls total. [S4]
2. Before cashing that setup, collect useful **bowling balls**. Each character’s ball improves that character’s scoring and grants a persistent perk; a matching ball **doubles that character’s Character Multiball jackpots**. [S2][S4]
3. During any multiball, shoot the **upper mini-playfield ramp** for a rapidly decaying **1.5×–5× playfield multiplier**, then attack the prepared jackpots. [S2][S4]
4. Add a **White Russian** to a valuable character shot when possible; it provides several multiplied shots and survives between balls until consumed. [S4]
5. **Alternate line:** take the simpler three-lock regular Multiball—collect its six jackpots and then the Super Jackpot—rather than risking a long Character-Multiball setup. [S3][S4]

The core tournament decision is therefore **score a smaller multiball now, or keep building characters/balls/multipliers for a much larger one later**.

## Core rules and persistence

**Confirmed rule:** spell a character’s name to qualify that character for Character Multiball, then start it at the saucer. Starting with multiple characters is particularly valuable: balls = **1 + number of qualified characters, maximum five**. Characters added *after* multiball starts can add balls, but only those active **at the start** participate in the important cross-multiplication of jackpots. [S2][S4] ([Dutch Pinball][3])

**Regular Multiball:** hit the LIGHT/LOCK targets near the left ramp, then shoot the ramp to lock; **three locks** start multiball. Six main jackpots qualify the Super Jackpot. Current code limits regular-MB add-a-ball to **one per multiball**. [S2][S4]

Major leverage:

* **Mini-playfield ramp:** during all multiballs, awards a **1.5× through 5× playfield multiplier that rapidly decays**. [S2][S4]
* **Bowling balls:** character-specific multiplier/perk resources; they persist until *The Dude Abides*. [S2][S4]
* **White Russian:** complete the right target bank, then assign the drink to a blinking character shot; its remaining uses persist across balls. Current rules do **not** allow multiple White Russians to stack with each other. [S2][S4]
* **Mark It Zero:** normally timed. Walter’s bowling-ball perk makes it untimed and persistent across balls. Since v1.01, multiple Mark It Zeros cannot be simultaneously banked; completing ZERO while one is already lit instead gives points and refreshes the timer where applicable. [S2]

The six broad accomplishments lead to **The Dude Abides**. Phase 1 is single-ball and can continue after a drain; completing it starts the multiball phase. [S2][S3]

## Skill shots

| Skill shot                      | How                                                                                | Award / why choose it                                                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **MAUDE / normal skill shot**   | Normal plunge through the flashing top lane; flippers lane-change the lit lane     | Advances MAUDE/top-lane progress and is the lowest-commitment plunge.                                                         |
| **Rug Mode Skill Shot**         | **Hold left flipper** while launching, then hit the Rug within about **5 seconds** | Immediately opens the Rug hole, putting the first Rug mode one shot away.                                                     |
| **Let’s Go Bowling Skill Shot** | **Hold right flipper** while launching to the upper playfield, then make its ramp  | Immediately lights **Let’s Go Bowling** at the start shots; strategically strong when chasing a bowling-ball multiplier/perk. |

These are documented in the official manual/flowchart. No verified ball-number scaling was found. [S3][S4] ([Dutch Pinball][4])

## Secondary features

* **Kickback:** the left outlane can be protected by a lit kickback; after use, the **Trampoline** target can relight it. A failed kickback receives a short saver in current rules. [S2][S4]
* **ZERO outlane save:** if an outlane switch completes ZERO and would otherwise drain, current code can return the ball unless the kickback already handles it. [S2]
* **Mystery:** spinner progress lights Mystery at the scoop. In a **Tournament Game**, mystery is not random: awards follow a fixed order by level. Possible normal-game awards include ball saver, multiball, bowling-ball and large point awards. [S2]
* **Extra ball:** can be lit from Rug-mode or Mark-It-Zero milestones; required counts are adjustment-sensitive. No universal tournament point-conversion value was verified. [S2][S4]
* **Player controls:** flippers lane-change MAUDE/ZERO and select bowling choices; the launch button controls bowling-ball release and can be relevant when choosing among simultaneously available saucer awards. [S4]
* **Video mode:** none found. Bowling is a physical mini-playfield feature, not a video mode.

## What to watch

1. **Several character qualifications lit:** the player may deliberately be refusing Character Multiball because a larger starting stack scores substantially better. [S4]
2. **Collected bowling-ball indicators:** these identify which characters now have an enhanced jackpot plus their special perk; a matching ball is especially meaningful before Character Multiball. [S2][S4]
3. **Player shoots upstairs during multiball:** the mini-playfield ramp is probably not a detour—it can bring the whole playfield as high as **5×**, but the multiplier falls quickly. [S2]
4. **Rug rolls back and exposes its hole:** a Rug mode or the Rug double-jackpot opportunity is ready to be cashed. [S1][S4]

## Important shots

| Shot                    | Position               | Advances                                        | Why now?                                                          | Risk                                                                                                 |
| ----------------------- | ---------------------- | ----------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Left saucer**         | Far left / left-center | Character MB, Mark It Zero and other lit starts | Converts accumulated setup into a mode/multiball                  | Eject quality is setup-sensitive.                                                                    |
| **Donny orbit**         | Left orbit             | DONNY / character jackpot                       | Character qualification and lucrative MB shot                     | **Observed:** some games send this return dangerously toward center; guide/level sensitive. [S7][S8] |
| **Dude / left ramp**    | Left-center            | DUDE; locks; regular-MB Super Jackpot           | Central normal-MB route                                           | **Observed:** marginal shots can roll back/reject. [S7]                                              |
| **Rug**                 | Center                 | Rug modes; Rug MB jackpot                       | Opens hidden hole; potentially double jackpot in regular MB       | Bash returns are inherently less predictable.                                                        |
| **Mini-playfield ramp** | Upper playfield        | BOWLING; multiball playfield X                  | During MB this can be the highest-leverage setup shot on the game | Requires giving up immediate lower-playfield jackpots while X decays.                                |
| **White Russian bank**  | Far right              | White Russian multiplier                        | Prepare multiplied uses on an important character shot            | Stand-up target attack sacrifices flow/control.                                                      |

Physical-risk observations are machine-sensitive rather than universal rules. [S7][S8] ([Pinside][5])

## Match strategy

**Playing ahead:** **Strategic inference:** cash a reasonably prepared Character Multiball rather than stretching for every character; use existing bowling balls/White Russian value, protect the kickback, and take the mini-playfield multiplier only when the return is comfortable.

**Playing behind:** **Strategic inference:** delay Character Multiball for more simultaneous characters and matching bowling balls, prepare a White Russian, then attack the mini-ramp for a high playfield multiplier before cashing jackpots. Already-developed **Nihilist Showdown** is also high variance: later waves carry escalating jackpots and can award another ball after a completed wave. [S2][S4]

A separate swing opportunity is **Bowling Super Jackpot**: after ten frames it pays **bowling score × 25,000**, so a perfect 300 game is **7.5M**—large enough to matter even though bowling is not the simplest tournament route. [S2]

**Key recurring decision:** **start Character Multiball now versus continue setup.** More characters dramatically improve its ceiling, but every extra prerequisite risks draining without realizing any of that investment.

## Danger zones

* **Donny / left-orbit return:** repeatedly reported as capable of feeding near straight-down-the-middle on some setups; highly leveling/guide dependent. [S7][S8]
* **Left-ramp rollback:** a weak or partial Dude/lock shot can come back unexpectedly fast. [S7]
* **Rug bash:** direct strikes into the central moving toy can generate awkward rebounds rather than a controlled return. [S7]
* **Multiplier greed:** not a physical defect, but strategically dangerous—the upper-playfield X decays quickly, so a failed upstairs attempt can consume most of the value before any jackpot is made. [S2]

## Spoken commentary cues

* “They’re intentionally leaving Character Multiball ready—the more characters they bring in at the start, the bigger that multiball gets.”
* “That bowling ball isn’t just a collectible; it boosts this character and doubles the matching Character-Multiball jackpot.”
* “They’ve gone upstairs for the playfield multiplier—this can reach five-times, but it starts bleeding away immediately.”
* “The White Russian is loaded on that character shot, so they’ve got a limited number of multiplied cash-outs there.”
* “Three locks is the simpler route: six jackpots, then the regular Multiball Super.”
* “The Rug is open now—that hidden hole is the mode start they’ve been setting up.”

## Trivia

* Dutch Pinball built an actual **Brunswick-style 10-pin bowling alley** into the lower playfield rather than representing bowling only on the LCD. [S1] ([Dutch Pinball][1])
* The center **Rug physically rolls away** to reveal a hidden hole—an unusually literal implementation of the movie’s most famous object. [S1]
* The game contains **more than 200 movie quotes and clips** according to Dutch Pinball. [S1]
* Initial production code dates to **2016**, but the fully implemented *The Dude Abides* wizard mode did not arrive until **v1.00 in October 2022**. [S2]
* Code v1.10 added a dedicated **Tournament Game** in which Mystery awards use fixed sequences instead of randomness. [S2]

## Questions for the humans

### Edition and configuration checks

1. The official v1.15 changelog gives only **November 2024**, not an exact release day. How should the final binder represent the required code date?
   A. **`v1.15 — 2024-11 (exact day unverified)`**
   B. Omit the date until a primary source with the exact day is found
   C. Human editor has an official dated release announcement/download record

### Uncertainties and conflicts

1. Extra-ball thresholds are operator-adjustable, and I found no authoritative universal **tournament point-conversion value**.
   A. Mention only that extra balls may be disabled/converted by tournament configuration
   B. Omit extra balls from the final one-page sheet
   C. Human editor has a confirmed current competition-mode conversion rule

2. The official v1.00 manual predates several material changes in **v1.01+**—most notably Mark It Zero banking and regular-Multiball add-a-ball limits. This brief uses the later changelog as authoritative where they conflict. [S2][S4]
   A. Keep that current-code interpretation
   B. Binder is intentionally documenting an older software revision

## Human resolutions

1. The official v1.15 changelog gives only **November 2024**, not an exact release day. How should the final binder represent the required code date?
   A. **`v1.15 — 2024-11 (exact day unverified)`**
   B. Omit the date until a primary source with the exact day is found
   C. Human editor has an official dated release announcement/download record
   **Human answer:** A. **`v1.15 — 2024-11 (exact day unverified)`**

1. Extra-ball thresholds are operator-adjustable, and I found no authoritative universal **tournament point-conversion value**.
   A. Mention only that extra balls may be disabled/converted by tournament configuration
   B. Omit extra balls from the final one-page sheet
   C. Human editor has a confirmed current competition-mode conversion rule
   **Human answer:** A. Mention only that extra balls may be disabled/converted by tournament configuration

2. The official v1.00 manual predates several material changes in **v1.01+**—most notably Mark It Zero banking and regular-Multiball add-a-ball limits. This brief uses the later changelog as authoritative where they conflict. [S2][S4]
   A. Keep that current-code interpretation
   B. Binder is intentionally documenting an older software revision
   **Human answer:** A. Keep that current-code interpretation

## Sources

* **[S1] — The Big Lebowski Pinball Machine — Dutch Pinball.** Manufacturer product/support/download page. Identity, hardware, current v1.15 availability, physical features. [Dutch Pinball game page](https://dutchpinball.com/games/the-big-lebowski?utm_source=chatgpt.com)
* **[S2] — The Big Lebowski Software Changelog — Dutch Pinball.** Official code notes. v1.15, Tournament Game, v1.00–1.01 rules changes, multipliers, bowling, mystery, ball saves, wizard mode. [Official software changelog](https://suite.dutchpinball.com/thebiglebowski/software/changelog?utm_source=chatgpt.com)
* **[S3] — The Big Lebowski Rules Flowchart — Dutch Pinball.** Official current rules diagram. Skill shots, wizard goals, Character MB, Bowling, Mystery, regular MB. [Official rules flowchart PDF](https://cms.dutchpinball.com/uploads/TBL_Pinball_Rules_Flowchart_913244f3cf.pdf?utm_source=chatgpt.com)
* **[S4] — The Big Lebowski Rules Manual v1.00 — Dutch Pinball.** Official detailed rules manual; superseded by later changelog where noted. Qualification, skill shots, multipliers, multiballs, persistence, bowling, Rug/Car/Nihilist modes. [Rules manual PDF](https://o.pinside.com/5/a1/23/5a12309de75fd7d1c3e64fce697f22edaf29a8fc.pdf?utm_source=chatgpt.com)
* **[S5] — The Big Lebowski Machine Details — Pinside.** Reference database. Year, credits, platform and major hardware. [Pinside machine archive](https://pinside.com/pinball/machine/big-lebowski/details?utm_source=chatgpt.com)
* **[S7] — The Big Lebowski: Delivery Fiasco and First Impressions — Pinside.** Player/owner observations. Physical shot feeds, left-ramp behavior and Rug returns; used only for machine-sensitive danger notes. [Pinside observations thread](https://pinside.com/pinball/forum/topic/the-big-lebowski-delivery-fiasco-and-first-impressions?utm_source=chatgpt.com)
* **[S8] — The Big Lebowski Official Club Thread — Pinside.** Owner/manufacturer discussion. Corroborates setup sensitivity of the left-orbit feed. [Pinside owners thread](https://pinside.com/pinball/forum/topic/the-big-lebowski-official-club-thread/page/5?utm_source=chatgpt.com)

[1]: https://dutchpinball.com/games/the-big-lebowski?utm_source=chatgpt.com "The Big Lebowski Pinball Machine | Dutch Pinball"
[2]: https://dutchpinball.com/games/the-big-lebowski "The Big Lebowski Pinball Machine | Dutch Pinball"
[3]: https://dutchpinball.com/tbl/changelog "The Big Lebowski™ Pinball changelog"
[4]: https://cms.dutchpinball.com/uploads/TBL_Pinball_Rules_Flowchart_913244f3cf.pdf "Print"
[5]: https://pinside.com/pinball/forum/topic/the-big-lebowski-delivery-fiasco-and-first-impressions?utm_source=chatgpt.com "The Big Lebowski: delivery fiasco and first impressions | All Pinball | Pinside.com"
