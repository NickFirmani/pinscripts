## Identity and versions

* **Ghostbusters (Pro)** — Stern Pinball, **2016**, Stern SPIKE/DMD generation. Design: **John Trudeau**; lead software credits include **Dwight Sullivan, Corey Stup, and Tanio Klyce**; artwork by **Jeremy Packer / Zombie Yeti**. [S1][S5] ([Stern Pinball][1])
* Editions: **Pro, Premium, Limited Edition**. Rules are broadly shared, but the physical games differ materially. On the **Pro**, Slimer only moves vertically; both ramps normally feed the right side; Storage Facility uses virtual locks; the right eject is a shallow saucer. Premium/LE add moving Ecto Goggles features, magnetic slings, physical locks, and different ramp feeds. [S1][S3] ([Stern Pinball][1])
* **Rules basis: `code` — v1.17.0, released 2019-10-08.** This remains the latest verified Stern release. Version 1.17 changed skill-shot scoring to **1M + 5% of score**, modified several awards, restricted 6× multiplier extension, capped Picto-Pops add-a-ball behavior, and fixed scoring/state issues. [S2][S5] ([Epicenter For All Things Pinball][2])
* Commentary-relevant multiballs: **Storage Facility Multiball**, **We Came, We Saw, We Kicked Its… (WCWS)**, **Mass Hysteria Multiball**, plus deep wizard multiball **We’re Ready To Believe You**. [S3]
* Research scope follows the supplied commentary brief.

## Thirty-second game plan

1. **Observed strategy:** use the opening skill shot to **Start Scene**, normally at the **Left Scoop or Left Ramp**, avoiding the dangerous Slimer qualification route. [S3][S4]
2. Stay on one scene sequence until it is complete; completing a sequence lights **WCWS multiball at the Left Ramp**, a reliable tournament payoff. [S3][S4]
3. Between opportunities, make **Gear Combos**: Left Ramp → Proton Pack standups/left captive ball. These light **2× then 3× playfield**; start both together for **6×**. [S3][S4]
4. Bring 3×/6× into a strong scene or multiball. **6× is the game's major scoring lever**, but in v1.17 it cannot be extended. [S2][S3]
5. **Viable alternate:** collect ghosts toward **Storage Facility Multiball** and stack it with an active scene; deeper ghost progression also reaches PKE Frenzy and Mass Hysteria. [S3]

## Core rules and persistence

* Scenes form three ordered ladders: **Left Scoop (2 modes), Left Ramp (3), Right Orbit (4)**. Completing an entire ladder lights WCWS; its ball count corresponds to that ladder's length, so the easiest two-mode route also produces the smallest WCWS. [S3][S4]
* If no scene is lit, shoot the dangerous center **GHOST** target to lower Slimer, then bash Slimer to relight scenes. During a scene, GHOST can normally spot the next required shot but **not the final shot**. [S3]
* On default current-code behavior, draining during most scenes gives progression credit but loses their remaining scoring; the final scene in a sequence instead resumes on the next ball. These behaviors are adjustment-sensitive. [S3]
* Collecting ghosts lights important milestones: Storage Facility locks at several thresholds, video mode at 40, Loopin’ Supers at 60, PKE Frenzy at 80, and Mass Hysteria at 100. [S3]
* **Storage Facility:** three virtual locks on the Pro start 3-ball multiball. Ghost shots are jackpots; clearing them lights three Super Jackpots. It can be started during scenes. [S3]
* **Playfield multipliers:** Gear Combo lights 2×, then 3×; shoot the corresponding standup to activate. Running both gives 6×. Individual 2×/3× timers can be extended; **6× cannot** on v1.17. [S2][S3]
* Super Jackpot starts at **5M each ball**, can reach **30M**, and resets between balls. It becomes tournament-changing primarily when multiplied or during Loopin’ Supers. [S3][S4]

## Skill shots

Ghostbusters has **two independent skill-shot components**, both selected before plunging. A successful component scores **1M + 5% of the player's current score**, plus its award. Missing one does not automatically cancel the other. [S2][S3]

* **Top-lane Skill Shot** — left flipper chooses P/K/E:

  * **P:** +3 Bonus X.
  * **K:** advances playfield-multiplier qualification; usually the strategically strongest lane choice.
  * **E:** +3M Super Jackpot.
* **Playfield Skill Shot** — right flipper selects the blue arrow:

  * Left Scoop: **Start Scene** / later Tobin’s Guide.
  * Left Orbit: +5M Super Jackpot.
  * Left Ramp: **Start Scene** / later Light Super Jackpot.
  * Right Orbit: **Start Scene** / later River of Slime.
  * Right Ramp: Start PKE Frenzy, or later Catch 10 Ghosts.
  * Right Eject: Catch 10 Ghosts. [S3]
* **Observed tournament choice:** soft-plunge for control and take **Left Scoop or Left Ramp Start Scene** on ball 1. It bypasses Slimer qualification and immediately begins the primary route. [S3][S4]

No separate Super/secret skill shot was verified.

## Secondary features

* **Ball save:** default start-of-ball save can rescue **two consecutive drains** within its timer; operator-adjustable from one to five saves. [S3]
* **Video Mode:** lit at 40 ghosts or through other awards and started at the Right Eject.

  * **Negative Reinforcement on ESP Ability:** escalating double-or-nothing guessing. In **tournament mode**, randomness is removed: the player gets one guaranteed correct guess per 10 collected ghosts, then the next is guaranteed wrong.
  * **Don’t Cross the Streams:** flippers steer two proton streams; catch 15 ghosts without crossing streams or letting one escape. [S3]
* **Extra balls:** commonly lit through scene/ghost progression. When configured to award points instead, current documentation gives **15M**, affected by playfield multiplier. [S3]
* **Tobin’s Spirit Guide / Picto-Pops:** award variable features including locks, multipliers, Super Jackpots and points. Do not assume deterministic competition behavior beyond the verified video-mode rule. [S3]
* No Action Button or player-activated save.

## What to watch

* **Blue skill-shot arrow:** shows exactly which opening award the player is attempting; Left Scoop/Left Ramp usually means immediate scene progression.
* **2× / 3× inserts beside the Left Ramp:** both lit/active means a potential **6× scoring window** is being prepared or spent.
* **Ghost-count ladder:** 40/60/80/100 telegraphs video mode, Loopin’ Supers, PKE Frenzy, and Mass Hysteria respectively.
* **Left Ramp flashing WCWS:** a whole mode sequence is complete; this is usually the player's tournament cash-out.

## Important shots

| Shot                        | Position    | Advances                                   | Why now?                                   | Risk                                            |
| --------------------------- | ----------- | ------------------------------------------ | ------------------------------------------ | ----------------------------------------------- |
| Left Scoop                  | Far left    | Scene ladder; Tobin’s                      | Easiest 2-mode path toward WCWS            | Tight shot; miss loses control                  |
| Left Orbit / Spinner        | Left        | Scenes; Super Jackpot value                | Safe-ish flow shot and scene progress      | Feeds pops/upper playfield                      |
| Left Ramp                   | Left-center | Scenes, Gear Combos, locks, WCWS, Super JP | Central scoring/setup shot                 | Half-ramp rejects can curl toward right outlane |
| GHOST / Slimer              | Center      | Relights scenes; spots mode shots          | Recovery after missing scene qualification | **Extremely drain-prone center return**         |
| Captive ball / Gear targets | Center-left | PF multipliers, mini-modes                 | Enables 2×/3×/6×                           | Standups produce violent rebounds/airballs      |
| Right Ramp                  | Right       | PKE Frenzy; scene shots                    | Large side feature / mode objective        | Steep and among the game's hardest shots        |

[S3][S4]

## Match strategy

**Playing ahead:**
**Strategic inference:** keep shooting the known scene/ramp route and take a qualified WCWS rather than making unnecessary center-target or multiplier standup shots. An ordinary controlled multiball is preferable to dying while assembling 6×.

**Playing behind:**
Build **3×/6×** first and expose it to WCWS, Storage Facility, a strong scene, Loopin’ Supers, or late PKE scoring. A multiplied feature can erase a large deficit quickly. [S3][S4]

**Key recurring decision:**
**Cash the currently qualified mode/multiball, or risk the Gear standups to bring playfield-X into it?** The multiplier is enormously powerful, but the shots used to activate it are among Ghostbusters’ most dangerous.

## Danger zones

* **GHOST target:** misses can bleed speed off the center guide and dribble **straight down the middle**. [S3]
* **Left-ramp reject:** partial shots can curl across and disappear down the **right outlane**. [S3]
* **Multiplier / captive-ball standups:** close to the flippers and notorious for violent airballs and center returns. [S3]
* **Pop exit through Slimer lane:** aggressive pops can send the ball backward into the center lane for an immediate drain. [S3]
* **Bottom geometry:** wide flipper gap, double inlanes and steep factory flipper angles make seemingly ordinary feeds unexpectedly difficult to control. [S3]

## Spoken commentary cues

* “They’re taking **Start Scene** off the skill shot—that saves them from having to fight Slimer.”
* “That finishes the ladder; **We Came, We Saw** is now lit at the Left Ramp.”
* “The Gear Combo has qualified three-X; if they bring two-X in as well, that becomes **six-X playfield**.”
* “Six-X is running, and on 1.17 they **cannot extend it**—this is the scoring window.”
* “That GHOST target can spot the next mode shot, but it can’t give them the last one.”
* “Forty ghosts means video mode; if competition mode is on, Negative Reinforcement is **deterministic**, not a real guess.”

## Trivia

* Ghostbusters was designed by **John Trudeau**, with final software led in part by Dwight Sullivan; it was one of Stern’s early **SPIKE** titles. [S1][S5]
* Original cast member **Ernie Hudson** recorded new speech guiding the player as a Ghostbusters recruit. [S1] ([Stern Pinball][1])
* All three editions use hand-drawn artwork by **Zombie Yeti**. [S1]
* The Premium/LE **Ecto Goggles** use a Pepper’s Ghost-style optical illusion; the Pro omits that mechanism. [S1][S3]
* Version **1.16/1.17** substantially rewrote the late rules years after the game's 2016 release, so early strategy guides can describe materially obsolete tournament exploits. [S2][S3]

## Questions for the humans

### Edition and configuration checks

1. **Should the final sheet assume Stern Competition/Tournament mode?** This materially affects Negative Reinforcement scoring. [S3]
   A. Yes — competition mode
   B. No — standard/random behavior
   C. Describe both briefly

2. **Should the sheet assume current v1.17 scene-drain defaults?** Scene completion/persistence is operator-adjustable and can meaningfully change the optimal mode route. [S3]
   A. Yes — v1.17 defaults
   B. Note that venue configuration must be checked
   C. Omit persistence detail from the one-pager

### Uncertainties and conflicts

* **Tobin’s Spirit Guide / Picto-Pops competition normalization:** current sources document their random award pools but do not adequately establish a deterministic competition-mode sequence. Treat them as variable unless verified on the target configuration.
* No material conflict found on the **latest software version**: current game archives and contemporaneous release material both identify **v1.17.0, 2019-10-08**. [S2][S5]

## Human resolutions

1. **Should the final sheet assume Stern Competition/Tournament mode?** This materially affects Negative Reinforcement scoring. [S3]
   A. Yes — competition mode
   B. No — standard/random behavior
   C. Describe both briefly
   **Human answer:** A. Yes — competition mode

2. **Should the sheet assume current v1.17 scene-drain defaults?** Scene completion/persistence is operator-adjustable and can meaningfully change the optimal mode route. [S3]
   A. Yes — v1.17 defaults
   B. Note that venue configuration must be checked
   C. Omit persistence detail from the one-pager
   **Human answer:** A. Yes — v1.17 defaults

## Sources

* **[S1] — Ghostbusters** — Stern Pinball; official manufacturer page. Identity, editions, Slimer/Ecto Goggles hardware, artwork, Ernie Hudson speech. [Stern Ghostbusters page](https://wp.sternpinball.com/game/ghostbusters/?utm_source=chatgpt.com)
* **[S2] — Ghostbusters v1.17 Code Update / Stern release notes** — Stern release notes reproduced contemporaneously by Pinball Supernova; code/version source. Release date, skill-shot change, 6× behavior, fixes and award changes. [Ghostbusters v1.17 release notes](https://pinballsupernova.wordpress.com/2019/10/08/code-update-sterns-ghostbusters-version-v-1-17/?utm_source=chatgpt.com)
* **[S3] — Ghostbusters Pinball Rulesheet, code 1.17** — ThreeWayCombo; detailed community rules/competition reference. Current rules, strategy, physical feeds, skill shots, multipliers, modes, tournament video mode, persistence/settings. [Ghostbusters 1.17 rulesheet PDF](https://o.pinside.com/4/97/42/49742fa0b8406ae58c8deb26ac677824fbae1e25.pdf?utm_source=chatgpt.com)
* **[S4] — Ghostbusters Pinball Tutorial, Rules & Gameplay Strategy Guide** — Kineticist; modern expert strategy guide. Tournament opener, mode-ladder strategy, 6× importance, Gear Combos and Storage Facility stacking. [Kineticist Ghostbusters tutorial](https://www.kineticist.com/news/ghostbusters-pinball-tutorial?utm_source=chatgpt.com)
* **[S5] — Ghostbusters (Pro) Game Archive** — Pinside; secondary identity/version record. Credits, SPIKE hardware, Pro identity, latest software **v1.17 / 2019-10-08**. [Pinside Ghostbusters Pro archive](https://pinside.com/pinball/machine/ghostbusters?utm_source=chatgpt.com)

[1]: https://wp.sternpinball.com/game/ghostbusters/ "Ghostbusters – Stern Pinball"
[2]: https://pinballsupernova.wordpress.com/2019/10/08/code-update-sterns-ghostbusters-version-v-1-17/ "CODE UPDATE : STERN’S GHOSTBUSTERS: VERSION V 1.17 | Epicenter For All Things Pinball"
