## Identity and versions

**Iron Maiden: Legacy of the Beast — Pro**, Stern Pinball, **2018**, SPIKE 2. Lead design **Keith Elwin**; software/rules **Rick Naegele and Elwin**; mechanical engineering **Harrison Drake**; art **Jeremy Packer / Zombie Yeti**; animation **Zac Stark**; sound **Jerry Thompson**. This was Elwin's first production design for Stern. [S1][S2]

The Pro shares the four-flipper/two-spinner layout, bullseye, three-bank drops and captive-ball rules architecture with Premium/LE, but lacks their motorized sarcophagus, moving center ramp/Underworld scoop and secret tomb entrance. On Pro, the center jump ramp is fixed and Mummy locks use the **center ramp**. [S1][S3]

Latest verified code: **v1.16.0, November 26, 2024**. Its gameplay changes are minor/system-oriented relative to the mature 1.xx ruleset. [S2]

Major scoring multiballs: **Trooper, Mummy, Cyborg**, plus the Eddie Battle multiballs **Aces High** and **Rime of the Ancient Mariner**. [S3]

## Thirty-second game plan

1. **Always work toward an Eddie Battle.** Shoot white arrows to spell E-D-D-I-E, then start the selected Battle at the center/bullseye shot. Single-ball Battles can be carried into Trooper or Mummy Multiball. [S3]
2. Complete Battles and then **cash the Soul Shard** at the bullseye: it starts at 20% of the Battle score and can score **2X/3X** depending on bullseye accuracy. [S3]
3. Build **2X/3X playfield** from the four orange X targets and save it for a Battle, multiball, Soul Shard, or large Power Jackpot. Qualified X carries between balls. [S3]
4. Use **Trooper Multiball** as the reliable major multiball: three locks, then jackpots → Super Jackpot; drop-bank Cannon shots can spot 1–3 jackpots and the first Cannon adds a ball. [S3][S4]
5. **Alternate scoring engine:** let Power Features accumulate, build the **Power Jackpot multiplier**, and only cash the Orb once it has become substantial. [S3][S4]

## Core rules and persistence

**Eddie Battles:** E-D-D-I-E qualification becomes harder as Battles are played. *Fear of the Dark*, *Hallowed Be Thy Name*, and *Flight of Icarus* are single-ball and may stack with Trooper/Mummy if started **before** the multiball. *Aces High* and *Rime* are themselves 2-ball multiballs and cannot stack with another multiball. [S3]

**Soul Shards:** winning a Battle lights a **10-second hurry-up** at the bullseye. Base value begins at 20% of that Battle's score; bullseye accuracy can double or triple it. Missing the hurry-up loses that Shard. Shards later enhance 2 Minutes to Midnight, Number of the Beast, Tomb progress and bonus. [S3]

**Trooper Multiball:** drop-bank awards cycle through Bonus X → Orb → Light Lock. Three virtual locks start MB. Three jackpots light Super; Super relights collected jackpots one multiplier level higher. **Trooper jackpot progress carries into later Trooper Multiballs.** [S3][S4]

**Power Jackpot:** sustained ramp/orbit/spinner/target/pop play activates five Power Features. Completing one lights the Orb for Power Jackpot; completing additional Power Features while it is lit adds **+1X**, while Eddie Cards and Tomb awards can add enormous base/multiplier value. It also receives playfield X. [S3]

**Huge but rare scoring leverage:** a 6-Way Combo ending in a **Super Deathblow** is 60M before multipliers; with Super Combos (5X) and 3X playfield, the verified ceiling is **900M**. It is not the normal tournament plan, but it is absolutely match-swinging. [S3]

## Skill shots

* **Normal Skill Shot:** soft plunge into the dedicated target — **1M, +1 EDDIE letter, +5s ball save**. [S3]
* **Super Skill Shot:** hold left flipper, plunge around the inner orbit to the upper flipper, then hit the Super Jackpot target. Current code's base is **10M**, plus instant Playfield X qualification and extra ball-save time. Older rulesheets still show 5M; Stern's changelog explicitly increased it. [S2][S3]
* **Secret left outlane:** direct plunge/upper-flipper feed to the left outlane — **25M**; historically also grants additional ball-save time. [S5]
* **Secret left inlane:** first switch left inlane — **5M**. [S5]
* **Secret center/bullseye:** soft-plunge then center shot — **6M**. [S5]
* **Secret right orbit:** first qualifying shot to right orbit — **8M**. [S5]

**Important tournament setting:** Secret Skill Shots default to **OFF in Competition Mode**, specifically avoiding outcomes such as the 25M outlane plunge. [S2]

## Secondary features

**Revive:** spinner hits spell R-E-V-I-V-E and light outlane rescues. Factory settings make the first qualification effectively two separate saves, one per outlane; harder settings can consume both at once. Lit Revives **carry between balls**. The left spinner itself is notoriously dangerous, so experienced players often work on it during multiball/ball save. [S3][S4]

**Orb Mystery:** drop-bank progression lights the Orb; repeating Light Orb before collection raises Mystery to Level 2/3. Competition Mode removes randomness from relevant awards. [S3]

**Extra Balls:** qualified from Power Features, Tomb Treasure #5 and loop progress. Current Competition Install sets **NO EXTRA BALLS**. Earlier mature code defines disabled-EB compensation as **10M, not multiplied by playfield X**. [S2][S3]

No player action button is used for normal gameplay.

## What to watch

* **White arrows / EDDIE completed:** Battle qualification is progressing; once complete, center is the start shot. [S3]
* **Bullseye flashing after a Battle:** the Soul Shard is on a short hurry-up; center accuracy determines 1X/2X/3X value. [S3]
* **2X/3X insert solid vs flashing:** solid = playfield multiplier qualified; flashing = active. [S3]
* **Power Jackpot value/multiplier on display:** if the player keeps refusing the lit Orb, they may intentionally be building a much larger cash-out. [S3][S4]

## Important shots

| Shot                   | Position           | Advances                                      | Why now?                                       | Risk                                   |
| ---------------------- | ------------------ | --------------------------------------------- | ---------------------------------------------- | -------------------------------------- |
| Bullseye / center ramp | Center             | Battle start, Soul Shard, Cyborg, mode finals | Central cash-out; accuracy can multiply awards | Direct center return                   |
| Left spinner / orbit   | Far left           | EDDIE, REVIVE, Power Spinners                 | Modes + outlane insurance                      | **Documented risky spinner return**    |
| Right ramp             | Right-center       | EDDIE, Power Ramps, Icarus                    | Flow shot and major mode scoring               | Reject can return quickly              |
| Trooper drops          | Lower-center       | Orb, Bonus X, locks, Cannon                   | Main MB qualification and utility              | Direct drop-bank rebounds              |
| Mummy captive ball     | Upper-center/right | MUMMY / Mummy MB                              | Safe-ish upper-flipper progression             | Repeated captive hits can lose control |
| Orb                    | Left-center        | Mystery, Power Jackpot                        | Cash a matured Power Jackpot                   | Direct target/rebound                  |

[S3][S4]

## Match strategy

**Playing ahead:** favor straightforward Battles, collect the Soul Shard instead of extending a completed mode for greed, take 2X playfield rather than risking extra X-target work for 3X, and use multiball ball-save time to build REVIVE. **Strategic inference**, consistent with competitive guides warning against overbuilding elaborate stacks. [S4]

**Playing behind:** bring *Hallowed* or *Flight of Icarus* into Trooper/Mummy, activate 3X playfield, and target a multiplied Soul Shard or mature Power Jackpot. *Flight of Icarus* ramp combos scale especially quickly; *Fear of the Dark* can also explode through spinner multipliers. [S3][S4]

**Key recurring decision:** **cash value now or keep building multipliers?** Maiden offers that choice repeatedly with Playfield X, Power Jackpot, Soul Shards, loop jackpots and multiball jackpot ladders. Strong players differ mainly in how much extra risk they accept before collecting.

## Danger zones

* **Left REVIVE spinner:** explicitly identified by competitive rules sources as a high-risk shot; best attacked with protection active. [S3][S4]
* **Bullseye:** required constantly but a square center hit can give a fast uncontrolled return.
* **Trooper drops:** valuable but repeated direct bank shots create center-rebound danger.
* **Upper-flipper mini-loop/Super target:** missing gives up a controlled upper-flipper possession and can send the ball back into traffic.
* **Outlane Secret Skill Shot:** if enabled, the 25M attempt is deliberately a drain-adjacent gamble; if the rescue timing fails, the ball can simply be gone. [S5]

## Spoken commentary cues

* “EDDIE is complete—center starts the Battle.”
* “Mode's finished, but the job isn't done: he's got ten seconds to cash the Soul Shard.”
* “Center bullseye matters here—the better hit can triple that Shard.”
* “Playfield X is qualified, not running yet; he's saving the inlane activation for something valuable.”
* “He's leaving the Power Jackpot lit because every additional completed feature can add another multiplier.”
* “That's the Cannon during Trooper—the first one adds a ball and can spot up to three jackpots.”

## Trivia

* Iron Maiden was **Keith Elwin's first production Stern design**; the playfield evolved from his earlier **Archer** homebrew layout. [S2][S3]
* All three editions use **four flippers and two spinners**, unusually dense shot geometry for a Stern of the period. [S1]
* The game contains **12 selectable Iron Maiden songs**, but song choice is purely soundtrack choice and does **not** determine gameplay. [S1][S3]
* Premium/LE add the motorized sarcophagus and lifting center ramp; the **Pro deliberately leaves those mechanisms out**, giving it distinct center-shot geometry. [S1]
* The deepest wizard mode, **Run to the Hills**, requires ten Tomb Treasures and begins a six-ball multiball. [S3]

## Questions for the humans

### Tournament and venue checks

1. Which code is installed?
   A. v1.16.0
   B. Older official Stern code
   C. Custom/community code
   D. Unsure

2. Is Stern's full **Competition Install** enabled?
   A. Yes
   B. Competition Mode only
   C. Custom tournament settings
   D. Unsure

3. Are **Secret Skill Shots** enabled?
   A. No — Competition default
   B. Yes
   C. Unsure
   *This matters because the left-outlane secret is worth 25M.*

4. How are Extra Balls handled?
   A. Competition Install — none
   B. Disabled for 10M
   C. Played normally
   D. Local tournament rule
   E. Unsure

5. What is the **Revive difficulty**?
   A. Factory/easier — left and right rescues consumed independently
   B. Hard — one rescue consumes both
   C. Unsure

6. Does this machine have a notable physical tendency?
   A. Left spinner returns are especially dangerous
   B. Bullseye rejects toward center
   C. Drop-bank rebounds are severe
   D. One upper-loop feed is unreliable
   E. Other: ___

### Uncertainties and conflicts

* **Super Skill Shot value:** the community rulesheet still prints **5M** [S3], but Stern's official changelog explicitly raised its base to **10M** [S2]. Use **10M on current code**.
* **Secret Skill Shots:** they exist in current code but default **OFF in Competition Mode**. Older tournament footage can therefore show behavior that a modern Competition Install will not. [S2]
* **Detailed rulesheet revision:** the current community rulesheet says it is based on **v1.10**, while current software is v1.16.0. Later releases primarily add system support and fixes; the notable v1.15 gameplay fix concerns *Rime of the Ancient Mariner*. [S2][S3]
* **Can I Play With Madness:** later code can make this feature available on Pro under certain Insider Connected/settings conditions, but tournament directors commonly disable it for game length. Confirm before putting it on the final one-page flow. [S3][S6]

## Human resolutions

1. Which code is installed?
   A. v1.16.0
   B. Older official Stern code
   C. Custom/community code
   D. Unsure
   **Human answer:** A. v1.16.0

2. Is Stern's full **Competition Install** enabled?
   A. Yes
   B. Competition Mode only
   C. Custom tournament settings
   D. Unsure
   **Human answer:** A. Yes

3. Are **Secret Skill Shots** enabled?
   A. No — Competition default
   B. Yes
   C. Unsure
   *This matters because the left-outlane secret is worth 25M.*
   **Human answer:** comp or comp mode unclear. a for skill shots

4. How are Extra Balls handled?
   A. Competition Install — none
   B. Disabled for 10M
   C. Played normally
   D. Local tournament rule
   E. Unsure
   **Human answer:** a or b

5. What is the **Revive difficulty**?
   A. Factory/easier — left and right rescues consumed independently
   B. Hard — one rescue consumes both
   C. Unsure
   **Human answer:** A. Factory/easier — left and right rescues consumed independently

6. Does this machine have a notable physical tendency?
   A. Left spinner returns are especially dangerous
   B. Bullseye rejects toward center
   C. Drop-bank rebounds are severe
   D. One upper-loop feed is unreliable
   E. Other: ___
   **Human answer:** E. Other: ___

## Sources

**[S1] — Stern Pinball, “Stern Pinball Announces New Iron Maiden Pinball Machines” + official Feature Matrix.** Manufacturer sources; release identity, music, all-model features and Pro/Premium/LE hardware differences.
[Stern launch announcement](https://www.sternpinball.com/2018/03/27/stern-pinball-announces-new-iron-maiden-pinball-machines/?utm_source=chatgpt.com)
[Official feature matrix PDF](https://sternpinball.com/wp-content/uploads/2018/10/Iron-Maiden-Pinball-Feature-Matrix.pdf?utm_source=chatgpt.com)

**[S2] — Stern Iron Maiden Pro software changelog, reproduced in Pinside Game Archive.** Version-sensitive source; latest **v1.16.0**, Competition Install, Secret Skill Shot adjustment, Super Skill Shot increase, EB compensation and current configuration behavior.
[Iron Maiden Pro software archive/changelog](https://pinside.com/pinball/machine/iron-maiden-legacy-of-the-beast/details?utm_source=chatgpt.com)

**[S3] — “Iron Maiden Pinball Rulesheet,” Pinball Rule Sheets / Tilt Forums.** Detailed community rules documentation; Eddie Battles, Soul Shards, Trooper/Mummy/Cyborg MB, Power Jackpot, multipliers, Revive, combos, Tomb Treasures and persistence.
[Iron Maiden rulesheet](https://pinballrulesheets.com/stern/iron-maiden-pinball-rulesheet?utm_source=chatgpt.com)

**[S4] — James McFatter, “Iron Maiden Pinball Tutorial, Strategy & Rules Guide,” Kineticist; David Lee, “Iron Maiden Guide,” Pinball for Mortals.** Experienced competitive strategy sources; Battle priorities, multiball play, Power Jackpot patience, Revive risk, loops and mode/multiball tradeoffs.
[Kineticist Iron Maiden tutorial](https://www.kineticist.com/news/iron-maiden-pinball-tutorial?utm_source=chatgpt.com)
[Pinball for Mortals Iron Maiden guide](https://www.pinballformortals.com/2019/12/15/iron-maiden-pinball-guide/?utm_source=chatgpt.com)

**[S5] — Tilt Forums / experienced-player Secret Skill Shot verification.** Glass-off testing and code-era discussion; supports 25M left outlane, 5M left inlane, 6M center and 8M right-orbit secret shots.
[Secret Skill Shot verification thread](https://tiltforums.com/t/iron-maiden-pinball-rulesheet/3787?page=19&utm_source=chatgpt.com)

**[S6] — INDISC 2019 game-settings discussion, Tilt Forums.** Tournament evidence; Iron Maiden was run on hard settings with short multiball saves, Competition Mode and **Can I Play With Madness disabled**.
[INDISC 2019 settings discussion](https://tiltforums.com/t/indisc-2019-game-settings-discussion/4790?utm_source=chatgpt.com)
