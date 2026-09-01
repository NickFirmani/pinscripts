## Identity and versions

**TRANSFORMERS: More Than Meets the Eye — Pro**, Stern Pinball, released **May 20, 2026**, on the **SPIKE 3** platform. Lead design **Elliot Eismin**; software/rules **Elizabeth Gieske and Mike Kyzivat**; mechanics **Robert Blakeman**; animation **Tom Kyzivat**; sound **Jerry Thompson**; producer **John Blakely**. [S1][S2]

This is the **Generation 1 cartoon / 1986-film** Transformers game, not Stern's 2011 Michael Bay-themed *Transformers*. Pro/Premium/LE share the core scoring architecture. The **Pro has static Megatron** and simpler lock/feed hardware; Premium/LE add the animatronic firing Megatron cannon, Soundwave physical cassette locks and additional sculpt/mechanical effects. [S1][S3]

Latest verified Pro code: **v0.89.0, August 12, 2026**. This remains pre-1.0 software; v0.89 substantially reworked Tech Spec Mania and Combiner scoring, so older launch strategy should be treated cautiously. [S2][S4]

Major multiballs: **Transformers Multiball, Combiner Multiball, Tech Spec Mania**, plus Dinobot Island's two-ball multiball. [S3]

## Thirty-second game plan

1. **Start a Mission while preparing Transformers Multiball.** Current code requires Optimus to light locks, then the center VUK to lock three balls. Missions can run during multiball if started first. [S3][S4]
2. Build **Bumblebee 2X scoring** at the captive ball before starting MB. During MB, the special add-a-ball sequence can upgrade this to **3X for 30 seconds**. [S3]
3. During Transformers MB, qualify **several jackpots before collecting one**: the jackpot multiplier equals the number currently lit. Three jackpots light the side-ramp Super. [S3]
4. Collect **Tech Specs** and mission Final Blows. Final Blows create persistent **2X Shot-X** opportunities when a Tech Spec is subsequently collected at that shot. [S3]
5. Alternate route: after only **two Missions**, the right ramp lights **One Shall Fall**. You can start it immediately or deliberately play more Missions first to make the battle easier/more valuable. [S3]

## Core rules and persistence

Five 60-second **Missions** start behind Megatron's three-bank. The first two require one Megatron-scoop qualification; later Missions require two. Mission progress is **saved if the mode times out or the player drains**, making partially completed Missions persistent rather than lost. [S3]

The spinner fills **Energon Cubes**. At the next Mission, a player may spend one to **Energize** it—easier but lower-value. Complete a Mission without using Energon and the next can become **Rusted**—harder, but higher scoring. This is a central difficulty-versus-value decision. [S3]

A Mission counts as complete after its required shots; the optional **Final Blow** at Megatron is an additional payoff. Final Blow awards a random **2X Shot-X**; that multiplier becomes active when a Tech Spec is lit/collected at the corresponding shot. [S3]

**Transformers Multiball:** hit Optimus to light Lock, then the VUK to lock. Three locks start MB. Each major shot progresses purple Decepticon → red Autobot → flashing jackpot. A jackpot's multiplier equals the number of jackpots currently qualified, so spreading shots before collecting can dramatically increase scoring. Three jackpots light the side-ramp Super Jackpot. [S3]

**Playfield X:** repeated lit captive-ball hits spell BUMBLEBEE and start **30 seconds of 2X scoring**. If 2X is active before a compatible MB, use the once-per-game add-a-ball at the Space Bridge and hit the held ball to raise this to **3X**. [S3]

## Skill shots

* **Optimus Skill Shot:** short plunge to the upper flipper → Optimus target. **500K +5 sec ball save.**
* **Side Ramp Skill Shot:** same feed → side ramp. **5M +8 sec ball save.**
* **Space Bridge Super Skill Shot:** same feed → difficult Space Bridge. **8M +10 sec ball save.**
* **Secret Skill Shot:** short-plunge/catch lower-right, shoot the Grimlock left orbit to return to the upper flipper, then complete an upper-flipper skill shot. The best documented version—Space Bridge—is **15M**. [S3]
* **Alternate full-plunge shot:** the current competitive card also documents a full plunge to the right flipper followed by a red shot; its exact current v0.89 award is not documented in the main rulesheet. [S5]

The upper-flipper skill shots are unusually important because success also **extends the opening ball save**.

## Secondary features

**Multiball Add-A-Ball:** once per game after the normal MB ball save expires, the **Space Bridge** lights. It adds a ball and holds it for 10 seconds; hitting the captive ball before release starts **30 seconds 2X**, or **3X** if Bumblebee 2X was already running. Mystery can relight this feature after use. [S3]

**Left outlane save:** lit at the beginning of the game; after use it can be relit through Mystery. [S3]

**Countdown to Extinction:** on the **last ball**, a right-outlane drain starts an **18-second** rescue: make the right ramp to continue the ball. v0.87 specifically increased this from 15 to 18 seconds and pauses other mode timers during the rescue. [S2][S3]

**Action button / Tech Specs:** cassette combos light the action button; pressing it lights all Tech Specs temporarily, creating concentrated Shot-X opportunities. In Combiner MB the same button cycles/selects Combiners. [S3]

**Extra Balls:** lit at the Space Bridge by playing all five Missions or collecting 15 Tech Specs. Tournament handling is not sufficiently documented in the current public rules reference; confirm locally. [S3]

## What to watch

* **Mission marked Energized or Rusted:** tells you whether the player chose easier/lower scoring or harder/higher scoring.
* **BUMBLEBEE / captive-ball 2X flashing:** player is likely preparing a multiball before starting the 30-second multiplier.
* **Multiple red/white jackpot arrows during Transformers MB:** delaying the first collect can increase its jackpot multiplier.
* **Right ramp flashing One Shall Fall:** two Missions have been played; refusal to shoot it usually means the player is deliberately improving the mini-wizard first. [S3]

## Important shots

| Shot                  | Position                | Advances                             | Why now?                                     | Risk                                                  |
| --------------------- | ----------------------- | ------------------------------------ | -------------------------------------------- | ----------------------------------------------------- |
| Megatron bank/scoop   | Center-right            | Missions, Final Blows                | Primary mode progression                     | Drop/scoop attacks can rebound directly toward center |
| Optimus               | Left-center             | Lights MB locks; builds jackpot      | Required before each current-code lock       | Direct bash/standup rebound                           |
| Lock VUK              | Center-left             | Transformers MB locks                | Main protected scoring setup                 | Tight shot, though successful VUK is a useful bailout |
| Center spinner        | Center                  | Energon; Golden Lagoon; MB scoring   | Builds easier Missions or huge spinner mode  | Misses enter busy lower-field geometry                |
| Grimlock / left orbit | Far left                | Dinobot Missions; upper-flipper feed | Starts alternate stack and feeds skill shots | Gated by targets; nearby hidden sling adds danger     |
| Side ramp             | Upper-flipper left side | Combiner parts; MB Super JPs         | Major cash-out / Combiner route              | Difficult; short shots fall into bumper/slings        |

[S3][S6]

## Match strategy

**Playing ahead:** take **Energized Missions**, build a modest 2X stack, and start Transformers MB instead of forcing a Rusted mode or one more multiplier step. Use the VUK as a relatively controlled progression shot and take available Mystery/outlane insurance. **Strategic inference.**

**Playing behind:** lean into multiplicative scoring—complete a normal Mission to Rust the next, activate Bumblebee **2X**, start the Rusted Mission into Transformers MB, then convert the add-a-ball sequence to **3X** while several MB jackpots are simultaneously qualified. v0.89's heavily increased **Tech Spec Mania** scoring is another legitimate comeback route. [S2][S3]

**Key recurring decision:** **start the prepared scoring feature now, or improve it first?** The game repeatedly rewards delay—Rusted Missions, more lit MB jackpots, One Shall Fall perks, Combiner completion—but its difficult shots and nasty lower bumper/slings make every extra setup flip expensive.

## Danger zones

* **Side-ramp miss:** current competitive guidance specifically warns that misses bounce between the bumper and slings and can end the ball almost immediately. [S6]
* **Lower-left hidden sling / bumper zone:** the Grimlock area can unexpectedly accelerate balls toward the lower slings/outlanes. [S6]
* **Megatron/drop-bank rebound:** mandatory mode progression through direct targets can produce fast center returns.
* **Right ramp:** described as the game's steepest shot; rejects return quickly into lower play.
* **Upper-flipper miss:** losing the controlled left-orbit/plunge feed often drops the ball directly into the game's chaotic lower half. [S6]

## Spoken commentary cues

* “He's starting the Mission before multiball—that's the stack order.”
* “He passed on the Energon Cube, so the next Mission can be Rusted: harder, but worth more.”
* “There are several jackpots flashing; the next collect is multiplied by how many he's qualified.”
* “Bumblebee double scoring is ready—if he carries that into multiball, the add-a-ball sequence can turn it into triple.”
* “One Shall Fall is already available after two Missions, but he's deliberately making the battle stronger before taking it.”
* “That side ramp is valuable, but a short shot drops directly into the bumper-and-sling blender.”

## Trivia

* This is the first Stern Transformers title based specifically on the **original Generation 1 animated continuity**; Stern's 2011 game used the live-action films. [S1][S6]
* The release coincides with the **40th anniversary of *The Transformers: The Movie*** and includes “The Touch” by Stan Bush. [S1]
* **Peter Cullen** and **Frank Welker** recorded new Optimus Prime / Megatron-Soundwave callouts. [S1]
* Stern introduced the game on **SPIKE 3** hardware. [S2]
* The Pro deliberately keeps **Megatron static**, while Premium/LE use an animated robot with a physical ball-firing fusion cannon. [S1]

## Questions for the humans

### Tournament and venue checks

1. Which software is installed?
   A. **v0.89.0 — Aug. 12, 2026**
   B. v0.88.0
   C. v0.87.0 or earlier
   D. Unsure

2. Is the tournament using:
   A. Full Stern Competition Install
   B. Competition Mode only
   C. Custom tournament settings
   D. Default/location settings
   E. Unsure

3. How are Extra Balls handled?
   A. Disabled
   B. Played normally
   C. Plunge without flipping
   D. Local point conversion
   E. Unsure

4. Is the **once-per-game multiball Add-A-Ball** left at stock behavior?
   A. Yes
   B. Disabled/adjusted
   C. Unsure

5. Which physical feed is most problematic on this Pro?
   A. Side-ramp miss → bumper/slings
   B. Right-ramp reject
   C. Megatron/drop rebound
   D. Upper-flipper miss
   E. Other: ___

### Uncertainties and conflicts

* **Early-code strategy:** v0.87 changed the main MB qualification to require **Optimus → Lock VUK**, while some June strategy material still describes simply looping the VUK six times. Current v0.89 rules above use the newer qualification. [S2][S3][S6]
* **Tech Spec Mania:** v0.89 says scoring was raised roughly **4X–10X** and the Super formula was reworked. Any pre-August 12 scoring examples are stale. [S2]
* **Rules are unfinished:** current software is still **0.89**, and the public rulesheet still contains unknown values in parts of One Shall Fall. Do not imply that the game's long-term tournament meta is settled. [S2][S3]
* **Competition configuration:** I found current rules and adjustments, but not an authoritative published Competition-Install profile for this new title. Confirm Extra Balls, ball-save and other event settings on the actual game.
* **Pro/Premium physical feeds differ:** Premium/LE's firing cannon and physical Soundwave lock alter ball movement; do not use Premium feed observations as evidence for this Pro. [S1][S6]

## Human resolutions

1. Which software is installed?
   A. **v0.89.0 — Aug. 12, 2026**
   B. v0.88.0
   C. v0.87.0 or earlier
   D. Unsure
   **Human answer:** A. **v0.89.0 — Aug. 12, 2026**

2. Is the tournament using:
   A. Full Stern Competition Install
   B. Competition Mode only
   C. Custom tournament settings
   D. Default/location settings
   E. Unsure
   **Human answer:** a or b

3. How are Extra Balls handled?
   A. Disabled
   B. Played normally
   C. Plunge without flipping
   D. Local point conversion
   E. Unsure
   **Human answer:** A. Disabled

4. Is the **once-per-game multiball Add-A-Ball** left at stock behavior?
   A. Yes
   B. Disabled/adjusted
   C. Unsure
   **Human answer:** A. Yes

5. Which physical feed is most problematic on this Pro?
   A. Side-ramp miss → bumper/slings
   B. Right-ramp reject
   C. Megatron/drop rebound
   D. Upper-flipper miss
   E. Other: ___
   **Human answer:** na

## Sources

**[S1] — Stern Pinball, *Roll Out for Battle with TRANSFORMERS: More Than Meets the Eye* + official Pro/Premium model pages.** Primary manufacturer sources; release date, G1/film theme, models, voices and Pro/Premium physical differences.
[Stern launch announcement](https://www.sternpinball.com/2026/05/20/roll-out-for-battle-with-transformers-more-than-meets-the-eye-by-stern-pinball/?utm_source=chatgpt.com)
[Official Pro model page](https://www.sternpinball.com/game/transformers-more-than-meets-the-eye/pro/?utm_source=chatgpt.com)
[Official Premium model page](https://www.sternpinball.com/game/transformers-more-than-meets-the-eye/premium/?utm_source=chatgpt.com)

**[S2] — *Transformers: More Than Meets the Eye Pro software changelog* — Stern release notes archived by Pinside.** Version-sensitive source; **v0.89.0 Aug. 12, 2026**, v0.87 lock-rule change, Tech Spec Mania rebalance, One Shall Fall updates and current adjustments.
[Current Pro software/changelog archive](https://pinside.com/pinball/machine/transformers-more-than-meets-the-eye-pro/details?utm_source=chatgpt.com)

**[S3] — *Transformers: More Than Meets the Eye Rulesheet* — Tilt Forums.** Current detailed community rulesheet, explicitly updated to **code 0.89**; Missions, Energon/Rust, multiballs, Tech Specs, playfield X, saves and mini-wizards.
[Current Tilt Forums rulesheet](https://tiltforums.com/t/transformers-more-than-meets-the-eye-rulesheet/10229?utm_source=chatgpt.com)

**[S4] — Stern v0.89 software notes.** Current scoring-change evidence, especially Tech Spec Mania and Combiner MB.
[v0.89 Pro changelog](https://pinside.com/pinball/machine/transformers-more-than-meets-the-eye-pro/details?utm_source=chatgpt.com)

**[S5] — JLP Pinball Cards, *Transformers: More Than Meets the Eye*, updated July 2026.** Competitive quick-reference source; early tournament strategy and alternate plunge behavior; predates v0.89, so numerical rules are used cautiously.
[JLP Transformers card](https://pinballcards.net/transformers-more-than-meets-the-eye-2026/?utm_source=chatgpt.com)

**[S6] — Noah Crable, *Transformers Pinball Tutorial, Rules & Strategy Guide*, Kineticist, June 25, 2026.** Experienced strategy and physical-play source; mission/MB stacking, Energon/Rust choices, difficult ramps, Megatron technique and lower-playfield danger.
[Kineticist Transformers strategy guide](https://www.kineticist.com/news/transformers-pinball-tutorial?utm_source=chatgpt.com)

Research scope and required structure follow the supplied publishing-workflow brief.
