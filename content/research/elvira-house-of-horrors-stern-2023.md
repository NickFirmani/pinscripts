## Identity and versions

* **Elvira’s House of Horrors — Blood Red Kiss Edition**, Stern, **2023**, based on the 2019 game. Design: **Dennis Nordman**; software/rules: **Lyman F. Sheats Jr.**; art: **Greg Freres**; engineering/mechanics: **Tom Kopera**; callouts include **Cassandra Peterson** and Tim Kitzrow. SPIKE 2 platform. [S1][S3] ([Kineticist][1])
* Blood Red Kiss was limited to **500 games**. Its differences are principally cosmetic/presentation—red-sparkle playfield/art, black-sparkle armor, dagger shooter knob, signed card, unique attract/start presentation. I found **no separate competitive ruleset** for it. [S2][S3] ([Stern Pinball][2])
* **Rules basis: `code` — v1.12.0, released 2026-07-01.** v1.12 is system-focused; the latest major gameplay change is v1.11.0 (2024-12-23), which substantially completed **Wild Market Value**. [S3] ([Pinside][3])
* Important multiballs: **Wild Women, Add-a-Zombie, Attic Attack** (Garage); **Trunk Multiball / Phone-a-Fiend**; plus Haunt wizard multiballs **House Party** and **They Came From Space**. [S4]
* Research scope follows the supplied commentator-reference specification.

## Thirty-second game plan

1. **Observed strategy:** get a **Haunt** running, then layer a prepared **Garage or Trunk multiball** underneath it. Haunts explicitly stack with multiball. [S4][S5] ([TiltForums][4])
2. Prepare **Double Trouble** by completing both target banks, but trigger its inlane only when the scoring window is ready: 2× playfield for 30 seconds; qualifying it again while active produces **4×**. [S4]
3. Complete the Haunt, then maximize **Trailer Trash**: shoot both ramps before the House to raise the cash-out from 50% → 75% → **100% of the Haunt score**. Double Trouble multiplies that collect, making this a major tournament swing. [S4][S6] ([Pinside][5])
4. Use **Atomic Rayguns** to spot difficult mode shots rather than risking dangerous precision shots; Skeleton Keys unlock additional Haunts. [S4]
5. **Alternate strategy:** build the relatively straightforward Garage multiballs and jackpot/super-jackpot cycles rather than committing to deep Haunt progression. [S4][S5]

## Core rules and persistence

**Haunts:** repeated House shots qualify a Haunt; when the House flashes purple, the next House shot starts one. Normal Haunts begin with **45 seconds**. Progress shots made below 15 seconds restore the timer to 15; the timer pauses while the ball is in the pops. A failed/timed-out Haunt normally cannot be replayed before *They Came From Space*. [S4]

Completing a Haunt advances **B-Restorator** progress toward **Director’s Cut** and qualifies Trailer Trash. After four completed Haunts, Director’s Cut lets the player re-collect values derived from those finished Haunts; completion awards **100M**. [S4][S3]

**Trailer Trash:** starts at 50% of the completed Haunt’s score. One ramp increases it to 75%; both ramps to 100%; collect at the House. It can remain active during multiball and is affected by playfield X. [S4][S6]

**Double Trouble:** complete both the Trunk and Hand-of-Fate target banks, then roll through the lit inlane for **2× scoring / 30s**. Requalify and start it while active for **4×**; target-bank completions can extend its timer. [S4]

**Current stacking caveat:** Garage and Trunk multiballs can each be layered with Haunts, but current code does **not** allow Trunk MB and Garage MB to be started on top of one another. [S3][S4] ([Pinside][6])

Deep progression ends in **Wild Market Value**. On v1.11+, it is a six-stage wizard mode: initial market-value hurry-up, four multiball jackpot stages whose scoring rises with balls in play, then a Final Super Jackpot. Double Trouble is disabled inside the mode. [S3] ([Pinside][3])

## Skill shots

| Skill shot                                  | How                                             | Award / strategic use                                                                                                                            |
| ------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Dead End Skill Shot**                     | Plunge into either lit Dead End top lane        | 250K + increment and **+5× bonus multiplier**. Safe value when not forcing progression.                                                          |
| **Back Door / Super Secret Unskilled Shot** | Soft plunge so the ball enters behind the House | 1M + increment; **immediately qualifies a Haunt**, or starts it if already qualified. During an active Haunt/Gappa Angry it spots mode progress. |

Both are verified rules; v1.10 added clearer lamp effects for skill shots. [S4][S3] ([TiltForums][4])

## Secondary features

* **Atomic Raygun / action button:** collected through Junk in the Trunk. The button spots a lit shot in the most recently started mode; it is especially useful for avoiding the hardest Haunt shot. Rayguns cannot simply collect Trailer Trash. [S4]
* **Pew Pew Pew:** current code feature. Collect/use three Rayguns, then shoot the lit left-ramp/trunk shot; switches become a timed scoring frenzy. [S3] ([Pinside][3])
* **Return:** defeating a Deadhead lights a **right-outlane save**. [S4]
* **Hand of Fate:** complete its target bank, then drain through the lit **left outlane**. A display wheel appears and the player stops it with the lockdown-bar button. Awards include ball save, multiball extensions, points and **Double Bone-Us**. This is player-controlled, not merely a random consolation award. [S4]
* **Extra balls:** two completed Haunts or two defeated Deadheads can light one at the House. Stern’s current Competition install explicitly sets **NO EXTRA BALLS**. [S3][S4] ([Pinside][3])

## What to watch

1. **House flashing purple:** a Haunt is qualified; a House shot now starts the mode. [S4]
2. **Double Trouble inlane lit / 2× or 4× running:** the player has entered the game’s primary multiplier window; expect immediate cash-out attempts. [S4]
3. **Trailer Trash after a completed Haunt:** watch the ramps. Zero / one / two ramp “bits” means a 50% / 75% / 100% Haunt-value collect at the House. [S4]
4. **Physical Garage or Trunk setup:** a player refusing an available multiball is often intentionally waiting to start a Haunt first. [S4][S5]

## Important shots

| Shot                  | Position     | Advances                                 | Why now?                                            | Risk                                                     |
| --------------------- | ------------ | ---------------------------------------- | --------------------------------------------------- | -------------------------------------------------------- |
| **House Entrance**    | Center       | Haunts, Trailer Trash, many supers       | Central qualify/start/cash-out shot                 | Misses/rejects return centrally and can destroy control. |
| **Left ramp / Trunk** | Left-center  | Junk awards, Trunk locks, Trailer Trash  | Builds utility items and MB; Trailer Trash ramp bit | Partial ramp/re-entry is setup-sensitive.                |
| **Garage**            | Center-left  | Wild Women → Add-a-Zombie → Attic Attack | Main repeatable multiball route                     | Gravestone/drop-target misses rebound into open play.    |
| **Right ramp**        | Right-center | Trailer Trash, Haunt shots               | Second ramp needed for 100% Trailer Trash           | Rejects can return quickly to the flippers.              |
| **Crypt**             | Far right    | Deadheads / Return ball save             | Survival utility and Wild Market progression        | VUK eject is famously machine-sensitive.                 |
| **Hand-of-Fate bank** | Right side   | Double Trouble + Hand of Fate            | Helps arm 2×/4× and eventual wheel                  | Stand-up rebounds sacrifice control.                     |

## Match strategy

**Playing ahead:** **strategic inference:** cash Trailer Trash at 75–100% rather than extending a scoring setup unnecessarily; use prepared multiball for protection, and favor the normal Dead End plunge over a difficult Back Door attempt on a hostile machine.

**Playing behind:** pursue the full **Haunt + multiball + 4× Double Trouble** stack, then finish the Haunt and collect 100% Trailer Trash while X is still running. Documented owner/tournament play shows Trailer Trash itself can become a several-hundred-million-point swing when multiplied. [S5][S6]

**Key recurring decision:** **take the multiball now or save it for a Haunt?** Immediate multiball gives safety and modest jackpots; delaying it creates the much larger—but riskier—mode/multiball/multiplier stack.

## Danger zones

* **Crypt VUK eject:** documented machines vary from controlled returns to left-outlane/center danger; highly setup-sensitive. [S7] ([Pinside][7])
* **Right-orbit feed:** some setups send the ball toward the sling rather than cleanly to a flipper. [S7] ([Pinside][8])
* **Pop-bumper exit:** owners document straight-down-the-middle exits; control can disappear abruptly after a safe-looking House feed. [S7]
* **Garage/drop-target rebounds:** center-left target work can produce lateral or center movement instead of a controlled feed.
* **Target-bank greed for 4×:** strategically dangerous because the standups needed to requalify Double Trouble are less controlled than simply taking an already-large Haunt/Trailer Trash value.

## Spoken commentary cues

* “They’ve got the Haunt running—now they’re trying to bring the multiball underneath it.”
* “Double Trouble is armed; they’re waiting to roll that inlane until the scoring window is ready.”
* “One Trailer Trash ramp makes this 75 percent; both ramps makes the House worth the full Haunt again.”
* “That second Double Trouble activation is the big one—now the whole playfield is four-times.”
* “They’re saving the Raygun for the ugly mode shot rather than spending it on an easy collect.”
* “The multiball is available, but starting it now would give up the better Haunt stack.”

## Trivia

* *House of Horrors* is the **third Stern/Bally-era Elvira pinball**, following *Elvira and the Party Monsters* and *Scared Stiff*. [S1]
* Stern filmed **new Cassandra Peterson/Elvira video specifically for the game**, unusual for a licensed pinball production. [S1]
* Blood Red Kiss was limited to **500 units** and uses red sparkle printing throughout plus Elvira’s tattoo motif in the cabinet treatment. [S2]
* The BRK launch coincided with substantial new 2023 code including **Pew Pew Pew**, additional Elvira speech and later the Eegah Haunt. [S2][S3]
* Nearly five years after the original game release, **v1.11 (2024-12-23)** substantially expanded the final Wild Market Value wizard into its present six-stage structure. [S3]

## Questions for the humans

### Edition and configuration checks

1. Which rules environment should the final sheet assume?
   A. **Current v1.12 with Stern Competition install**
   B. Current v1.12, normal settings
   C. Keep configuration-neutral and flag tournament-sensitive rules only

2. Competition install disables extra balls and changes several difficulty/safety settings, including Garage-lock difficulty and some ball saves. Should the final one-pager:
   A. Assume Competition behavior throughout
   B. Describe factory gameplay and leave tournament setup to venue notes
   C. Mention only the strategically large differences

### Uncertainties and conflicts

1. **Physical feeds are highly setup-sensitive.** Crypt VUK, right-orbit and pop exits have documented machine-to-machine variation. [S7] These belong more naturally in venue notes than universal rules.
   A. Keep generic warnings on the game page
   B. Move all physical-feed commentary to venue notes

2. The maintained community rulesheet [S4] originated on older code and still contains some incomplete feature descriptions. This brief uses Stern’s later changelog [S3] as authoritative whenever newer code explicitly changes those rules.

## Human resolutions

1. Which rules environment should the final sheet assume?
   A. **Current v1.12 with Stern Competition install**
   B. Current v1.12, normal settings
   C. Keep configuration-neutral and flag tournament-sensitive rules only
   **Human answer:** A. **Current v1.12 with Stern Competition install**

2. Competition install disables extra balls and changes several difficulty/safety settings, including Garage-lock difficulty and some ball saves. Should the final one-pager:
   A. Assume Competition behavior throughout
   B. Describe factory gameplay and leave tournament setup to venue notes
   C. Mention only the strategically large differences
   **Human answer:** A. Assume Competition behavior throughout

1. **Physical feeds are highly setup-sensitive.** Crypt VUK, right-orbit and pop exits have documented machine-to-machine variation. [S7] These belong more naturally in venue notes than universal rules.
   A. Keep generic warnings on the game page
   B. Move all physical-feed commentary to venue notes
   **Human answer:** A. Keep generic warnings on the game page

2. The maintained community rulesheet [S4] originated on older code and still contains some incomplete feature descriptions. This brief uses Stern’s later changelog [S3] as authoritative whenever newer code explicitly changes those rules.
   **Human answer:** ok

## Sources

* **[S1] — Elvira’s House of Horrors — Stern Pinball.** Manufacturer game page; theme, editions and production presentation. [https://wp.sternpinball.com/game/elviras-house-of-horrors/](https://wp.sternpinball.com/game/elviras-house-of-horrors/?utm_source=chatgpt.com)
* **[S2] — Stern Pinball Celebrates the Hostess with the Mostess, Elvira — Stern Pinball, 2023-10-19.** Manufacturer announcement; Blood Red Kiss production/cosmetics and 2023 feature update. [https://www.sternpinball.com/2023/10/19/stern-pinball-celebrates-the-hostess-with-the-mostess-elvira-%F0%9F%92%8B/](https://www.sternpinball.com/2023/10/19/stern-pinball-celebrates-the-hostess-with-the-mostess-elvira-%F0%9F%92%8B/?utm_source=chatgpt.com)
* **[S3] — Elvira’s House of Horrors software changelog — Stern readme mirrored by Pinside.** Primary-derived code history; v1.12 date, v1.11 Wild Market Value, v1.07–1.10 changes, Competition install. [https://pinside.com/pinball/machine/elviras-house-of-horrors-premium/details](https://pinside.com/pinball/machine/elviras-house-of-horrors-premium/details?utm_source=chatgpt.com)
* **[S4] — Elvira’s House of Horrors Rulesheet — Tilt Forums.** Detailed community rules documentation; Haunts, skill shots, Trailer Trash, Double Trouble, multiballs, Junk, Hand of Fate and persistence. [https://tiltforums.com/t/elvira-s-house-of-horrors-rulesheet/5815](https://tiltforums.com/t/elvira-s-house-of-horrors-rulesheet/5815?utm_source=chatgpt.com)
* **[S5] — Elvira’s House of Horrors Rules & Shot Guide — Pinball Genie.** Current strategy/rules synthesis; tournament stacking route, 4× strategy, Trailer Trash and important shot selection. [https://pinball-genie.com/machines/elvira](https://pinball-genie.com/machines/elvira?utm_source=chatgpt.com)
* **[S6] — Elvira’s House of Horrors Owners Club strategy discussion — Pinside.** Experienced-player evidence that Double Trouble multiplies Trailer Trash and that this can create very large tournament scoring swings. [https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/179](https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/179?utm_source=chatgpt.com)
* **[S7] — Elvira’s House of Horrors Owners Club technical/playfield discussions — Pinside.** Used only for machine-sensitive Crypt VUK, orbit and drain behavior. [https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/305](https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/305?utm_source=chatgpt.com)

[1]: https://www.kineticist.com/games/pinball/elviras-house-of-horrors-2019?utm_source=chatgpt.com "Elvira's House of Horrors Pinball Machine (2019) by Stern Pinball Inc."
[2]: https://www.sternpinball.com/2023/10/19/stern-pinball-celebrates-the-hostess-with-the-mostess-elvira-%F0%9F%92%8B/?utm_source=chatgpt.com "Stern Pinball Celebrates the Hostess with the Mostess, Elvira 💋 – Stern Pinball"
[3]: https://pinside.com/pinball/machine/elviras-house-of-horrors-premium/details "Elvira's House of Horrors (Premium Edition) Pinball Machine (Stern, 2019) | Pinside Game Archive"
[4]: https://tiltforums.com/t/elvira-s-house-of-horrors-rulesheet/5815?utm_source=chatgpt.com "Elvira’s House of Horrors Rulesheet - Wiki Rulesheets - Tilt Forums"
[5]: https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/179?utm_source=chatgpt.com "Elvira's House of Horrors - The Owner's Club | All clubs (...members only!) | Pinside.com"
[6]: https://pinside.com/pinball/machine/elviras-house-of-horrors-40th-anniversary/details?utm_source=chatgpt.com "Elvira's House of Horrors (40th anniversary edition) Pinball Machine (Stern, 2021) | Pinside Game Archive"
[7]: https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/36?hl=turbo2nr&utm_source=chatgpt.com "Elvira's House of Horrors - The Owner's Club | All clubs (...members only!) | Pinside.com"
[8]: https://pinside.com/pinball/forum/topic/elvira-s-house-of-horrors-the-owner-s-club/page/306?hl=burgertime79&utm_source=chatgpt.com "Elvira's House of Horrors - The Owner's Club | All clubs (...members only!) | Pinside.com"
