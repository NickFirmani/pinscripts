Using the uploaded brief as the specification for the research output. 

## Identity and versions

* **Total Nuclear Annihilation (TNA)** — Spooky Pinball, **2017**; P3-ROC solid-state platform. Designed, engineered, programmed, scored, and sound-designed principally by **Scott Danesi**; art by **Matt Andrews**; software also credits **Jimmy Lipham and Michael Ocean**. Original production: **550**. [S1][S5] ([Total Nuclear Annihilation Pinball][1])
* **Collector’s Edition (2022): 250 units.** The official documentation says original and CE rules are “almost identical”; CE differences are primarily upgraded components/cosmetics rather than a separate ruleset. [S1][S5] ([Total Nuclear Annihilation Pinball][1])
* Latest verified code: **v1.6.0, December 13, 2025**. It materially changed jackpot farming and added Tournament Mode. [S3] ([Total Nuclear Annihilation Pinball][2])
* One primary **3-ball Multiball**, expandable to **4 balls** via Super Jackpot/add-a-ball. [S2] ([Tilt Forums][3])

## Thirty-second game plan

1. **Destroy reactors.** Fill the 3×3 keypad grid, shoot the scoop to start the reactor, then send the ball through the lit orbit(s) into the upper Reactor area until it reaches **100% / Critical**. [S2] ([Tilt Forums][4])
2. Once Critical, hit the flashing **RAD / DESTROY / pop-bumper** shots to destroy it. Reactor progress **carries between balls**. [S2]
3. **Observed strategy:** build Multiball alongside reactor progress and, when practical, destroy reactors with multiple balls alive. Multiball's playfield multiplier equals the number of balls in play, making reactor destruction one of the game's biggest scoring moments. [S2][S3] ([ManualsLib][5])
4. In Multiball, hit the three inline drops for **1× → 2× → 3× Jackpot**, then the scoop for **5× Super Jackpot**; Super Jackpot can add a fourth ball. [S2]
5. On v1.6.0, don't endlessly farm one reactor: the second Multiball on the same reactor cuts jackpots to **55%**, and the third+ to **10%**; advancing to the next reactor restores full value. [S3][S4] ([Total Nuclear Annihilation Pinball][2])

## Core rules and persistence

* There are **nine reactors**. Later reactors require more upper-playfield progress and more kill shots, while their scoring increases. Reactor state persists ball-to-ball. [S2] ([Tilt Forums][4])
* The keypad's pink/blue 3×3 grid qualifies Reactor Start. A **Hands-Free Skill Shot instantly completes this grid**, making it extraordinarily valuable. [S2]
* Once started, spinner and upper Reactor switches raise both critical percentage and Reactor Value. The 1-2-3 upper targets are the quickest documented way to max that value. Reactor 1 maxes at 75K, Reactor 2 at 112.5K, Reactor 3 at 150K. [S2]
* Once Critical, reactor kill shots are randomly selected from RAD, DESTROY, and the pop bumper. Higher reactors require more of them. [S2]
* During an active reactor, refilling the keypad scores a **Reactor Jackpot = 25% of current Reactor Value**. [S2]
* Locks are physical and **shared/stealable in multiplayer**: the next player receives credit for balls already physically locked. [S2]
* In Multiball, playfield scoring is multiplied by **balls in play**. The current code explicitly incorporates ball count into reactor-destruction scoring. [S3]
* Destroying Reactor 9 **ends the game**. The final Total Nuclear Annihilation bonus is the accumulated value of the destroyed reactors; remaining balls award that bonus again rather than continuing play. [S2] ([Tilt Forums][6])

## Skill shots

**Hands-Free Skill Shot**

* Before plunging, flippers select a lit C-O-R-E lane; once the shooter switch opens, selection freezes.
* Make that lane **without changing it after launch**.
* Awards **100K**, completes the entire reactor keypad, and adds a full lane-ball-save level. If a reactor is already running, it awards a Reactor Jackpot instead. [S2]

**Regular Skill Shot**

* Move the lit C-O-R-E lane **after plunging**, then hit it.
* Awards **50K** plus one full lane-ball-save level. [S2]

**Secret Skill Shot**

* With fewer than two locks, full-plunge around and quickly shoot the lock lane.
* Awards **100K and locks the ball**. [S2]

**Super Secret Skill Shot**

* Added by later code: full plunge, **do not flip the left flipper**, dead-bounce to the right and backhand the lock lane.
* Awards **100K**; later code also added ball-save protection to secret-skill-shot play. [S6] ([This Week in Pinball][7])

## Secondary features

* **SAVE ball save:** S-A-V-E are the four in/outlanes and can be lane-changed with the flippers. Light three, then collect the flashing fourth for a **10-second save**. Multiple levels can be banked; unused levels add 10K each to bonus. [S2]
* **Mystery:** complete R-A-D, then scoop. Awards include grid completion, lock enable, Super Spinner, ball save, Bonus X and points. **v1.6.0 Tournament Mode fixes the award order and removes free-point Mystery awards.** [S2][S3]
* Tournament Mode **does not disable Extra Balls**. EBs are normally awarded at reactor thresholds; manual defaults shown in surviving documentation are reactors **3 and 6**. [S3] ([ManualsLib][8])
* Completing C-O-R-E also raises end-of-ball Bonus X. [S2]
* No video mode or conventional action button.

## What to watch

1. **All-pink keypad / scoop flashing:** Reactor Start is ready.
2. **Upper numeric display near 100 + red beacon:** reactor is about to become Critical; next phase moves back downstairs to kill shots. [S2][S7] ([Kineticist][9])
3. **White flashing RAD/DESTROY/pop shots:** player is one sequence away from collecting the Reactor Bonus.
4. **Balls physically trapped behind inline drops:** shared locks; two means the next lock shot starts Multiball.

## Important shots

| Shot             | Position            | Advances                           | Why now?                                    | Risk                                                               |
| ---------------- | ------------------- | ---------------------------------- | ------------------------------------------- | ------------------------------------------------------------------ |
| Keypad targets   | Center              | Reactor qualification / Reactor JP | Core progression                            | Direct standups; rules documentation calls grid shooting dangerous |
| Reactor scoop    | Left-center         | Start reactor / Mystery            | Converts completed grid into active reactor | **Very fast kickout**                                              |
| Lit orbit        | Far left/right      | Reactor heating                    | Safest way to reach upper Reactor area      | Slow right-orbit return clips sling                                |
| Inline lock lane | Right-center        | Locks / MB jackpots                | Builds protection and major scoring         | Gets more dangerous as drops descend                               |
| RAD / DESTROY    | Lower sides         | Reactor kill shots                 | Cash reactor once Critical                  | Standup rebounds under pressure                                    |
| Lock scoop       | Behind inline drops | 5× Super / add-a-ball              | Biggest MB jackpot and restores 4× PF       | Deep, narrow shot under multiball chaos                            |

[S2][S7] ([Tilt Forums][4])

## Match strategy

**Playing ahead:** prioritize reactor advancement over repeated same-reactor Multiballs. On v1.6.0, jackpot decay makes farming the same stage progressively unattractive. Take the Hands-Free Skill Shot, advance safely, and cash reactor kills rather than forcing marginal grid shots.

**Playing behind:** synchronize a **high-value reactor kill with 3×/4× Multiball**, then attack the 3× Jackpot → 5× Super sequence. Later-reactor jackpots also scale sharply with reactor number and balls in play. [S3][S4]

**Key recurring decision:** **destroy the reactor now, or delay until Multiball?** Immediate destruction secures progress; waiting risks the ball but can multiply the game's largest scoring resource. Scott Danesi's own one-reactor competition advice was to max reactor value and destroy it in Multiball. [S2][S7] ([Scott Danesi][10])

## Danger zones

1. **Keypad standups:** required progression with direct center-target rebound risk; Multiball is valuable precisely because it lets chaos complete these more safely. [S2]
2. **Reactor-scoop eject:** official rules warn how quickly it fires the ball back. [S2]
3. **Slow right-orbit return:** Scott Danesi confirms the geometry intentionally sends slow rollers onto the top of the right sling. [S7] ([Pinside][11])
4. **Deep inline drops:** backhanding remains possible, but each lowered target makes the lock lane increasingly hazardous. [S2]
5. **Upper Reactor exit:** chaotic slings/kickers plus a mini-flipper can return the ball downstairs with substantial speed.

## Spoken commentary cues

* “Hands-free skill shot—that completes the whole keypad, so Reactor Start is already ready.”
* “Reactor's at one hundred percent; now the white lower-playfield shots are the kill sequence.”
* “They're waiting on the reactor kill because three balls alive means **three-times playfield**.”
* “First, second, third drop are the one-, two-, and three-times jackpots; the scoop behind them is the **five-times Super**.”
* “That's their second Multiball on this same reactor, so on 1.6 the jackpots are already down to **55 percent**.”
* “Two balls are physically locked—and on TNA those locks are stealable.”

## Trivia

* Scott Danesi began TNA as a **homebrew project in November 2015**; Spooky picked it up for production in 2016, with production beginning in 2017. [S1] ([ManualsLib][12])
* Danesi deliberately designed it as an **early-1980s Bally-style game using modern electronics, displays and lighting**. [S1]
* Danesi also composed the game's celebrated **synthwave soundtrack** and sound package. [S5]
* The physical two-tier lock is commonly called the **“Danesi Lock.”** [S7] ([Kineticist][9])
* Destroying all nine reactors is unusually literal: **you win, the flippers shut off, and the game ends.** [S2]

## Questions for the humans

### Tournament and venue checks

1. What code is installed?
   A. **v1.6.0**
   B. v1.5.x
   C. Earlier
   D. Newer / beta
   E. Unknown

2. Is **Tournament Mode** enabled?
   A. Yes
   B. No
   C. Unknown

3. How are Extra Balls handled?
   A. Played normally
   B. Disabled
   C. Must be plunged
   D. Converted / tournament ruling
   E. Other

4. What is **Reactor Difficulty**?
   A. Easy
   B. Medium/default
   C. Hard
   D. Custom
   E. Unknown

5. Are stock **shared physical locks** being used?
   A. Yes — lock stealing allowed
   B. Event has a special ruling
   C. Unknown

6. Which feed is most dangerous on this copy?
   A. Reactor scoop eject
   B. Slow right-orbit return
   C. Keypad rebounds
   D. Inline-lock rebounds
   E. Upper-Reactor exit
   F. Nothing unusual

### Uncertainties and conflicts

* **Old jackpot documentation is obsolete on v1.6.0.** Earlier rulesheets describe a simple reactor/balls-in-play formula [S2]; current code additionally reduces jackpots to **55% on the second Multiball and 10% on the third+ Multiball on the same reactor**. [S3][S4]
* **Tournament Mode is new in v1.6.0** and fixes Mystery ordering, but explicitly **does not remove Extra Balls**. Event organizers still need to handle EBs separately. [S3]
* Reactor Difficulty is operator-adjustable and changes **initial keypad spots, heating requirements and kill-shot requirements**; it materially affects expected progression speed. [S1]
* Original and CE rules are officially described as nearly identical [S1], but physical upgrades can still change lock, scoop and feed behavior.
* Physical lock stealing is intentional under standard multiplayer rules. Any event-specific anti-stealing ruling should be communicated before play. [S2]

## Human resolutions

1. What code is installed?
   A. **v1.6.0**
   B. v1.5.x
   C. Earlier
   D. Newer / beta
   E. Unknown
   **Human answer:** A. **v1.6.0**

2. Is **Tournament Mode** enabled?
   A. Yes
   B. No
   C. Unknown
   **Human answer:** A. Yes

3. How are Extra Balls handled?
   A. Played normally
   B. Disabled
   C. Must be plunged
   D. Converted / tournament ruling
   E. Other
   **Human answer:** B. Disabled

4. What is **Reactor Difficulty**?
   A. Easy
   B. Medium/default
   C. Hard
   D. Custom
   E. Unknown
   **Human answer:** default

5. Are stock **shared physical locks** being used?
   A. Yes — lock stealing allowed
   B. Event has a special ruling
   C. Unknown
   **Human answer:** A. Yes — lock stealing allowed

6. Which feed is most dangerous on this copy?
   A. Reactor scoop eject
   B. Slow right-orbit return
   C. Keypad rebounds
   D. Inline-lock rebounds
   E. Upper-Reactor exit
   F. Nothing unusual
   **Human answer:** F. Nothing unusual

## Sources

**[S1]** *Total Nuclear Annihilation Documentation & Downloads* — Danesi Designs / official TNA site. **Official documentation hub.** Original/CE manuals, Reactor Difficulty matrix and current jackpot tables.
[Official TNA documentation](https://tnapinball.com/documentation.php)

**[S2]** *Total Nuclear Annihilation Rulesheet* — Tilt Forums Wiki Rulesheets, with direct contributions/corrections from Scott Danesi. **Detailed rules source.** Skill shots, reactors, persistence, locks, Multiball, saves, Mystery and endgame.
[TNA rulesheet](https://tiltforums.com/t/total-nuclear-annihilation-rulesheet/3209)

**[S3]** *Total Nuclear Annihilation v1.6.0 Code Update* — Scott Danesi / official TNA site, December 13, 2025. **Primary software source.** Current code, jackpot decay, Reactor Bonus fix and Tournament Mode.
[Official TNA code updates](https://www.tnapinball.com/code-updates.php?utm_source=chatgpt.com)

**[S4]** *TNA Jackpot Value Lookup Table — Code v1.6.0* — Danesi Designs. **Primary current scoring table.** Jackpot values by reactor, balls in play and repeat Multiball count.
[Official v1.6.0 jackpot table](https://tnapinball.com/docs/TNA%20Jackpot%20Value%20Lookup%20-%20Sheet1.pdf)

**[S5]** *Total Nuclear Annihilation Machine Archive* — The Pinball Archive / IPSND. **Identity and production source.** Credits, P3-ROC, original 550-unit run and 2022 CE context.
[The Pinball Archive — TNA](https://www.pinballarchive.com/machines/total-nuclear-annihilation?utm_source=chatgpt.com)
[IPSND — TNA](https://www.ipsnd.net/view.aspx?id=6444&utm_source=chatgpt.com)

**[S6]** *Total Nuclear Annihilation Super Secret Skill Shot* — This Week in Pinball / Kineticist, January 2019. **Contemporary developer-revealed rules source.** Super Secret Skill Shot procedure.
[Super Secret Skill Shot report](https://twip.kineticist.com/p/twip-tuesday-january-15th-2019?utm_source=chatgpt.com)

**[S7]** *TNA competitive/physical observations* — Kineticist/Dead Flip and Scott Danesi owner-thread comments. **Designer and competitive-play evidence.** Danesi Lock, beacon, lock stealing, right-orbit geometry and reactor-in-Multiball strategy.
[Kineticist TNA observations](https://www.kineticist.com/news/total-nuclear-annihilation-five-things-seen-heard-learned?utm_source=chatgpt.com)
[Scott Danesi geometry discussion](https://pinside.com/pinball/forum/topic/total-nuclear-annihilation-cluball-welcome/page/149?utm_source=chatgpt.com)

[1]: https://tnapinball.com/documentation.php "Total Nuclear Annihilation Documentation & Downloads"
[2]: https://tnapinball.com/?utm_source=chatgpt.com "Total Nuclear Annihilation Pinball - Official Website"
[3]: https://tiltforums.com/t/total-nuclear-annihilation-rulesheet/3209?page=2 "Total Nuclear Annihilation Rulesheet - Page 2 - Wiki Rulesheets - Tilt Forums"
[4]: https://tiltforums.com/t/total-nuclear-annihilation-rulesheet/3209 "Total Nuclear Annihilation Rulesheet - Wiki Rulesheets - Tilt Forums"
[5]: https://www.manualslib.com/manual/2078091/Spooky-Pinball-Total-Nuclear-Annihilation.html?page=10&utm_source=chatgpt.com "Spooky Pinball Total Nuclear Annihilation Service Manual (Page 10 of 36) | ManualsLib"
[6]: https://tiltforums.com/t/total-nuclear-annihilation-rulesheet/3209/44?utm_source=chatgpt.com "Total Nuclear Annihilation Rulesheet - #44 by bkerins - Wiki Rulesheets - Tilt Forums"
[7]: https://twip.kineticist.com/p/twip-tuesday-january-15th-2019?utm_source=chatgpt.com "TWIP Thursday: January 17th, 2019"
[8]: https://www.manualslib.com/manual/2078091/Spooky-Pinball-Total-Nuclear-Annihilation.html?page=13&utm_source=chatgpt.com "Spooky Pinball Total Nuclear Annihilation Service Manual (Page 13 of 36) | ManualsLib"
[9]: https://www.kineticist.com/news/total-nuclear-annihilation-five-things-seen-heard-learned?utm_source=chatgpt.com "Total Nuclear Annihilation – Five Things Seen/Heard/Learned | Kineticist"
[10]: https://www.scottdanesi.com/?cat=15&utm_source=chatgpt.com "Total Nuclear Annihilation | ScottDanesi.com"
[11]: https://pinside.com/pinball/forum/topic/total-nuclear-annihilation-cluball-welcome/page/149?utm_source=chatgpt.com "Total Nuclear Annihilation Club...Welcome to the future! | All clubs (...members only!) | Pinside.com"
[12]: https://www.manualslib.com/manual/2078091/Spooky-Pinball-Total-Nuclear-Annihilation.html?utm_source=chatgpt.com "SPOOKY PINBALL TOTAL NUCLEAR ANNIHILATION SERVICE MANUAL Pdf Download | ManualsLib"
