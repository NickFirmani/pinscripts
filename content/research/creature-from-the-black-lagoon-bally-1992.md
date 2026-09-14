## Identity and versions

* **Creature from the Black Lagoon** — Bally/Midway, **1992**, Williams **WPC Fliptronics II**. Design: **John Trudeau**; software: **Jeff Johnson**; art: **Kevin O’Connor**; mechanics: Ernie Pizarro; music/sound: Paul Heitsch. About **7,841** produced. [S4] ([Kineticist][1])
* One physical edition; the important distinction is software.
* **Rules basis: `rom` — Revision 5.0**, U6 `rev 50.rom`, released **2020-11-01** by Planetary Pinball under license from Williams. It is based on factory L-4 but fixes scoring bugs and adds competition-oriented deterministic options. [S1] ([Planetary Pinball][2])
* Stock **L-4** remains common. Rev 5.0 materially differs: tournament mode can make the Girl search deterministic, fixes Snack Attack/Move Your Car/playfield-X/Super Jackpot bugs, makes Playground and Snackbar awards patterned, and fixes bonus-X calculation. [S1]
* One major mode: **2-ball Multiball**, culminating in Jackpot and Super Jackpot. [S2]

Research scope follows the supplied brief.

## Thirty-second game plan

1. **Spell F-I-L-M** to light Multiball: K-I-S-S gives F, Snackbar/Menu gives I, P-A-I-D gives L, and the right Slide scoop gives M. [S2]
2. Lock at either saucer to begin **2-ball Multiball**, then search the three caves until the Girl is found. [S2]
3. Before cashing the big value, repeatedly shoot the **Left/Creature Ramp** so the Whirlpool spells CREATURE and raises the playfield multiplier—normally as high as **4×**. [S2]
4. Rescue at the Snackbar, shoot it again for **Jackpot**, get the required pop hits, then return to Snackbar for **Super Jackpot**, worth twice the base Jackpot and multiplied by playfield-X. [S2]
5. **Alternate tournament route:** repeated Center Shots into **Move Your Car** are comparatively controllable and can score up to **80M** per perfect round; Unlimited Millions from the Slide can also become enormous on a player who can loop the Left Ramp. [S2][S3][S5]

The key decision is **how long to build playfield-X while only two balls remain before cashing Jackpot/Super Jackpot**.

## Core rules and persistence

* F-I-L-M progress is cumulative and must be completed again for each Multiball. K-I-S-S and P-A-I-D progress survive Multiball; **Menu-target progress resets after Multiball**. [S2]
* Multiball Search shots are Left Saucer, Snackbar, and Right Saucer. In stock L-4 the Girl is random. **Rev 5.0 tournament mode instead puts her at the second Search shot, and after a Jackpot at the third, player-specifically.** [S1][S2] ([Planetary Pinball][2])
* Finding the Girl → Snackbar **Rescue** → Snackbar **Jackpot** → required Jet Bumpers → Snackbar **Super Jackpot**. A Super immediately **doubles the base Jackpot for the rest of the game**. [S2]
* Jet Bumpers also increase base Jackpot throughout the game; this makes a late multiplied Super capable of completely swinging a match. [S2]
* Completing CREATURE in the Whirlpool raises playfield-X. Legacy normal/hard/easy settings cap it at **4× / 3× / 5×** respectively. Rev 5.0 fixes a bug that could corrupt later multiballs' multiplier behavior. [S1][S2]
* Lose one ball **before collecting Jackpot** and stock rules offer about **14 seconds** to shoot Snackbar for one Multiball Restart. No restart after a Jackpot. [S2]
* Timed single-ball modes pause during Multiball and resume afterward. Rev 5.0 specifically repairs broken Move Your Car behavior after such interruptions. [S1][S2]
* Rev 5.0 corrects Bonus X to the displayed **1×/2×/4×/6×/8×/10×** and triples the underlying bonus base to compensate. Bonus is still secondary to major Multiball scoring. [S1]

## Skill shots

* **P-A-I-D Skill Shot:** plunge into the flashing top rollover. It instantly completes P-A-I-D, advances Bonus X and awards the **L** in F-I-L-M. Flippers lane-change the lit rollover in both directions. [S2]
* **K-I-S-S Skill Shot:** plunge completely around the Back Orbit, timing the cycling K-I-S-S lamps. Before F is collected—and provided the preceding Multiball did not score a Jackpot—it can spot multiple or all four letters. Later attempts normally spot one. Completing K-I-S-S gives **F**. [S2]
* **Double Film Letter Combo:** after a K-I-S-S skill shot completes F, immediately shooting the Right Saucer/Slide for M adds a **4M** combo. Useful, but secondary to getting two F-I-L-M letters quickly. [S2]

## Secondary features

* **Free Pass:** timed start-of-ball save; an outlane/drain while lit returns the ball to the shooter lane. It does **not** operate during Multiball and is commonly disabled in hard tournament setups. [S2][S3]
* **Video Mode:** normally qualified at 8 Right Ramps and started at whichever saucer is lit; flipper buttons punch the Peeping Tom. Base completion scoring is meaningful but far below a multiplied Multiball Super. [S2]
* **Extra Balls:** notably available from repeated K-I-S-S and other features. No universal built-in tournament point conversion was verified; event/operator policy matters. [S2]
* **Snackbar / Playground randomness:** stock L-4 contains randomness. On Rev 5.0 tournament play, Playground follows a fixed player-specific sequence, and Snackbar awards follow a defined pattern rather than arbitrary feature awards. [S1]
* No Action Button or Magna-Save. Flippers do control the P-A-I-D lanes and can hurry the bonus countdown. [S2]

## What to watch

* **F-I-L-M inserts:** instantly show how close the player is to Multiball and which qualification shot they are hunting. [S2]
* **Heavy strobes at the saucers:** F-I-L-M is complete; a saucer lock will start the movie/Multiball. [S2]
* **Creature Ramp / Whirlpool activity during Multiball:** the player is deliberately building playfield-X before taking Jackpot. [S2]
* **Snackbar marquee:** Search → Rescue → Jackpot → Super Jackpot / Restart tells you exactly where Multiball stands. [S2]

## Important shots

| Shot                   | Position     | Advances                                       | Why now?                                  | Risk                                               |
| ---------------------- | ------------ | ---------------------------------------------- | ----------------------------------------- | -------------------------------------------------- |
| K-I-S-S / Left Saucer  | Far left     | F; Multiball start/search                      | Repeatable F progress; possible lock      | Tight lane; bad misses approach left outlane       |
| Left / Creature Ramp   | Left-center  | PF multiplier in Multiball; Unlimited Millions | Build 2×–4× before Jackpot                | Steep; rejects often require emergency save        |
| Center / Move Your Car | Center       | P-A-I-D/pops; Move Your Car                    | Safe-ish repeat scoring and Super-JP pops | Misses near Snackbar/ramp can rebound centrally    |
| Snackbar               | Center-right | I; Search, Rescue, JP, SJP, Restart            | Main Multiball cash-out                   | Missed scoop is one of the game's nastier rebounds |
| Right Ramp             | Right-center | Snack Attack, Video, Super Scoring             | Feature route / controllable transfer     | Fast left-flipper return changes timing            |
| Slide / Right Saucer   | Far right    | M; Slide modes; Multiball/search               | Easy FILM letter or valuable mode         | Saucer-lane feed can threaten the right side       |

[S2][S3]

## Match strategy

**Playing ahead:**
Favor F-I-L-M progress, controllable Center Shots, and a conservative Multiball. Once a reasonable playfield-X is established, take the Jackpot rather than risk losing the second ball while greedily circling the Whirlpool. **Strategic inference** from the risk/value structure. [S2]

**Playing behind:**
Push multiplier harder, build the base Jackpot with pops, and pursue **multiplied Super Jackpots**. A 4× Super on a well-developed Jackpot can be worth hundreds of millions or more. Unlimited Millions is another high-variance route for a player confidently looping the Left Ramp. [S2][S3]

**Key recurring decision:**
During Multiball: **cash Jackpot now, or keep one ball controlled and use the other on the Creature Ramp for another playfield-X?** Strong players may deliberately delay Jackpot because its value multiplies; losing the second ball first can throw away the opportunity.

## Danger zones

* **Left Ramp reject:** steep entrance; weak shots can return sharply toward the center. [S2]
* **Snackbar miss:** central, relatively unforgiving shot; misses frequently demand an immediate save. [S2]
* **Menu targets:** direct standup work is the least-controlled way to obtain I; the rulesheet specifically recommends using Snackbar spotting when available. [S2]
* **Outlane/inlane divider:** factory games have bare metal divider posts rather than rubber, so balls wandering toward the sides are difficult to rescue. [S2]
* **Right Ramp return:** feeds the left flipper at high speed, making repeated ramp timing noticeably different from the first shot. [S2]

## Spoken commentary cues

* “They only need the **I in F-I-L-M** now, so all of this is about getting that Snackbar open.”
* “Multiball is running, but they’re **not taking the Jackpot yet—they’re building playfield multiplier in the Whirlpool**.”
* “That’s the Rescue; one more Snackbar shot is the Jackpot.”
* “Now they need the pops. Once the bumper requirement is met, Snackbar becomes **Super Jackpot for twice the base value**.”
* “They’ve lost the second ball before Jackpot, so the Snackbar is lit briefly for the **Multiball Restart**.”
* “That Center Shot has started **Move Your Car**—four clean repeats can turn this into an 80-million-point mode.”

## Trivia

* The playfield's signature Creature is a **backlit hologram**, one of pinball's most distinctive early-1990s visual mechanisms. [S4]
* The game is themed not simply around the monster film, but around **watching it at a 1950s drive-in theater**. [S4]
* Five period songs rotate in the game, including **“Rock Around the Clock,” “Get a Job,” and “Summertime Blues.”** [S2]
* Completing P-A-I-D hides a small **Williams cow** in the DMD animation. [S2]
* Rev 5.0 finally gave the previously decorative **10M/20M/30M left-inlane lamps** a scoring purpose during Big Millions. [S1] ([Planetary Pinball][2])

## Questions for the humans

### Edition and configuration checks

1. **Which gameplay ROM should the finished binder page target?** This materially changes competition behavior.
   A. **Revision 5.0 (2020)** — current licensed update; recommended baseline.
   B. **Factory L-4** — common original software.
   C. Both, with a short L-4 vs Rev-5 callout.

### Uncertainties and conflicts

1. **Playfield multiplier maximum is adjustment-sensitive.** The legacy rules document 4× normal, 3× hard, 5× easy; Rev 5.0 fixes multiplier bugs but does not state that these maxima changed. [S1][S2]
   A. Print “up to 4× normally; operator-adjustable.”
   B. Omit the explicit maximum from the quick sheet.

2. **Multiball Restart is documented in stock rules but can be disabled in tournament configurations.** [S2][S3]
   A. Show it as “possible if enabled.”
   B. Omit unless the event confirms it is active.

## Human resolutions

1. **Which gameplay ROM should the finished binder page target?** This materially changes competition behavior.
   A. **Revision 5.0 (2020)** — current licensed update; recommended baseline.
   B. **Factory L-4** — common original software.
   C. Both, with a short L-4 vs Rev-5 callout.
   **Human answer:** C. Both, with a short L-4 vs Rev-5 callout.

1. **Playfield multiplier maximum is adjustment-sensitive.** The legacy rules document 4× normal, 3× hard, 5× easy; Rev 5.0 fixes multiplier bugs but does not state that these maxima changed. [S1][S2]
   A. Print “up to 4× normally; operator-adjustable.”
   B. Omit the explicit maximum from the quick sheet.
   **Human answer:** B. Omit the explicit maximum from the quick sheet.

2. **Multiball Restart is documented in stock rules but can be disabled in tournament configurations.** [S2][S3]
   A. Show it as “possible if enabled.”
   B. Omit unless the event confirms it is active.
   **Human answer:** A. Show it as “possible if enabled.”

## Sources

* **[S1] — Game Code Update: REV5 Creature Black Lagoon** — Planetary Pinball Supply / Søren Worre. Direct authorized ROM documentation; Revision 5.0 identity/date, tournament patterns, bug fixes, bonus correction, new inlane feature.
  [https://www.planetarypinball.com/pinball-CFTBL-REV5](https://www.planetarypinball.com/pinball-CFTBL-REV5) ([Planetary Pinball][2])
* **[S2] — Sigma’s Guide to Creature from the Black Lagoon in 3-D** — Kevin Martin, Pinball Archive. Detailed community rulesheet; F-I-L-M, skill shots, Multiball sequence, multiplier, Jackpots/Supers, modes, persistence and physical feeds.
  [https://www.pinball.org/rules/creaturefromtheblacklagoon.html](https://www.pinball.org/rules/creaturefromtheblacklagoon.html) ([Pinball.org][3])
* **[S3] — PAPA 4 Strategy Guide: Creature from the Black Lagoon** — Bowen Kerins, Pinball Archive. Expert tournament strategy; Multiball priority, PF-X technique, Move Your Car, ramp/Slide alternatives, tournament settings and control.
  [https://www.pinball.org/rules/creaturefromtheblacklagoon-notes.txt](https://www.pinball.org/rules/creaturefromtheblacklagoon-notes.txt)
* **[S4] — Creature from the Black Lagoon Game Archive** — Kineticist / Pinside. Secondary identity source; WPC generation, production, credits, hologram.
  [https://www.kineticist.com/games/pinball/creature-from-the-black-lagoon](https://www.kineticist.com/games/pinball/creature-from-the-black-lagoon) ([Kineticist][1])
* **[S5] — Creature from the Black Lagoon Strategy** — JLP Pinball Cards. Modern tournament quick-reference; confirms Move Your Car as a practical repeatable tournament route and summarizes F-I-L-M strategy.
  [https://pinballcards.net/creature-from-the-black-lagoon-1992/](https://pinballcards.net/creature-from-the-black-lagoon-1992/) ([JLP's Pinball Cards][4])

[1]: https://www.kineticist.com/games/pinball/creature-from-the-black-lagoon?utm_source=chatgpt.com "Creature from the Black Lagoon Pinball Machine (1992) by Bally Manufacturing Co."
[2]: https://www.planetarypinball.com/pinball-CFTBL-REV5 "Planetary Pinball Game Code Update - REV5 Creature Black Lagoon"
[3]: https://www.pinball.org/rules/creaturefromtheblacklagoon.html "www.pinball.org"
[4]: https://pinballcards.net/creature-from-the-black-lagoon-1992/?utm_source=chatgpt.com "Creature from the Black Lagoon"
