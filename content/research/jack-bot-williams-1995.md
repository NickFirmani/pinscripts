## Identity and versions

* **Jack•Bot**, Williams, **1995**, Williams **WPC-Security** DMD platform. Design by **Barry Oursler and Larry DeMar**; software by **Larry DeMar and Louis Koziarz**; major art credits include **John Youssi, Doug Watson, Greg Freres and Paul Barker**; music/sound by **Jon Hey**. Production: **2,428**. [S1][S2] ([Pinside][1])
* **Rules basis: `rom` — factory game ROM 1.0R**, U6 checksum `1D10`, released **1995-08-07**. Prototype/sample 0.4 lacks several finished rules including Super Jack•Bot and production Tournament Mode behavior. [S1] ([Pinside][2])
* A later **1.01R “LED Ghost Fix”** exists in emulation archives, but it is a display/LED compatibility patch rather than a documented gameplay revision; use **1.0R** as the factory rules basis. [S1] ([VPForums][3])
* Two central scoring systems: **Multiball → Jack•Bots/Super Jack•Bots/Mega Visor**, and the four casino games → **Casino Run**. [S2][S3] ([GameFAQs][4])

Research scope follows the supplied commentator-reference specification. 

## Thirty-second game plan

1. **Observed strategy:** at game start, exploit the flashing Keno row/column to open the visor with **one accurate target hit**—the leftmost/yellow column is a commonly preferred safe attempt. If missed, opening the visor becomes much more work. [S3][S5] ([JLP's Pinball Cards][5])
2. Lock two balls in the Eyes and play **Multiball under control**. Jack•Bots begin at **50M** and climb; hitting one Eye for a Jack•Bot then the other Eye immediately scores a **3× Super Jack•Bot**. [S2][S3] ([GameFAQs][6])
3. In parallel, play all four **Casino Games** at the Game Saucer. Use **Double or Nothing** aggressively when the Cashier shot is comfortable; starting Multiball during its timer also collects the double. [S2][S6] ([GameFAQs][4])
4. After all four games, **Casino Run** starts at 100M and adds 4M per switch. Every spin risks a bomb that can erase the bank: behind, press your luck; ahead, cash sooner. [S2] ([GameFAQs][4])
5. **Alternate:** once the easy first visor opening is gone, especially after repeated Multiballs, casino games/Casino Run often become the lower-effort route while incidental target hits rebuild the visor. [S5][S6] ([Tilt Forums][7])

## Core rules and persistence

The first Multiball requires completing the Keno grid/opening the visor and locking two balls in the Eyes. The **first MB is 2-ball**; later ones are normally 3-ball. Physical balls in the Eyes are globally shared, but **lock credit is player-specific**: another player can consume the physical ball while your software lock remains credited. [S2] ([GameFAQs][6])

Four locations score Jack•Bots: both Eyes, **Cashier**, and **Hit Me**. The Game Saucer relights them. Jack•Bot value starts at **50M**, advances by 25M through 300M, then climbs faster to **500M**. An Eye Jack•Bot followed immediately by the opposite Eye scores **3× current value** as a Super. [S2] ([GameFAQs][6])

Fifteen Jack•Bots during MB enter **Mega Visor**: the visor closes and target hits rebuild the full Keno grid at 50M per light before the next giant cash-out sequence. [S2] ([GameFAQs][6])

The four Casino Games—**Poker, Slot Machine, Roll the Dice, Keno**—can be selected with the left flipper before shooting the Game Saucer. Many resulting awards can be risked via **Double or Nothing**: right flipper chooses the gamble, then Cashier must be hit before time expires; failure earns zero. [S2] ([GameFAQs][4])

**Casino Run:** 45-second single-ball mode; bank starts at **100M + 4M per switch**. Eyes or Game Saucer spin three reels. Bomb or timeout loses the bank; the player can instead collect and end the mode. A drain relaunches the ball but normally costs 5 seconds. [S2] ([GameFAQs][4])

## Skill shots

**Vortex Skill Shot:** plunge into the three-hole Vortex. The outer holes begin at 10M; the **middle hole is 3×**, permanently adds **+5M to future base skill-shot value**, and advances Bonus X. Vortex value can be developed to 50M; ordinary temporary value normally resets between balls unless Hold Vortex is awarded. [S2] ([GameFAQs][4])

During later Multiballs, a served plunger ball can convert the Vortex skill shot into a **Jack•Bot**, making plunge accuracy materially important. [S2]

During **Casino Run relaunches**, a successful skill shot with ≥10 seconds remaining adds **10 seconds**; with 9 seconds or less it instead **collects the bank and ends the Run**. [S2] ([GameFAQs][4])

**Observed advanced alternative:** tournament players may deliberately short-plunge so the game has not yet validated a plunge; this can permit safer initial visor work before three distinct switches register. This is an exploitation of switch validation, **not a formal second skill shot**. [S3] ([JLP's Pinball Cards][5])

## Secondary features

* **Cheat button:** repeatedly press the flashing Extra Ball/Buy-In button during eligible casino awards. On normal settings success is random; **Tournament Mode makes the cheat succeed every fourth eligible opportunity**. Slot Machine is not cheat-eligible in Tournament Mode. [S4] ([Tilt Forums][7])
* **Casino Run is different:** its bomb/randomness is **not normalized by Tournament Mode**. Competitive expert Keith Johnson (“Keefer”) specifically documents it as independent random behavior. [S4] ([Tilt Forums][7])
* **Ball save:** contemporary rules document roughly six seconds on a normal plunge; adjustment-sensitive. [S2] ([GameFAQs][4])
* **Extra balls:** numerous features can light EB at the movable inlane/outlane lamps. When EBs are disabled, competitive documentation confirms **Light Extra Ball becomes 200M**; Special point value is more configuration-sensitive. [S3][S7] ([JLP's Pinball Cards][8])
* **Bonus:** cards + current Vortex base + Dice wager, multiplied by Bonus X (normally up to 5×; a successful bonus cheat can reach 6×). This can become a substantial secondary score. [S2] ([GameFAQs][4])
* **Video mode:** None found.

## What to watch

1. **Keno grid flashing by rows/columns:** the easy one-shot visor opening is still alive. Once ordinary progress is made, expect a much longer qualification. [S3]
2. **Visor open / balls in Eyes:** Multiball is being staged; two software locks starts it. [S2]
3. **Game Saucer lit:** player is pursuing one of four casino games; after the fourth it becomes **Casino Run**. [S2]
4. **Casino Run bank + No Bomb:** a No Bomb removes much of the immediate risk; without one, a large bank creates the game’s signature collect-versus-gamble decision. [S2][S6]

## Important shots

| Shot                 | Position           | Advances                                        | Why now?                                              | Risk                                                       |
| -------------------- | ------------------ | ----------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| **Visor targets**    | Upper center       | Keno grid / visor opening                       | Fastest route to MB, especially flashing opening shot | Direct standups can return center                          |
| **Left / Right Eye** | Behind visor       | Locks, Jack•Bots, Casino spins                  | Locks MB; paired Eyes produce Super Jack•Bot          | Eject requires immediate control; machine-sensitive        |
| **Game Saucer**      | Upper-left-center  | Casino games, jackpot relight, Casino Run spins | Main casino progression                               | Narrow shot; kickout gives up control                      |
| **Cashier**          | Under left ramp    | Double or Nothing, Jack•Bot, bonus cash-outs    | Converts casino awards to 2×                          | Exposed standup; miss means losing Double-or-Nothing award |
| **Left ramp**        | Far left           | Relights Game Saucer; Vortex/return utilities   | Keeps casino progression moving                       | Feed can go bumps, plunger or return lane unpredictably    |
| **Hit Me**           | Lower-right/center | Blackjack; Jack•Bot during MB                   | Fourth jackpot location when lit                      | Awkward direct touch-target shot                           |

[S2][S3][S6] ([GameFAQs][4])

## Match strategy

**Playing ahead:** favor the controlled Multiball route, take available Supers, and **cash Casino Run earlier** once a meaningful bank is established rather than exposing a lead to random bombs. **Strategic inference:** small Double-or-Nothing awards become less attractive when protecting position.

**Playing behind:** lean into volatility: Double-or-Nothing valuable casino awards, press Casino Run toward a much larger bank, and chase repeated Eye-to-Eye Supers or Mega Visor. [S2][S6]

**Key recurring decision:** **deterministic Multiball execution or casino variance?** The answer often changes after the easy first visor-open opportunity is gone. [S3][S5]

## Danger zones

* **Visor targets:** central standups; the exact shots needed for MB can rebound immediately toward the drain.
* **Cashier:** Double or Nothing converts a normally ordinary target miss into **losing the entire casino-game award**. [S2]
* **Game Saucer kickout:** controllable on well-set-up machines, but tournament strategy explicitly emphasizes settling its eject before attacking Cashier. [S6] ([Digital Pinball Fans][9])
* **Eye ejects:** useful for trapping during Casino Run, but feeds vary between copies; strong players exploit predictable catches when available. [S6]
* **Casino Run clock:** a drain is not the end, but the **5-second penalty** can turn the next plunge into a forced collect or complete loss. [S2]

## Spoken commentary cues

* “The grid is still flashing—they can open the visor with one target instead of filling all twenty-five.”
* “They want left Eye then right Eye—that quick second Eye is the three-times Super Jack•Bot.”
* “That’s the fourth casino game, so Casino Run is now ready.”
* “They’ve chosen Double or Nothing: Cashier is now worth twice the award, and a miss gets zero.”
* “Tournament cheat is deterministic—every fourth *eligible* cheat works—but Casino Run itself stays random.”
* “They’ve got a huge Casino Run bank; now the question is whether to take it or spin into a possible bomb.”

## Trivia

* Jack•Bot is the **third Pin•Bot game**, after *Pin•Bot* (1986) and *The Machine: Bride of Pin•Bot* (1991). [S1] ([Pinside][1])
* Its physical playfield is essentially the **1986 Pin•Bot layout reused with radically deeper software**. [S2] ([GameFAQs][4])
* The Extra Ball button’s “cheating” is **intentional documented gameplay**, not a secret exploit. [S1][S4] ([Pinside][2])
* Holding both flippers during Casino Run can reveal a **Mortal Kombat 3 hint**, itself worth an Extra Ball. [S2] ([GameFAQs][4])
* The game includes a memorial for Williams mechanical designer **Joe Joos Jr.**, whose credits include many famous pinball toys. [S1] ([Arcade History][10])

## Questions for the humans

### Edition and configuration checks

1. Which cheat environment should the final page assume?
   A. **Tournament Mode — every fourth eligible cheat succeeds**
   B. Normal/random cheating
   C. Cheating disabled entirely

2. How are Extra Balls handled?
   A. **Disabled / Light EB becomes 200M**
   B. Extra Balls remain playable
   C. Venue-specific tournament conversion

### Uncertainties and conflicts

1. **Special conversion:** modern tournament cards state **500M** when converted [S3], while the Williams-era documentation and later investigation show Special-to-points can be configured differently, including much lower values. [S2][S7] Do not print “Special = 500M” without verifying the tournament setup. ([JLP's Pinball Cards][8])

2. **LED-fix ROM 1.01R:** emulation archives contain this patch, but factory software records identify **1.0R** as the final production rules release. No gameplay difference has been documented. [S1]

## Human resolutions

1. Which cheat environment should the final page assume?
   A. **Tournament Mode — every fourth eligible cheat succeeds**
   B. Normal/random cheating
   C. Cheating disabled entirely
   **Human answer:** A. **Tournament Mode — every fourth eligible cheat succeeds**

2. How are Extra Balls handled?
   A. **Disabled / Light EB becomes 200M**
   B. Extra Balls remain playable
   C. Venue-specific tournament conversion
   **Human answer:** A. **Disabled / Light EB becomes 200M**

1. **Special conversion:** modern tournament cards state **500M** when converted [S3], while the Williams-era documentation and later investigation show Special-to-points can be configured differently, including much lower values. [S2][S7] Do not print “Special = 500M” without verifying the tournament setup. ([JLP's Pinball Cards][8])
   **Human answer:** special = 500m

2. **LED-fix ROM 1.01R:** emulation archives contain this patch, but factory software records identify **1.0R** as the final production rules release. No gameplay difference has been documented. [S1]
   **Human answer:** ok

## Sources

* **[S1] — Jack•Bot game archive / software history — Pinside + Arcade-History.** Identity, WPC-S platform, credits, production count, factory **ROM 1.0R / 1995-08-07**, production-code changes. [Pinside Jack•Bot archive](https://pinside.com/pinball/machine/jack-bot/details?utm_source=chatgpt.com) · [Arcade-History Jack•Bot entry](https://www.arcade-history.com/game/5341/jackbot?utm_source=chatgpt.com)
* **[S2] — Jack•Bot Rulesheet — Mark Phaedrus / GameFAQs, 1995.** Detailed contemporary rules: Multiball, jackpots, skill shot, casino games, Casino Run, bonus, EBs and persistence. [Contemporary Jack•Bot rulesheet](https://gamefaqs.gamespot.com/pinball/916482-jackbot/faqs/1397?utm_source=chatgpt.com)
* **[S3] — Jack•Bot Strategy Card — JLP Pinball Cards, updated 2026-07-21.** Current tournament route: instant visor opening, controlled MB, Super technique, short-plunge exploit and EB conversion. [Current Jack•Bot strategy card](https://pinballcards.net/jackbot-1995/?utm_source=chatgpt.com)
* **[S4] — Jack•Bot Tournament Cheat Rules — Keith Johnson / Tilt Forums.** Authoritative competitive explanation of deterministic Tournament Mode cheats and Casino Run’s separate randomness. [Tournament cheat discussion](https://tiltforums.com/t/whats-your-favorite-game-to-play-in-a-tournament/232/?utm_source=chatgpt.com)
* **[S5] — Competitive Jack•Bot discussion — Tilt Forums.** Tournament evidence that missing the easy visor opening materially shifts strategy toward Casino Run. [Competitive Jack•Bot discussion](https://tiltforums.com/t/whats-your-favorite-game-to-play-in-a-tournament/232/?utm_source=chatgpt.com)
* **[S6] — Jack•Bot Tactics and Strategies — Digital Pinball Fans.** Observed high-level Casino Run, Double-or-Nothing, eye-eject and Cashier strategy. [Jack•Bot tactics discussion](https://digitalpinballfans.com/threads/jack%E2%97%8Fbot-tactics-and-strategies.10084/?utm_source=chatgpt.com)
* **[S7] — Points for Extra Ball Wiki — Tilt Forums.** Competitive verification of Jack•Bot’s **200M Light-EB conversion** and discussion of Special conversion sensitivity. [Extra-ball conversion reference](https://tiltforums.com/t/points-for-extra-ball-wiki/2725/?utm_source=chatgpt.com)

[1]: https://pinside.com/pinball/machine/jack-bot?utm_source=chatgpt.com "Jack*Bot Pinball Machine (Williams, 1995) | Pinside Game Archive"
[2]: https://pinside.com/pinball/machine/jack-bot/details?utm_source=chatgpt.com "Jack*Bot Pinball Machine (Williams, 1995) | Pinside Game Archive"
[3]: https://www.vpforums.org/index.php?showtopic=11322&utm_source=chatgpt.com "pinMAME 2.3 and missing ROMs - VPinMAME - VPForums.org"
[4]: https://gamefaqs.gamespot.com/pinball/916482-jackbot/faqs/1397 "Jack*Bot - Rule Sheet - Pinball - By MPhaedrus - GameFAQs"
[5]: https://pinballcards.net/jackbot-1995/ "Jack*Bot"
[6]: https://gamefaqs.gamespot.com/pinball/916482-jackbot/faqs/1397?utm_source=chatgpt.com "Jack*Bot - Rule Sheet - Pinball - By MPhaedrus - GameFAQs"
[7]: https://tiltforums.com/t/whats-your-favorite-game-to-play-in-a-tournament/232/8?u=heyrocker "What’s your favorite game to play in a tournament? - Tilt Forums"
[8]: https://pinballcards.net/jackbot-1995/?utm_source=chatgpt.com "Jack*Bot"
[9]: https://digitalpinballfans.com/threads/jack%E2%97%8Fbot-tactics-and-strategies.10084/?utm_source=chatgpt.com "Jack●Bot Tactics and Strategies | Digital Pinball Fans"
[10]: https://www.arcade-history.com/game/5341/jackbot?utm_source=chatgpt.com "Jack*Bot (1995) - Pinball by Williams Electronics Games, Inc."
