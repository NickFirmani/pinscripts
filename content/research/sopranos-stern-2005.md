Research brief following the attached specification for **The Sopranos (Stern, 2005)**. Pasted text

## Identity and versions

**The Sopranos** — Stern Pinball, 2005. Design: **George Gomez**; software/rules credits include **Dwight Sullivan, Lonnie D. Ropp, and Lyman F. Sheats Jr.**; artwork by Kevin O’Connor; music/sound by Chris Granner. Modified Stern Whitestar platform, DMD, two flippers. About **3,500** produced. [S1][S2] [Pinside](https://pinside.com/pinball/machine/sopranos/details?utm_source=chatgpt.com)

- **Rules basis: `rom` — CPU 5.00 (`sopcpua.500`)**, released **2005-10-26**. Display ROM is also 5.00. The final update added tournament settings; the substantive gameplay fixes were already present in earlier revisions. [S2] [Pinside](https://pinside.com/pinball/shops/shop/1083-matt-s-basement-arcade/01580-sopranos-pinball-stern-rom-upgrade-chip-set)
- Major multiballs: **Stugots Multiball, Bing Multiball, Underboss Multiball**; deep wizard mode **Boss** is also a multiball-style mode. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)
- No edition split.

## Thirty-second game plan

1. **Tournament default: get Stugots Multiball quickly.** With the normal manual plunger, strong players can short-plunge to a flipper, hit the Stugots drop target/lock, and exploit playfield validation so an immediate drain may be returned without consuming the normal ball save. Repeat for the second lock. **Observed strategy.** [S4][S5] [Tilt Forums](https://www.tiltforums.com/t/list-of-exploits-that-are-allowed-disallowed-in-tournament-play/5399/?utm_source=chatgpt.com)
2. During Stugots, work the drop target toward **Double Jackpot and Super Jackpot**; the Super is worth over 3M and is also required for Boss. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)
3. Use multiball protection to attack the dangerous **Safe**, left ramp/Bing, loops, and envelopes. Advancing ranks eventually triggers **Underboss**, a 4-ball multiball with 1x/3x/5x lock payoffs. [S3][S6] [Pinball.org](https://pinball.org/rules/sopranos.pdf)
4. **Stack before cashing:** an Episode must be started *before* multiball to coexist with it; Stugots and Bing can also stack, and Underboss can be added on top if the rank is reached while another multiball is running. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf?utm_source=chatgpt.com)
5. Alternate route when the boat exploit is disabled: build **Bing Multiball** on the left ramp and progress ranks through envelopes rather than repeatedly bashing the Safe.

## Core rules and persistence

**Stugots:** knock down the drop target, then lock **two balls** in the boat. During multiball, the drop target scores the initial Jackpot; three drop-target hits then expose the boat for **Double Jackpot (~2.15M)** and another boat shot for **Super Jackpot (~3.225M)**. After the Super, the five main arrows become jackpots and the sequence can repeat. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)

**Bing:** three left-ramp shots start **Party at the Bing**, a 30-second switch-count mode. The first qualification needs 75 switch hits; incomplete progress is saved. Completion immediately starts 3-ball Bing Multiball, where all major shots score jackpots starting at 125K and building to 250K. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)

**Ranks:** collecting the four envelope shots lights Advance Rank at the inner loop; completing the Safe also advances rank. Each new rank starts a **feature-specific 2x scoring period for the rest of that ball**—for example Double Safe, Double Truck Heist or Double Episode. Reaching **Underboss** starts 4-ball Underboss Multiball. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)

**Underboss:** major arrows and the Safe spell UNDERBOSS. Completing it lights three ball locks; successive locks pay **1x, 3x, then 5x** values before balls are released and the cycle repeats. This is one of the game's biggest scoring escalators. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)

Episodes cannot stack with each other, but one Episode can stack with a multiball if the Episode starts first. Episode timers pause while the ball is in the pop bumpers. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)

## Skill shots

- **Normal Skill Shot:** lane-change the flashing **R-I-P** top lane and plunge through it. Scores **500K +250K per previous successful skill shot**, also burying a character and advancing the associated Bonus X. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)
- **Super Skill Shot:** hold the **left flipper** while plunging; the ball loops back to the flippers and gives roughly five seconds to make a feature shot. Particularly useful choices:
  - left ramp → **start Bing**
  - inner loop → **light/start an Episode**
  - right ramp → awards **three Meadowlands hits**
  - right loop → **start Truck Heist hurry-up**. [S3] [Pinball.org](https://pinball.org/rules/sopranos.pdf)
- In tournaments, the **short-plunge Stugots validation setup** is often more strategically important than either formal skill shot. [S4]

## Secondary features

- **Fish / Add-A-Ball:** spell F-I-S-H through the in/outlanes to light the left saucer. Its award is state-sensitive; during multiball one of its first useful awards is **Add-A-Ball**, normally once per multiball. It can also give Bing hits, R-I-P progress, episode time, or an envelope. [S3] [doczz.net](https://doczz.net/doc/67542/sopranos-rulesheet-v1.6-en?utm_source=chatgpt.com)
- **Ball save:** final code inherits an approximately **8-second factory start-of-ball saver**; the Stugots exploit is powerful because the short plunge/drop-target sequence can leave the playfield *unvalidated*, so a drain may return the ball before that saver even starts. [S2][S4] [Pinside](https://pinside.com/pinball/shops/shop/1083-matt-s-basement-arcade/01580-sopranos-pinball-stern-rom-upgrade-chip-set)
- **Executive Game:** one Episode is a poker video mode where the player can wager points and can actually **lose score**, an unusually important commentary caveat. [S3] [doczz.net](https://doczz.net/doc/67542/sopranos-rulesheet-v1.6-en?utm_source=chatgpt.com)
- **Pork Store:** random/mystery-style awards include progress toward rank, Meadowlands, Truck Heist, spinner value and other features. ROM 5.00 added tournament settings, but I did not locate an authoritative full deterministic award table. [S2][S3] [Pinside](https://pinside.com/pinball/shops/shop/1083-matt-s-basement-arcade/01580-sopranos-pinball-stern-rom-upgrade-chip-set)
- **Extra Ball:** Acting Capo lights an EB at the inner loop. Tournament point conversion is **uncertain**; community references disagree on exact value, so do not print a universal number without checking configuration. [S3][S7] [Tilt Forums](https://tiltforums.com/t/points-for-extra-ball-wiki/2725/?utm_source=chatgpt.com)

## What to watch

1. **Boat drop target down / LOCK lit:** the player is building the easiest major multiball.
2. **Stugots Super Jackpot insert/callout:** the next boat hit can be the big payoff and also checks a Boss requirement.
3. **Rank indicator approaching Underboss:** the player may suddenly trigger a 4-ball multiball, potentially on top of Stugots/Bing.
4. **Fish lit during multiball:** expect an Add-A-Ball attempt rather than a normal scoring shot.

## Important shots

| Shot | Position | Advances | Why now? | Risk |
|---|---|---|---|---|
| **Stugots / Boat** | Upper-right | Locks, Stugots JP/Super | Fastest tournament scoring route | Ramp can reject; boat releases can feed awkwardly toward center [S8] |
| **Left Ramp / Bing** | Left-center | Party at the Bing / Bing MB | Stack another multiball and build Boss progress | Reject loses control |
| **Inner Loop / Spinner** | Center-left | Episodes, Rank, EB, Boss | Converts envelopes/rank and starts modes | Exits through pops, surrendering possession |
| **Safe** | Center | Rank; Boss requirement | Fastest rank progress, especially under MB protection | Direct center rebound; shallow saucer can reject SDTM [S6][S8] |
| **Fish** | Far left saucer | Add-A-Ball / contextual awards | Extend multiball or spot needed progress | Saucer eject returns uncontrolled |
| **Right Ramp / Meadowlands** | Right | Meadowlands, Episodes, envelopes | Boss progression and useful doubled scoring | Entrance is also the pop-bumper exit, especially messy in MB |

## Match strategy

**Playing ahead:**  
**Observed strategy:** exploit or otherwise reach Stugots quickly, take its Jackpot/Super sequence, and use envelopes rather than naked Safe shots to advance rank. If already scoring comfortably, avoid over-investing in Boss progression.

**Playing behind:**  
Start an Episode first, then stack **Stugots + Bing**, pound the Safe while protected, and try to reach **Underboss while the earlier multiball is still active**. Underboss's 3x/5x lock awards give much more comeback ceiling. [S3][S6]

**Key recurring decision:**  
**Start Stugots immediately or build the stack first.** Immediate Stugots is extremely safe/efficient—especially with validation abuse—but delaying it long enough to light an Episode, Bing, or rank progression can create a vastly stronger stacked multiball.

## Danger zones

- **Safe:** the most obvious center-drain lure; hard hits rebound directly toward the flippers, and its shallow saucer can spit balls back out. [S6][S8]
- **Stugots ramp:** strong shots can bounce back; releases from the boat can occasionally head between the flippers. [S8]
- **Right ramp:** it is also the pop-bumper exit, so an intended shot can collide with an exiting ball during multiball. [S3]
- **Inner loop/pop feed:** many successful features intentionally give up controlled possession to the bumpers.

## Spoken commentary cues

- “That boat drop target doesn't validate the playfield—this is the famous Sopranos short-plunge multiball setup.”
- “Two balls in Stugots starts the boat multiball; now they're working toward the Double and Super Jackpot.”
- “They're using multiball as cover to hit the Safe—that shot is much nastier in single-ball play.”
- “Underboss just started on top of the existing multiball; the lock values can climb to five-times.”
- “The Fish is lit during multiball—that's usually an Add-A-Ball opportunity.”
- “That Episode had to be started first; Sopranos won't let you add an Episode after the multiball is already running.”

## Trivia

- The game includes recorded voices from **James Gandolfini, Dominic Chianese and Steven Van Zandt**. [S1] [Pinside](https://pinside.com/pinball/machine/sopranos/details?utm_source=chatgpt.com)
- George Gomez and Lyman Sheats were both fans of the TV series, and Gomez later described the design as unusually easy to brainstorm because of the strength of the theme. [S9] [Kineticist](https://www.kineticist.com/promoters/wedgehead-pinball-podcast/episode-78-sopranos-pinball-w-george-gomez?utm_source=chatgpt.com)
- The Safe physically **splits open** to reveal a saucer behind it. [S1][S8]
- The Stugots is a genuine **two-ball physical lock** shaped around Tony's yacht. [S1][S3]
- Stern's final 5.00 update arrived only in October 2005, months after production began, and specifically added tournament settings. [S2]

## Questions for the humans

### Edition and configuration checks

1. Is the tournament preserving the **Stugots playfield-validation exploit**?
   A. Yes — standard manual plunger, exploit allowed  
   B. Mechanically nerfed / auto-launch or shooter removed  
   C. Normal hardware but tournament rules prohibit it

2. Should the finished page assume **Competition Mode**?
   A. Yes  
   B. No  
   C. Mention only that it normalizes some random/global behavior

3. Is CPU **5.00** the intended ROM baseline?
   A. Yes  
   B. Older ROMs may appear, so avoid revision-sensitive tournament statements

### Uncertainties and conflicts

1. **Extra-ball point conversion conflicts.** The Tilt Forums points wiki lists **10M** for Sopranos [S7], while a separate tournament discussion claims **25M** and is immediately challenged by another experienced player.  
   A. Omit the number  
   B. Verify on CPU 5.00 / event settings before publication

2. ROM 5.00 definitely adds **tournament settings** [S2], but I did not locate a reliable Sopranos-specific table documenting exactly how every Pork Store/Fish/random award is normalized.

## Human resolutions

1. Is the tournament preserving the **Stugots playfield-validation exploit**?
   A. Yes — standard manual plunger, exploit allowed  
   B. Mechanically nerfed / auto-launch or shooter removed  
   C. Normal hardware but tournament rules prohibit it
   **Human answer:** Yes

2. Should the finished page assume **Competition Mode**?
   A. Yes  
   B. No  
   C. Mention only that it normalizes some random/global behavior
   **Human answer:** A. Yes

3. Is CPU **5.00** the intended ROM baseline?
   A. Yes  
   B. Older ROMs may appear, so avoid revision-sensitive tournament statements
   **Human answer:** A. Yes

1. **Extra-ball point conversion conflicts.** The Tilt Forums points wiki lists **10M** for Sopranos [S7], while a separate tournament discussion claims **25M** and is immediately challenged by another experienced player.  
   A. Omit the number  
   B. Verify on CPU 5.00 / event settings before publication
   **Human answer:** A. Omit the number

2. ROM 5.00 definitely adds **tournament settings** [S2], but I did not locate a reliable Sopranos-specific table documenting exactly how every Pork Store/Fish/random award is normalized.
   **Human answer:** ok

## Sources

**[S1] — The Sopranos Game Manual / Instruction Card** — Stern Pinball — manufacturer documentation; identity, objectives, locks, Safe, Bing, Extra Ball and adjustments.  
[Official Stern Sopranos manual](https://sternpinball.com/wp-content/uploads/2018/12/Sopranos_Manual.pdf?utm_source=chatgpt.com)

**[S2] — The Sopranos CPU 5.00 Stern README / revision history** — Stern text mirrored by Pinside — ROM source; exact **5.00 / 2005-10-26** release, prior fixes, tournament-settings addition.  
[Sopranos 5.00 ROM revision history](https://pinside.com/pinball/shops/shop/1083-matt-s-basement-arcade/01580-sopranos-pinball-stern-rom-upgrade-chip-set)

**[S3] — Sopranos Rulesheet v1.6** — SpiderMan / Flippermarkt — detailed community rulesheet; skill shots, ranks, multiballs, stacking, Fish, Boss.  
[Sopranos Rulesheet PDF](https://pinball.org/rules/sopranos.pdf?utm_source=chatgpt.com)

**[S4] — List of Exploits Allowed / Disallowed in Tournament Play** — Tilt Forums — competitive rules source; confirms Stugots playfield-validation technique and its tournament legality in documented rulesets.  
[Tilt Forums exploit reference](https://www.tiltforums.com/t/list-of-exploits-that-are-allowed-disallowed-in-tournament-play/5399/?utm_source=chatgpt.com)

**[S5] — Games to exploit playfield validation / Opening Gambits** — Tilt Forums — tournament strategy evidence for short-plunge Stugots as the dominant opening exploit.  
[Sopranos validation discussion](https://www.tiltforums.com/t/games-to-exploit-playfield-validation/6654/?utm_source=chatgpt.com)

**[S6] — The Sopranos strategy article** — Bright Lights Bumper City — observed strategy; Bing safety, Safe danger, and attacking the Safe under multiball protection.  
[Sopranos strategy article](https://bumpercity.blogspot.com/2014/11/the-sopranos.html?utm_source=chatgpt.com)

**[S7] — Points for Extra Ball Wiki / tournament discussion** — Tilt Forums — secondary evidence for disputed disabled-EB point values.  
[Points for Extra Ball Wiki](https://tiltforums.com/t/points-for-extra-ball-wiki/2725/?utm_source=chatgpt.com)

**[S8] — The Sopranos first-look playfield review** — Pinball News/BMI archive — physical-feed source; Safe saucer rejects, boat-ramp rejects/releases and pop/right-ramp interaction.  
[Sopranos playfield review](https://www.bmigaming.com/Discontinued/sopranospinball-pinballnewsreview.htm?utm_source=chatgpt.com)

**[S9] — Sopranos Pinball with George Gomez** — Wedgehead/Kineticist — designer interview summary; design history and Gomez/Sheats theme context.  
[George Gomez Sopranos interview summary](https://www.kineticist.com/promoters/wedgehead-pinball-podcast/episode-78-sopranos-pinball-w-george-gomez?utm_source=chatgpt.com)
