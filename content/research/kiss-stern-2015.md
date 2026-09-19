## Identity and versions

* **KISS**, Stern, **2015**, SPIKE/DMD platform. Design: **John Borg**; software: **Lonnie D. Ropp, Mike Kyzivat, Tanio Klyce, Waison Cheng**; art: **Kevin O’Connor**; mechanics: **Robert Blakeman**; sound: **Bob Baffy**. [S1][S2] ([Stern Pinball][1])
* **Rules basis: `code` — v1.41.0, released 2018-12-11.** This is the final verified public release; v1.40 was the major late rules rewrite, while v1.41 mainly added competition virtual locks, tuning and polish. [S2] ([Pinside][2])
* The requested model is **underspecified under the supplied catalog convention**. **Pro must be a separate entry from Premium/LE**: Premium/LE have physical Demon locks, KISS drop targets, the Starchild drop target/levitating-ball transfer and different Love Gun startup behavior; Pro uses standups/virtual behavior instead. Premium and LE are gameplay-equivalent. [S1][S6] 
* Core major multiballs/wizards: **Love Gun Multiball, Demon Multiball, Heaven’s on Fire, KISS Army, Rock City**. [S3] ([Pinball Rule Sheets][3])

Research scope follows the supplied commentator-reference specification. 

## Thirty-second game plan

1. **Observed strategy:** finish an easy song—commonly **Deuce**—as quickly as possible. One completed song gives **2× playfield for the rest of the ball**; further same-ball completions raise that to **3×, 5×, then 10×**. This is the central tournament scoring engine. [S3][S4] ([Kineticist][4])
2. Immediately shoot **Backstage Pass** after completing a song to start another; long balls compound enormously because the playfield X keeps climbing. [S4] ([Kineticist][4])
3. Prepare **Love Gun MB** through STAR while playing the song. Bring an active song into multiball; Love Gun is often more useful as mode protection than for its early jackpots. [S4][S5] ([JLP's Pinball Cards][5])
4. Later, **Demon MB** is the steadier scoring multiball. Locking one/two balls back into Gene during MB adds timed **2×/3× Demon playfield X**, additive with song X. [S3][S4] ([Pinball Rule Sheets][3])
5. **Alternate/deep route:** deliberately collect instruments via the right ramp and finish the center grid for **Heaven’s on Fire**, a very lucrative mini-wizard—especially with playfield X already running. [S3][S4] ([Kineticist][4])

## Core rules and persistence

Songs are untimed shot sequences. Progress **carries between balls**, but their scoring resets; the real reward is completion. On default/current play, song completions during the **same ball** award 2× → 3× → 5× → 10× playfield for the remainder of that ball. An adjustment can alter multiplier persistence, so do not assume it survives a drain. [S2][S3] ([Pinside][6])

Songs may run through multiball, but **must be started before the multiball**; you cannot normally select/start another during MB. This explains why strong players often finish a song, start the next one at Backstage Pass, *then* start multiball. [S3][S4] ([Pinball Rule Sheets][3])

**Shot X:** completing and collecting both KISS and ARMY hurry-ups lights all major shots; the next major shot becomes **2× for the rest of the ball**. This combines multiplicatively with combo X and the overall playfield multiplier. [S2][S3] ([Pinball Rule Sheets][7])

**Demon MB:** all six main shots can score two jackpots; the sixth and twelfth become Supers, followed by a roving Double Jackpot and a Double Super at Gene. During MB, relight Demon and lock one ball for **2×** playfield or a second for **3×**, normally 20 seconds. That X is **additive** with song X: e.g. 10× song + 3× Demon = 13× playfield. [S3][S4] ([Pinball Rule Sheets][3])

**Love Gun MB:** qualify through STAR. After its initial hurry-up, each jackpot shot must be repeated immediately for its Double Jackpot; clear the set → right-ramp Triple → **50M base Super at STAR**. Pro and Prem/LE handle the initial captive/add-a-ball phase differently. [S3][S4] ([Pinball Rule Sheets][3])

Grid progress toward **Heaven’s on Fire** carries between balls. The grid comprises KISS, ARMY, four bumpers and four instruments; instruments are the element that usually requires deliberate work. [S3][S4] ([Pinball Rule Sheets][3])

## Skill shots

**None found.** Current v1.41 has no formal skill shot. [S3][S4][S5] ([Pinball Rule Sheets][3])

A soft plunge can sometimes delay the left/right orbit switch long enough for the eventual rollback to count as an orbit shot; this is a useful plunge technique, **not a programmed skill shot**. [S4] ([Kineticist][4])

## Secondary features

* **Front Row:** repeated KISS completions light a virtual save on the **left outlane**; requirements rise after each use. [S3][S4] ([Pinball Rule Sheets][3])
* **Backstage Pass:** completing both KISS and ARMY lights Mystery at the scoop. During multiball it becomes an **add-a-ball once the ball saver has expired**; if collected while the saver still runs, v1.40 instead gives 2M and relights itself. [S2][S3] ([Pinside][2])
* Single-ball Backstage awards include **Super Ramps, Super Spinner, Super Targets, Super Pops, Super Scoring, shot-X, Bonus X and Hold Bonus**. Competition uses an organized award sequence rather than completely unconstrained normal randomness, but I did not find a concise authoritative v1.41 sequence table. [S2][S3] ([Pinside][2])
* **Extra Ball:** default current code can light one after **5 City Combos**; instrument progress can also qualify one. Tournament handling is adjustment-dependent. [S2][S3] ([Pinside][2])
* No action button or conventional video mode was verified.

## What to watch

1. **2X / 3X / Colossal lamps:** tells you immediately how much same-ball song leverage the player has built. At 5×/10×, ordinary-looking shots can decide the game. [S4] ([Kineticist][4])
2. **Purple Love Gun arrow / STAR progress:** Love Gun is ready; if a song is nearly complete, expect the player to delay MB until the multiplier is secured. [S3][S4]
3. **White shot-X arrows:** the next shot made will become permanently doubled for the ball. [S3]
4. **Center 16-light grid:** missing bottom-row instrument lights usually explains why the player keeps shooting the difficult right ramp. [S4] ([Kineticist][4])

## Important shots

| Shot                     | Position     | Advances                              | Why now?                               | Risk                                      |
| ------------------------ | ------------ | ------------------------------------- | -------------------------------------- | ----------------------------------------- |
| **STAR / Starchild**     | Upper-left   | Love Gun, modes                       | Easiest MB path; many song shots       | Chaotic mini-area; Pro/Prem feeds differ  |
| **Backstage Pass scoop** | Left-center  | New song, Mystery/add-a-ball, wizards | Essential after every song completion  | Tight; safer as a backhand on many games  |
| **Center ramp**          | Center       | Songs, combos, bumper feed            | Safest repeatable mode/2×-combo vector | Weak rejects can come quickly down center |
| **Demon / Gene**         | Center-right | Locks, Demon MB, instrument           | Steadier multiball scoring route       | Spinning disc/eject can return SDTM       |
| **Right ramp**           | Right-center | Love Gun start, instruments           | Critical for grid/Heaven’s on Fire     | Commonly one of the hardest shots         |
| **KISS / ARMY banks**    | Lower sides  | Hurry-ups, shot-X, Backstage          | Permanent ball-long shot multiplier    | Banks are angled toward opposite outlanes |

[S3][S4] ([Kineticist][4])

## Match strategy

**Playing ahead:** **strategic inference:** prioritize an easy song completion and stable 2×/3× playfield, take the accessible Love Gun protection, and avoid attacking KISS/ARMY standups merely for another shot multiplier if the outlane risk outweighs the value.

**Playing behind:** extend the ball at all costs: finish multiple songs for **5×/10×**, start a fresh mode before multiball, then pursue Demon’s additional 2×/3× or a deep Love Gun Super. Heaven’s on Fire under a large playfield X is another documented nine-figure opportunity. [S4] ([Kineticist][4])

**Key recurring decision:** **cash the ready multiball now, or risk finishing/starting another song first?** The extra song can turn the entire multiball from 1× into 2×/3×/5× scoring, but draining during setup forfeits that ball’s multiplier window.

## Danger zones

* **KISS/ARMY banks:** strong hits commonly arc toward the **opposite outlane**. [S4] ([Kineticist][4])
* **Demon eject:** Gene can spit the ball nearly SDTM; the single-ball return has a short compensating save, but **multiball Demon ejects are not saved by default**. [S3] ([Pinball Rule Sheets][3])
* **Right ramp:** difficult required shot for instruments/Love Gun; repeated misses expose the player to uncontrolled returns. [S4] ([Kineticist][4])
* **Starchild/STAR area:** inherently chaotic target/slingshot action; Prem/LE adds the drop-target/captive-ball mechanism.
* **Weak center-ramp attempt:** owner/play observations consistently flag partial shots as capable of returning quickly down the middle. [S7] ([Pinside][8])

## Spoken commentary cues

* “The song is more important than the points—finishing it turns on two-times for the rest of the ball.”
* “They’ve finished one song and gone straight to Backstage Pass; they want another mode before multiball.”
* “Both hurry-ups are collected, so the next shot they make becomes two-times for this ball.”
* “That Demon lock is doing two jobs: removing a ball from play and turning on another scoring multiplier.”
* “Love Gun is ready, but they’re delaying it to finish the song first.”
* “They keep shooting the right ramp because instruments are the real bottleneck to Heaven’s on Fire.”

## Trivia

* KISS was one of Stern’s earliest games on the **SPIKE** platform. [S1] ([Stern Pinball][1])
* Artist **Kevin O’Connor** also worked on Bally’s original 1979 *KISS*, giving the two games a deliberate visual connection. [S6] 
* **Paul Stanley and Gene Simmons recorded custom speech** for the machine. [S1] ([Stern Pinball][9])
* The four pop bumpers and central progress grid explicitly echo the classic Bally game. [S4] ([Kineticist][4])
* The LE was limited to **600 machines**; its added distinctions are presentation/collector features relative to Premium, not separate rules. [S2][S6] ([Pinside][10])

## Questions for the humans

### Edition and configuration checks

1. Which catalog entry is this machine?
   A. **Pro**
   B. **Premium/LE**
   C. Unknown — keep variant notes on the final sheet

2. Does the tournament use Stern **Install Competition / virtual Demon locks**?
   A. Yes
   B. No — use physical/default lock behavior
   C. Unknown

### Uncertainties and conflicts

1. **Shot-X persistence:** the v1.40-era maintained rulesheet and Stern-derived changelog describe 2× shot multipliers as lasting **for the rest of the ball** [S2][S3], while the 2026 Kineticist tutorial says “remainder of the game” [S4]. The code-era documentation is more authoritative, so this brief uses **rest of ball**. ([Pinball Rule Sheets][7])

2. **Heaven’s on Fire qualification count** is adjustment-sensitive, and archival sources disagree on which number should be called “default” after multiple late-code revisions. Avoid printing a fixed grid-count unless verified on the target setup. [S2][S3] ([Pinside][6])

## Human resolutions

1. Which catalog entry is this machine?
   A. **Pro**
   B. **Premium/LE**
   C. Unknown — keep variant notes on the final sheet
   **Human answer:** 2

2. Does the tournament use Stern **Install Competition / virtual Demon locks**?
   A. Yes
   B. No — use physical/default lock behavior
   C. Unknown
   **Human answer:** A. Yes

1. **Shot-X persistence:** the v1.40-era maintained rulesheet and Stern-derived changelog describe 2× shot multipliers as lasting **for the rest of the ball** [S2][S3], while the 2026 Kineticist tutorial says “remainder of the game” [S4]. The code-era documentation is more authoritative, so this brief uses **rest of ball**. ([Pinball Rule Sheets][7])
   **Human answer:** ok

2. **Heaven’s on Fire qualification count** is adjustment-sensitive, and archival sources disagree on which number should be called “default” after multiple late-code revisions. Avoid printing a fixed grid-count unless verified on the target setup. [S2][S3] ([Pinside][6])
   **Human answer:** ok

## Sources

* **[S1] — KISS official game page / launch announcement — Stern Pinball.** Identity, SPIKE platform, theme, music and primary mechanisms. [Stern KISS game page](https://www.sternpinball.com/game/kiss/?utm_source=chatgpt.com) ([Stern Pinball][1])
* **[S2] — KISS software history — Stern README mirrored by Pinside / Pinball Supernova.** **v1.41.0 / 2018-12-11**, v1.40 multiplier rewrite, Competition virtual locks, mystery and EB changes. [KISS Premium software archive](https://pinside.com/pinball/machine/kiss-stern-premium/details?utm_source=chatgpt.com) ([Pinside][2])
* **[S3] — KISS Wiki Rulesheet — Pinball Rule Sheets / Tilt Forums.** Detailed songs, shot-X, Demon/Love Gun, grid, wizard modes, saves and persistence. [KISS rulesheet](https://pinballrulesheets.com/stern/kiss-wiki-rulesheet?utm_source=chatgpt.com) ([Pinball Rule Sheets][3])
* **[S4] — Modern KISS Tutorial — James McFatter / Kineticist, updated 2026-04-29.** Current observed strategy, song sequencing, multiball decisions and physical-risk analysis. [Kineticist KISS tutorial](https://www.kineticist.com/news/modern-kiss-pinball-tutorial?utm_source=chatgpt.com) ([Kineticist][4])
* **[S5] — KISS Strategy Card — PinballCards, updated 2026-07-21.** Current tournament shorthand emphasizing Love Gun plus mode/playfield-X progression. [KISS strategy card](https://pinballcards.net/kiss-2015/?utm_source=chatgpt.com) ([JLP's Pinball Cards][5])
* **[S6] — KISS Feature Matrix — Stern Pinball.** Primary Pro/Premium/LE physical differences and LE collector features. [Official KISS feature matrix](https://sternpinball.com/wp-content/uploads/2018/11/KISS-feature-matrix.pdf?utm_source=chatgpt.com) 
* **[S7] — KISS owner/playability discussion — Pinside.** Used only for setup-sensitive center-ramp, Demon-return and outlane observations. [KISS owners discussion](https://pinside.com/pinball/forum/topic/kiss-armyno-regrets/page/4?utm_source=chatgpt.com) ([Pinside][8])

[1]: https://www.sternpinball.com/game/kiss/?utm_source=chatgpt.com "KISS – Stern Pinball"
[2]: https://pinside.com/pinball/machine/kiss-stern-premium/details?utm_source=chatgpt.com "KISS (Premium) Pinball Machine (Stern, 2015) | Pinside Game Archive"
[3]: https://pinballrulesheets.com/stern/kiss-wiki-rulesheet "KISS wiki rulesheet | Pinball Rule Sheets"
[4]: https://www.kineticist.com/news/modern-kiss-pinball-tutorial "Kiss (Stern) Pinball Machine Tutorial, Rules, Strategy & Gameplay Guide | Kineticist"
[5]: https://pinballcards.net/kiss-2015/?utm_source=chatgpt.com "KISS"
[6]: https://pinside.com/pinball/machine/kiss-stern/details?utm_source=chatgpt.com "KISS (Pro) Pinball Machine (Stern, 2015) | Pinside Game Archive"
[7]: https://pinballrulesheets.com/stern/kiss-wiki-rulesheet?utm_source=chatgpt.com "KISS wiki rulesheet | Pinball Rule Sheets"
[8]: https://pinside.com/pinball/forum/topic/kiss-armyno-regrets/page/4?utm_source=chatgpt.com "KISS(2015) Army...No Regrets! Owners, fans and groupies club | All clubs (...members only!) | Pinside.com"
[9]: https://www.sternpinball.com/2015/05/06/stern-pinball-joins-the-kiss-army-with-its-release-of-kiss-pinball/?utm_source=chatgpt.com "STERN PINBALL JOINS THE KISS ARMY WITH ITS RELEASE OF KISS PINBALL – Stern Pinball"
[10]: https://pinside.com/pinball/machine/kiss-stern-le/?utm_source=chatgpt.com "KISS (LE) Pinball Machine (Stern, 2015) | Pinside Game Archive"
