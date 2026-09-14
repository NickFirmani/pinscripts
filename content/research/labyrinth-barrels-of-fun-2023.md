## Identity and versions

* **Jim Henson’s Labyrinth** — Barrels of Fun, **2023**, the company’s debut machine. Lead design: **David Van Es**; rules: **Phil Grimaldi and Bowen Kerins**; software: **Eric Priepke**; engineering: **Travis Moseman**; primary playfield art: **Jonathan Bergeron**. FAST Pinball control system, dual LCDs, multiple magnets/diverters and mechanical toys. [S2][S4] ([Pinball Rule Sheets][1])
* One production model, announced with a maximum run of **1,100 machines**. [S4] ([Kineticist][2])
* **Rules basis: `code` — v2026.01.30, released 2026-01-30.** Current official download. This release mainly reworked audio, added shaker support and fixes; importantly, Tournament Mystery now alternates deterministically between points and bonus-X. [S1] ([Kollect Fun][3])
* Important multiballs: **Brick Keeper, Friend, Tea Time, Wise Man**, plus the late **Goblin City Multiball** wizard mode. [S3] ([Pinball Rule Sheets][1])

Research scope follows the supplied commentator-reference specification.

## Thirty-second game plan

1. **Strategic inference / practical tournament line:** develop **Ludo** while qualifying a normal mode. Ludo Level 1 gives **+50% mode scoring**; Level 2 gives **2× Brick Keeper jackpots**. [S3] ([Pinball Rule Sheets][1])
2. Start the mode **before** Brick Keeper Multiball, then bring Brick Keeper underneath it. Mode-selection/start logic is disabled during multiball, while current code explicitly supports modes running during Brick Keeper. [S1][S3] ([Kollect Fun][4])
3. In Brick Keeper MB, collect red jackpots, then attack the **left-orbit captive-ball/spinner Super Jackpot**. More jackpots increase the Super, and successive Supers require more setup. [S3] ([Pinball Rule Sheets][1])
4. **Orbs are the long-game leverage:** collect one for 10M, then assign a **permanent shot multiplier** to the next rainbow shot; stack up to **3× on one shot**. [S3] ([Pinball Rule Sheets][1])
5. **Alternate:** develop all three Friends and deliberately **decline Friend Multiball** until their jackpots are worth more, then take the larger MB later. [S3] ([Pinball Rule Sheets][5])

## Core rules and persistence

Spell **LABYRINTH** via white-arrow shots to light one of the two U-turn Mode Starts; qualification gets harder as modes are played. Default current code begins the first mode only one qualifying shot away. Six main modes lead eventually to Goblin City. [S1][S3] ([Kollect Fun][4])

**Brick Keeper Multiball:** complete green targets to light the first lock at the left orbit, second at the center ramp, then start MB at the right orbit. By default, an unplayed Brick Keeper MB receives substantial ball-3 assistance. Lock progress is player-specific. [S3] ([Pinball Rule Sheets][1])

**Friends persist and improve over the game.** Hoggle speeds LABYRINTH/locks; Ludo boosts mode and MB scoring; Sir Didymus adds survival and eventually a once-per-MB add-a-ball. Friend Multiball can be declined and offered again later. [S2][S3] ([Kollect Fun][6])

**Orbs persist** and are earned from strong mode performances, developed Friends, multiballs and quests. After collection, the next rainbow shot receives +1 shot-X, up to 3×. If the player drains before assigning it, the multiplier is lost but the Orb still counts toward the 13 needed for **Battle Jareth**. [S3] ([Pinball Rule Sheets][1])

Easy commentary trap: **Goblin City is reached by playing all six modes, but Battle Jareth requires all 13 Orbs**—much deeper qualification. [S3] ([Pinball Rule Sheets][1])

## Skill shots

Skill-shot value scales with **ball number**, not how many times that particular skill shot has been made. [S3] ([Pinball Rule Sheets][1])

| Skill shot  | How / award                                                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Worm**    | Very short plunge into Ello Worm staging area. 200K / 400K / 600K on balls 1–3.                                                   |
| **Wiseman** | Plunge down the full shooter wireform into the scoop under the right ramp. Also first half of a **Super Skill Shot** with Bridge. |
| **Target**  | Medium plunge to upper flipper → Change Mode target. 500K / 1M / 1.5M.                                                            |
| **Ramp**    | Medium plunge → upper-flipper center ramp. 350K / 700K / 1.05M.                                                                   |
| **Bridge**  | Medium plunge → upper flipper → bridge loop. 300K / 750K / 900K.                                                                  |
| **Egdirb**  | Stronger plunge that falls backward through the upper loop (“bridge” backwards). 250K / 500K / 750K.                              |
| **Village** | Plunge beyond upper loop but short of a full orbit into Goblin Village. Starts at 400K; later scaling not reliably documented.    |

[S3] ([Pinball Rule Sheets][1])

## Secondary features

* **Sir Didymus Defense:** Level-1 Didymus enables the post above the left outlane after spelling HELP. Later Didymus levels add a per-multiball add-a-ball and +5 seconds to major ball saves. [S2][S3] ([Kollect Fun][6])
* **U-turn / eject ball saves:** several short safety saves are operator-adjustable, including a U-turn save; these materially affect how punishing the game plays. [S1] ([Kollect Fun][4])
* **Mystery:** normally has a broader award pool including Tea Time MB and friend/quest help. On current code with **Tournament enabled, Mystery alternates between points and bonus multiplier**, removing that randomness. [S1][S3] ([Kollect Fun][4])
* **Extra balls:** lit from 10 Friend items, two Wise Man quests, or normally the third Mystery award. Above the allowed EB limit the collect converts to points, but I could not verify a universal tournament conversion value. [S1][S3] ([Pinside][7])
* **No conventional video mode found.**

## What to watch

1. **White LABYRINTH arrows / flashing U-turn entrances:** a main mode is ready; if Brick Keeper is also close, expect the player to start the mode first. [S3]
2. **Friend portraits and colored shots:** Ludo development is especially important—50% mode scoring and later 2× Brick Keeper jackpots. [S3]
3. **Rainbow shots immediately after an Orb collect:** the player is deciding where to place a permanent shot multiplier. [S3]
4. **Red arrows during Brick Keeper MB:** jackpots are building/qualifying the Super; the left orbit becomes the major cash-out. [S3] ([Pinball Rule Sheets][1])

## Important shots

| Shot                          | Position                    | Advances                       | Why now?                                         | Risk                                                                    |
| ----------------------------- | --------------------------- | ------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------- |
| **Left orbit / Brick Keeper** | Far left                    | Lock 1; BK Super Jackpot       | Core MB setup/cash-out                           | Fork/captive-ball traffic can return quickly.                           |
| **Center ramp**               | Center                      | LABYRINTH; Lock 2              | Mode + Brick Keeper progression                  | Upper-flipper shot is demanding; rejects documented. [S5]               |
| **U-turn / horseshoe**        | Upper center-right          | Starts modes                   | Converts qualification into scoring              | Some machines return this **SDTM**; short ball save is adjustable. [S5] |
| **Wiseman scoop**             | Upper-right center          | Mode start; quests             | Quest progression, bonus X, eventual Wise Man MB | Tight target/scoop sequence breaks control.                             |
| **Helping Hands scoop**       | Left-center                 | Friend jackpots; Friend MB; EB | Level Friends / cash Friend value                | Eject can be violent if poorly adjusted. [S5]                           |
| **Orb collect**               | Beneath upper-right flipper | Collect Orb → assign shot X    | Permanent scoring leverage                       | Must survive long enough to place the multiplier.                       |

## Match strategy

**Playing ahead:** take prepared Brick Keeper rather than overdeveloping Friends, place Orbs on shots you already make comfortably, and use Sir Didymus protection. **Strategic inference:** a secure 2× shot that you repeatedly hit is preferable to forcing a theoretically optimal but dangerous 3× placement.

**Playing behind:** develop **Ludo**, delay Friend MB for higher jackpot levels, and concentrate Orb multipliers onto a high-value shot. A mode + Ludo + Brick Keeper package offers substantially more ceiling than isolated MB scoring.

**Key recurring decision:** **cash the multiball now, or keep investing in Friends/modes/shot-X first?** Friend MB explicitly lets the player decline; Brick Keeper likewise becomes much more valuable after Ludo Level 2. [S3] ([Pinball Rule Sheets][5])

## Danger zones

* **Right side of U-turn / horseshoe:** repeated owner reports of straight-down-the-middle returns; highly setup-sensitive. [S5] ([Pinside][8])
* **Helping Hands / under-ramp ejects:** can fire near center if coil strength/pitch is poor; adjustable. [S5] ([Pinside][9])
* **Center-ramp rejects:** upper-flipper angle and machine pitch make this important shot deceptively difficult. [S5] ([Pinside][10])
* **Wide outlanes / lateral sling action:** side-to-side rebounds are repeatedly cited as dangerous. [S5] ([Pinside][11])
* **Unassigned Orb:** draining before the rainbow assignment wastes the permanent shot-X opportunity. [S3] ([Pinball Rule Sheets][1])

## Spoken commentary cues

* “They want the mode started **before** Brick Keeper; once multiball is running, that mode-start window is gone.”
* “Ludo Level Two is the big Brick Keeper breakpoint—those jackpots are now doubled.”
* “That Orb isn’t just wizard progress; the next rainbow shot gets a permanent multiplier.”
* “They’re passing on Friend Multiball deliberately—the Friends can be leveled further for bigger jackpots.”
* “Red arrows are Brick Keeper jackpots; now watch the left orbit for the spinner Super.”
* “That horseshoe return can be vicious—some setups actually need a programmed short save there.”

## Trivia

* Labyrinth was **Barrels of Fun’s first commercial pinball machine**. [S4] ([Kineticist][2])
* The game uses **all five David Bowie songs from the film**. [S4] ([Kineticist][2])
* Rules co-designer **Bowen Kerins** is a five-time PAPA/IFPA world champion and filmed the manufacturer’s official gameplay tutorial. [S4][S6] ([YouTube][12])
* The game was announced with a maximum production run of **1,100**, with one feature level rather than Pro/Premium/LE tiers. [S4] ([Kineticist][2])
* Current 2026 code completely refreshed the audio package with **Jeff Dodson** and added shaker-motor support. [S1] ([Kollect Fun][4])

## Questions for the humans

### Edition and configuration checks

1. Which rules environment should the finished page assume?
   A. **Current v2026.01.30, Tournament enabled**
   B. Current code, normal settings
   C. Configuration-neutral

2. The **U-turn, Helping Hands and ramp-eject short ball saves are adjustment-sensitive** and materially alter risk.
   A. Keep only a generic “machine-sensitive” warning
   B. Assume factory/default behavior
   C. Leave all feed details to venue notes

### Uncertainties and conflicts

1. Current code makes Tournament Mystery deterministic, alternating **points / bonus-X** [S1], while older rulesheets describe the normal random award pool [S3]. This brief treats the current-code tournament behavior as authoritative.

2. The maintained detailed rulesheet is based primarily on **2024-09-25 code** [S3]. Later official updates through 2026 change several settings/fixes but do not document a wholesale scoring-rule rewrite; this brief uses the official changelog wherever the two differ. ([Pinball Rule Sheets][1])

3. I found no authoritative current value for tournament/disabled **extra-ball point conversion**.

## Human resolutions

1. Which rules environment should the finished page assume?
   A. **Current v2026.01.30, Tournament enabled**
   B. Current code, normal settings
   C. Configuration-neutral
   **Human answer:** A. **Current v2026.01.30, Tournament enabled**

2. The **U-turn, Helping Hands and ramp-eject short ball saves are adjustment-sensitive** and materially alter risk.
   A. Keep only a generic “machine-sensitive” warning
   B. Assume factory/default behavior
   C. Leave all feed details to venue notes
   **Human answer:** A. Keep only a generic “machine-sensitive” warning

1. Current code makes Tournament Mystery deterministic, alternating **points / bonus-X** [S1], while older rulesheets describe the normal random award pool [S3]. This brief treats the current-code tournament behavior as authoritative.
   **Human answer:** ok

2. The maintained detailed rulesheet is based primarily on **2024-09-25 code** [S3]. Later official updates through 2026 change several settings/fixes but do not document a wholesale scoring-rule rewrite; this brief uses the official changelog wherever the two differ. ([Pinball Rule Sheets][1])
   **Human answer:** ok

3. I found no authoritative current value for tournament/disabled **extra-ball point conversion**.
   **Human answer:** ok

## Sources

* **[S1] Labyrinth Code Update / Update History — Barrels of Fun.** Primary manufacturer source; current `2026.01.30`, tournament Mystery, later fixes/settings. [Current update](https://shop.kollectfun.com/labyrinth-code-update/?utm_source=chatgpt.com) [Full update history](https://shop.kollectfun.com/labyrinth-update-history/?utm_source=chatgpt.com)
* **[S2] Jim Henson’s Labyrinth Manual R1.3 — Barrels of Fun.** Primary manufacturer manual, information current through 2025-08-27; Friends/perks and hardware. [Official manual PDF](https://shop.kollectfun.com/wp-content/uploads/2025/10/bof-labyrinth-manual-r1_3-sep-2025-web.pdf?utm_source=chatgpt.com)
* **[S3] Labyrinth Rulesheet — Pinball Rule Sheets / Tilt community.** Detailed rules: modes, skill shots, Friends, multiballs, Orbs, quests, wizard progression. [Rulesheet](https://pinballrulesheets.com/barrels-of-fun/labyrinth-rulesheet?utm_source=chatgpt.com)
* **[S4] Labyrinth launch / design overview — Kineticist and Barrels of Fun.** Identity, production plan, mechanisms, soundtrack and design team. [Kineticist launch overview](https://www.kineticist.com/news/labyrinth-barrels-of-fun?utm_source=chatgpt.com)
* **[S5] Labyrinth Owners / Playability discussions — Pinside.** Used only for setup-sensitive ejects, U-turn returns, ramp rejects and outlane behavior. [Playability discussion](https://pinside.com/pinball/forum/topic/labyrinth-playability-issues?utm_source=chatgpt.com)
* **[S6] Jim Henson’s Labyrinth Gameplay Overview — Barrels of Fun / Bowen Kerins.** Official manufacturer tutorial; general strategy and rules context, filmed on pre-release code. [Official tutorial video](https://www.youtube.com/watch?v=Ps0_mAqIlnk&utm_source=chatgpt.com)

[1]: https://pinballrulesheets.com/barrels-of-fun/labyrinth-rulesheet "Labyrinth Rulesheet | Pinball Rule Sheets"
[2]: https://www.kineticist.com/news/labyrinth-barrels-of-fun?utm_source=chatgpt.com "Labyrinth ft David Bowie is the First Pinball Machine from Barrels of Fun | Kineticist"
[3]: https://shop.kollectfun.com/labyrinth-code-update/?utm_source=chatgpt.com "Labyrinth Code Updates – Barrels of Fun"
[4]: https://shop.kollectfun.com/labyrinth-update-history/ "Labyrinth Update History – Barrels of Fun"
[5]: https://pinballrulesheets.com/barrels-of-fun/labyrinth-rulesheet?utm_source=chatgpt.com "Labyrinth Rulesheet | Pinball Rule Sheets"
[6]: https://shop.kollectfun.com/wp-content/uploads/2025/10/bof-labyrinth-manual-r1_3-sep-2025-web.pdf?utm_source=chatgpt.com "October 2025"
[7]: https://pinside.com/pinball/forum/topic/barrels-of-fun-jim-henson-s-labyrinth-faq?utm_source=chatgpt.com "Barrels of Fun - Jim Henson's Labyrinth FAQ | Barrels of Fun | Pinside.com"
[8]: https://pinside.com/pinball/forum/topic/labyrinth-playability-issues?utm_source=chatgpt.com "Labyrinth playability issues | Tech: LCD era games | Pinside.com"
[9]: https://pinside.com/pinball/forum/topic/labyrinth-owners-club-give-me-the-child/page/7?utm_source=chatgpt.com "Labyrinth owners club - Give me the Child! | All clubs (...members only!) | Pinside.com"
[10]: https://pinside.com/pinball/forum/topic/labyrinth-owners-club-give-me-the-child/page/112?utm_source=chatgpt.com "Labyrinth owners club - Give me the Child! | All clubs (...members only!) | Pinside.com"
[11]: https://pinside.com/pinball/forum/topic/labyrinth-owners-club-give-me-the-child/page/13?utm_source=chatgpt.com "Labyrinth owners club - Give me the Child! | All clubs (...members only!) | Pinside.com"
[12]: https://www.youtube.com/watch?v=Ps0_mAqIlnk&utm_source=chatgpt.com "Jim Henson's Labyrinth Pinball Gameplay Overview With Bowen Kerins - YouTube"
