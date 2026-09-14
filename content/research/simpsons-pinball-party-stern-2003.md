## Identity and versions

**The Simpsons Pinball Party** — Stern Pinball, 2003. Design is credited to **Keith P. Johnson and Joe Balcer**; software to Johnson and Dwight Sullivan. It is a Whitestar-era game with five flippers and a substantial upper mini-playfield. [S5][S6]

* **Rules basis: `rom` — CPU ROM 5.00 (`spp-cpu.500`), released 2007-07-02.** It requires Display ROM 5.00 or higher. [S1]
* ROM 5.00 mostly fixes bugs and Competition Mode behavior; the detailed Bowen Kerins rulesheet is written for ROM 3.00, so later ROM notes take precedence where they conflict. [S1][S2]
* Tournament-relevant multiballs/features include **Couch Multiball**, four **Itchy & Scratchy Multiballs**, **Pretzel Multiball**, **Scratchy's Revenge**, plus late-game **Springfield Mystery Spot** and **Alien Invasion**. [S2]

## Thirty-second game plan

1. **Build the shared timer stack.** Light TV at the **Krusty/right orbit**, reach the upper playfield through the **Garage**, and shoot the TV loop to start modes. Starting another timed feature resets the same timer and keeps everything already running alive. [S2][S3]
2. **Add Otto 2x scoring.** Light Otto, then shoot the Springfield Elementary/right inner loop. The selected shot scores 2x—including mode and multiball awards—while the common timer survives. [S2][S3]
3. **Stack, don't isolate.** Build three Couch locks and bring Couch or Itchy & Scratchy Multiball into the running TV/Otto stack; documented expert strategy often values starting more features over chasing modest standalone jackpots. **Observed strategy.** [S2][S4]
4. **Recognize Victory Laps as the huge cash-out.** Completing TV modes while preserving the same timer increases every major-shot Victory value, topping out at **2.5M per shot after all seven; 5M on a doubled shot**. At high values, stop adding TV modes and farm the easy shot. [S2][S4]
5. Alternate high-variance route: set up **Springfield Mystery Spot + another multiball/major mode**, because Mystery Spot doubles the whole playfield and is far stronger as a stack ingredient than by itself. **Observed strategy.** [S2][S4]

## Core rules and persistence

**Confirmed rule:** virtually all ordinary timed features share **one timer**. Starting a qualifying TV mode, Otto 2x, D'Oh Frenzy, or timed Treehouse mode resets it to at least 30 seconds. Existing timed features continue. The TV display shows green above 15 seconds, yellow at 6–15, and red at 5 or less; the Pop Target can add time. [S2]

TV modes are lit at the **Krusty/right orbit** and started at the upper TV loop. The right flipper selects the next mode. Completing a mode does **not** stop the shared timer; with no active TV mode, Victory scoring begins. Starting another TV mode suspends Victory scoring until that mode is completed. [S2][S4]

Otto's Bus Tour provides ten shot-area **2x multipliers**. A flashing red 2x insert means active; solid means that area's multiplier has been used this cycle. The multiplier doubles essentially all scoring attached to that area, including TV modes and multiballs. [S2]

Couch Multiball requires three upper-playfield Couch locks. In ordinary multiplayer, the **Hold Couch Locks** adjustment can allow physical balls/locks to be inherited or stolen. In **Competition Mode it is treated as Never**: balls may remain physically in the Couch, but every player must earn three locks personally. This is easy to miscall from video. [S1][S2]

**Competition Mode** also makes Otto sequence, Hurry-Ups, Treehouse awards and many Mystery outcomes deterministic rather than random. [S1]

End-of-ball bonus can become match-sized through bonus multipliers and accumulated values. Bowen specifically cautions against tilting away very large bonuses; treat the magnitude as **observed strategy**, not a fixed award. [S2]

## Skill shots

* **Comic Book Guy Skill Shot** — plunge directly into Comic Book Guy. It immediately starts **two Hurry-Ups** instead of one. Modern competitive guidance calls this the best general-purpose skill shot because it creates immediate scoring/progression. [S2][S3]
* **Kwik-E-Mart Skill Shot** — plunge through the Kwik-E-Mart mini-loop. It adds a large, increasing **bonus multiplier**; the ROM-3 rulesheet reports 5x through 10x on successive makes. Particularly attractive when protecting a potentially large end-of-ball bonus. [S2]
* **Bully Skill Shot** — plunge through Kwik-E-Mart into the strobing Bully target. Scores increasing points and immediately lights the next **Daredevil Mode**. [S2]

All three use the manual plunge; the lit/strobing target state gives the commentator the clearest intent cue. [S2]

## Secondary features

* **Ball save:** the standard Stern **Freeze Time** start-of-ball saver is operator-adjustable from OFF through 1–15 seconds or AUTO; the documented U.S. default is OFF. Couch Multiball and major multiballs/modes can have their own saves. [S7][S2]
* **Mystery / Clean the Garage:** enter the Garage when lit. Normal play can be random; Competition Mode substitutes deterministic, state-aware awards—for example lighting TV/Otto or adding time when useful. This makes Mystery strategically much stronger and more predictable in competition. [S1][S4]
* **Extra balls:** numerous features can light one. Whether these remain actual balls or become points is tournament/operator policy; no universal v5 conversion value was verified here, so commentary should use the venue note rather than assume one.
* **Player controls:** the **right flipper** selects the upcoming TV mode and some other selectable features. During **Springfield Mystery Spot, the left and right flipper buttons are intentionally reversed.** [S2]
* No separate conventional video mode materially relevant to tournament strategy was found.

## What to watch

1. **TV-board timer color:** green → yellow → red immediately shows whether the player needs a timer reset rather than raw scoring. [S2]
2. **Flashing red 2x insert:** that area is currently doubled; solid red means its Otto multiplier has expired for this cycle. [S2]
3. **TV lit + ball on upper playfield:** expect the player to prioritize the TV loop to start/reset a mode rather than shoot Couch automatically. [S2]
4. **Balls visibly in the Couch:** under Competition Mode this does **not** prove the current player owns those locks. Watch their lock progress/callout. [S1]

## Important shots

| Shot                                   | Position           | Advances                            | Why now?                                         | Risk                                                                                     |
| -------------------------------------- | ------------------ | ----------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **Garage**                             | Center-left        | Upper playfield; Mystery            | Gateway to TV/Couch progression                  | Weak shots fall into the pops and may not register the Garage. [S2][S6]                  |
| **Krusty / Right Orbit**               | Far right          | Lights TV                           | Keeps another timer reset available              | Spinner/orbit sends ball into upper/pops area rather than giving immediate control. [S2] |
| **Springfield Elementary / Otto Loop** | Inner right-center | Starts shot-specific 2x             | Preserve timer and multiply a lucrative shot     | Straight-up-the-middle shot; a reject is inherently consequential. [S2]                  |
| **TV Loop**                            | Upper playfield    | Starts selected TV mode             | Adds to stack/reset timer                        | Miss loses a valuable upper-playfield opportunity. [S2]                                  |
| **Couch Ramp**                         | Upper playfield    | Locks / Couch MB / super            | Build or cash the game's central multiball       | Requires precise upper-flipper timing; expert guidance emphasizes mastering it. [S2]     |
| **Itchy & Scratchy hole**              | Right side         | I&S multiballs / Scratchy's Revenge | Add balls to a stack or reach major late scoring | Drop-bank/hole access can be difficult under pressure. [S2][S4]                          |

## Match strategy

**Playing ahead:**
**Strategic inference:** preserve control, take available Couch/TV scoring, and cash strong Victory Laps rather than interrupting them to build an even larger stack. Avoid forcing the notoriously difficult left ramp merely for speculative future value.

**Playing behind:**
**Observed strategy:** extend the shared timer, accumulate TV modes and favorable Otto 2x shots, then combine multiple multiballs—especially **Scratchy's Revenge or another feature with Springfield Mystery Spot**. Bowen documents coordinated stacks exceeding 200M; treat that as observed upside rather than a guaranteed value. [S2][S4]

**Key recurring decision:**
**Start another feature or harvest the one already built.** Early, adding modes usually strengthens the stack and resets the clock; once Victory Laps become 500K–2.5M each, continuing to shoot a safe doubled ramp can be better than starting another TV mode and temporarily shutting Victory scoring off. [S4]

## Danger zones

* **Garage under-hit:** drops into the pop-bumper area without completing the intended Garage shot. [S2][S6]
* **Left Treehouse Ramp:** repeatedly identified as the game's hardest major shot; rejects are especially costly when a mode requires it. [S6][S4]
* **Springfield Elementary reject:** the useful Otto loop is essentially straight up the middle. **Strategic inference:** misses can rapidly turn a timer-saving attempt into drain danger. [S2]
* **Upper-playfield miss:** a failed Couch/TV opportunity often ejects the ball from the mini-playfield and forfeits the controlled setup the player worked to reach.
* **Tilt with built bonus:** TSPP can carry a very substantial end-of-ball bonus, so an aggressive save can lose more than the visible current feature value. **Observed strategy.** [S2]

## Spoken commentary cues

* “TV is lit—Garage to the upper playfield, then the TV loop starts the next mode.”
* “Everything is living on the same clock; starting another timed feature keeps the whole stack alive.”
* “That flashing red insert is the Otto **2x**—all scoring on that area is doubled.”
* “They've reached Victory Laps; another TV mode would suspend those laps until they finish it.”
* “Those balls in the Couch are misleading in Competition Mode—the player still has to earn all three locks.”
* “Mystery Spot reverses the flipper buttons and doubles the playfield; stack something with it and the score can explode.”

## Trivia

* The game uses a **two-level playfield**, five flippers, a moving/talking Homer head, Bart skateboard captive ball, miniature TV and physical three-ball Couch lock. [S5][S6]
* Stern recorded original dialogue from **Dan Castellaneta, Nancy Cartwright and Hank Azaria** specifically for the machine. [S5]
* Matt Groening and Bongo/Fox Studios participated in the artwork. [S5]
* Keith Johnson explicitly described the intent as giving expert players an unusually large number of things to accomplish—a good description of the famously layered ruleset. [S5]
* The final CPU ROM, **5.00**, arrived more than four years after the game's 2003 release. [S1]

## Questions for the humans

### Edition and configuration checks

1. Which rules environment should the final generic commentator page emphasize?
   A. **ROM 5.00 + Competition Mode** as the tournament baseline
   B. ROM 5.00 normal/random behavior
   C. Show the important differences between both

### Uncertainties and conflicts

1. **Springfield Mystery Spot ball count conflicts.** Bowen's ROM-3-era rulesheet says **five balls** [S2], while the current Kineticist guide says **four balls** [S4]. The ROM 4.00/5.00 change logs do not document a ball-count change.
   A. Verify on ROM 5.00 hardware and print the verified count
   B. Omit the ball count from the final page

2. **Scratchy's Revenge Super qualification conflicts.** Stern's ROM 3.00 revision history explicitly says the first Super requires **15 jackpots minus I&S supers already earned that cycle, minimum five; later Supers require 15** [S1]. The modern Kineticist guide simplifies this to **ten jackpots** [S4]. Because [S1] is direct revision documentation and no later change is documented, this brief treats [S1] as authoritative.
   A. Use the ROM-note rule
   B. Omit the exact jackpot count from the final quick reference

## Human resolutions

1. Which rules environment should the final generic commentator page emphasize?
   A. **ROM 5.00 + Competition Mode** as the tournament baseline
   B. ROM 5.00 normal/random behavior
   C. Show the important differences between both
   **Human answer:** A. **ROM 5.00 + Competition Mode** as the tournament baseline

1. **Springfield Mystery Spot ball count conflicts.** Bowen's ROM-3-era rulesheet says **five balls** [S2], while the current Kineticist guide says **four balls** [S4]. The ROM 4.00/5.00 change logs do not document a ball-count change.
   A. Verify on ROM 5.00 hardware and print the verified count
   B. Omit the ball count from the final page
   **Human answer:** A. Verify on ROM 5.00 hardware and print the verified count

2. **Scratchy's Revenge Super qualification conflicts.** Stern's ROM 3.00 revision history explicitly says the first Super requires **15 jackpots minus I&S supers already earned that cycle, minimum five; later Supers require 15** [S1]. The modern Kineticist guide simplifies this to **ten jackpots** [S4]. Because [S1] is direct revision documentation and no later change is documented, this brief treats [S1] as authoritative.
   A. Use the ROM-note rule
   B. Omit the exact jackpot count from the final quick reference
   **Human answer:** doesnt really matter...

## Sources

**[S1] — The Simpsons Pinball Party CPU ROM Revision History** — Stern Pinball; mirrored verbatim by Matt's Basement Arcade/Pinside — ROM release notes. Supports ROM 5.00/date, Competition Mode, Couch-lock treatment, Scratchy's Revenge revision, and v4/v5 changes.
[ROM 5.00 revision history mirror](https://pinside.com/pinball/shops/shop/1083-matt-s-basement-arcade/01944-the-simpsons-pinball-party-stern-rom-upgrade-chip-set?utm_source=chatgpt.com)

**[S2] — The Simpsons Pinball Party Rule Sheet** — Bowen Kerins — detailed rulesheet, explicitly based on ROM 3.00. Supports timer, TV modes, Victory scoring, Otto multipliers, skill shots, locks, multiballs, bonus and historical strategy.
[Bowen Kerins rulesheet](https://gamefaqs.gamespot.com/pinball/919758-the-simpsons-pinball-party/faqs/26419?utm_source=chatgpt.com)

**[S3] — Party Hard: The Simpsons Pinball Party Tutorial — Beginners Guide** — Kineticist — modern competitive tutorial. Supports basic stacking strategy, Otto use and Comic Book Guy skill-shot priority.
[Kineticist beginner tutorial](https://www.kineticist.com/news/the-simpsons-pinball-party-tutorial-beginners?utm_source=chatgpt.com)

**[S4] — The Simpsons Pinball Party Rules & Gameplay Tutorial — Advanced Guide** — Kineticist — expert strategy guide. Supports Victory-Lap strategy, Competition-Mode planning, Mystery Spot stacking and major-mode strategy.
[Kineticist advanced tutorial](https://www.kineticist.com/news/simpsons-pinball-party-tutorial-advanced?utm_source=chatgpt.com)

**[S5] — The Simpsons Pinball Party** — Stern Pinball — manufacturer game page. Supports identity, two-level hardware, Homer/Bart/Couch features, artwork participation and original voice recording.
[Official Stern game page](https://www.sternpinball.com/game/the-simpsons-pinball-party/?utm_source=chatgpt.com)

**[S6] — Simpsons Pinball Party, The** — JLP Pinball Cards — concise contemporary playfield/strategy reference. Supports Garage importance, difficult left ramp, mini-playfield route and shared-timer overview.
[Pinball Cards quick reference](https://pinballcards.net/simpsons-pinball-party-the-2003/?utm_source=chatgpt.com)

**[S7] — The Simpsons Pinball Party Owner Manual** — Stern Pinball, searchable mirror by Manualzz — manufacturer service manual. Supports Freeze Time ball-save adjustment/default and Competition Mode configuration.
[Owner manual mirror](https://manualzz.com/doc/77972105/stern-pinball-the-simpsons-pinball-party-owner-manual?utm_source=chatgpt.com)
