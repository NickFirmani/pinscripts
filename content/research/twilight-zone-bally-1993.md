## Identity and versions

* **Twilight Zone** — Bally, **1993**, model **50020**, Williams **WPC Fliptronics II** widebody. Design by **Pat Lawlor**; software by **Larry DeMar and Ted Estes**; art by **John Youssi**; mechanics by **John Krutsch**; music by **Chris Granner**. Production: **15,235**. [S3][S4]
* Major scoring multiballs are the regular **3-ball Multiball** and **3-ball Powerball Mania**; **Fast Lock** is a secondary multiball. **Lost in the Zone (LITZ)** is the six-ball timed wizard mode. [S2][S3]
* Latest verified official code family is **9.4**. **9.4H**, dated **October 22, 1998**, is the later Williams home/free-play derivative; production **L-4** dates June 14, 1993, and 9.2 dates February 28, 1995. [S1]
* Scope follows the supplied commentator-reference specification.

## Thirty-second game plan

1. **Observed strategy:** shoot both ramps to spell **GUM-BALL**. That lights both a **Lock** and the **Gumball Machine**. Repeat this progression throughout the game. [S2][S3]
2. For regular Multiball, preferably **lock two balls before starting it from the left ramp**: the opening Piano Jackpot is **40M instead of 15M**. Piano collects Jackpot; Camera relights it. [S2][S3]
3. Cash lit Gumballs at the **right orbit**. Eventually the ceramic **Powerball** comes into play; put it back into the Gumball Machine to start **Powerball Mania**. [S2]
4. In Powerball Mania, shoot the **right ramp → Powerfield** and get the ball through its upper hole for **50M Mania Jackpots**, repeatable after relighting the Powerfield with the left ramp. [S2][S3]
5. Alternate deep route: collect the **14 Door Panels** opportunistically. Completing the Door lights **Lost in the Zone**, a 45-second six-ball scoring explosion. [S2][S3]

## Core rules and persistence

* Each GUM-BALL completion lights one Lock and one Gumball. Gumballs **stack**; Locks do not—you must use the current Lock before spelling GUM-BALL again. Gumball loads score **15M, then 20M, then 25M thereafter**. [S2]
* Regular Multiball starts at the **Piano** with a **15M Jackpot after one lock or 40M after two+ locks**. Seven Greed targets add 5M each, allowing base Jackpots up to 65M/90M. Camera relights Jackpot; a Jackpot made with the Powerball can score **2×**. [S2]
* If regular Multiball ends **without a Jackpot**, the Lock lane briefly offers a one-time restart. Sources disagree between roughly 12 and 15 seconds; treat the actual machine timer as authoritative. [S2][S5]
* **Powerball Mania:** every upper Powerfield hole scores a fixed **50M Mania Jackpot**. Crucially, the Mania total—including jackpots—is stored in **end-of-ball bonus**, so a tilt can erase an enormous apparent scoring run. [S2][S3]
* Door Panels already collected remain lit until LITZ. Piano awards the currently flashing panel; Slot Machine awards another available panel. In Tournament Mode the Slot sequence is deterministic rather than random. [S2]
* **LITZ:** 45 seconds, all six balls kept alive by autofire, with Powerball Mania, clock, Greed and other scoring running simultaneously. Completing LITZ resets the Door for another trip. [S2]
* The physical Powerball is **shared machine state**, not player-specific. Its position in the trough/Gumball Machine can therefore advantage a later player; software can instead simulate the Powerball. [S2]

## Skill shots

**Normal Skill Shot**

* Soft plunge through one of three rollovers without reaching the scoop.
* **Red:** 2M + advances one bumper level.
* **Orange:** 5M + advances two.
* **Yellow:** 10M + advances all three and, on normal settings, spots the 10M Door Panel. [S2]
* **Observed strategy:** usually skip it. A successful plunge is fired from the Rocket directly toward the dangerous Town Square bumpers. [S2][S5]

**Super Skill Shot**

* Collect its Door Panel, then shoot the **left ramp**, which diverts the ball back to the manual plunger.
* All rollover/scoop results score 10M; **Red lights Battle the Power, Orange lights the outlanes, Yellow lights a temporary Extra Ball**. [S2]
* It cannot be stacked and takes precedence over starting normal Multiball from the left ramp. [S2]

## Secondary features

* **Ball save:** factory-style play normally has none. Later **9.2+** code added adjustment support for broader ball-save use; the older implementation allowed an adjustable first-ball saver. Verify the tournament setting. [S1][S2]
* **Magna-Flip / Battle the Power:** shoot the lit right ramp to the mini-playfield; flipper buttons energize its two magnets. The upper hole doubles that Battle's accumulated Powerfield value and can award a Door Panel. [S2]
* **Extra Balls:** numerous routes exist. When EBs are disabled in Tournament Mode, the Lite Extra Ball Door Panel is automatically considered complete, preventing it from blocking LITZ. [S2]
* **Camera:** eight semi-random awards. Tournament Mode parallelizes the award sequence between players; some awards can be very large, including **3× Town Square up to 75M** or **Collect Bonus**. [S2]
* No conventional video mode.

## What to watch

1. **GUM-BALL / Lock / Gumball lamps:** tells whether the player is building regular Multiball, advancing toward the Powerball, or both.
2. **Piano red versus Camera lit:** red Piano means Jackpot; Camera means the player is trying to relight it.
3. **White Powerball on the playfield + Gumball lit:** Powerball Mania is one right-orbit shot away.
4. **Door Handle flashing:** all Door Panels are complete; next valid Door collect starts **Lost in the Zone**.

## Important shots

| Shot                  | Position                       | Advances                            | Why now?                                                      | Risk                                          |
| --------------------- | ------------------------------ | ----------------------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| Left ramp             | Left-center                    | GUM; Piano relight; Multiball start | Foundation shot; starts MB with controlled upper-flipper feed | Reject returns toward center                  |
| Right ramp            | Right-center                   | BALL; Powerfield                    | GUM-BALL and Mania Jackpot access                             | Steep reject / upper-feed chaos               |
| Lock lane             | Upper-right                    | Physical locks; MB restart; EB      | Needed for 40M-start Multiball                                | Narrow shot can bounce straight toward center |
| Piano                 | Upper-right-flipper cross-shot | Door Panels; Multiball Jackpot      | Primary MB cash-out                                           | Requires accurate upper-flipper shot          |
| Camera                | Under upper-left flipper       | Jackpot relight; Camera awards      | Necessary for repeated MB Jackpots                            | Awkward horizontal upper-flipper shot         |
| Gumball / right orbit | Far right                      | Gumballs; Powerball Mania           | Turns ramp work into 15–25M and eventually PB Mania           | Powerball is fast and ignores helper magnets  |

## Match strategy

**Playing ahead:** prioritize **two-lock regular Multiball**, clean Piano Jackpots and stacked 25M Gumballs. Avoid unnecessary bumper/skill-shot exposure and don't turn a secure lead into a Powerfield control experiment. **Observed strategy.** [S3]

**Playing behind:** **Powerball Mania** is the practical blow-up route: each successful Powerfield upper hole is 50M, with repeated jackpots possible. If LITZ is already close, finishing the Door provides the highest deep-game ceiling. [S2][S3]

**Key recurring decision:** **start regular Multiball after one lock or spend another shot building the second lock?** One lock gets protection sooner but starts Jackpot at 15M; two locks raise it immediately to **40M** and are the preferred scoring setup when survival allows. [S2][S3]

## Danger zones

1. **Lock lane reject:** narrow sweet spot; even a seemingly clean hit can bounce straight toward the center drain. [S2]
2. **Slot Machine kickout:** extremely copy-dependent; mastering its catch/dead-pass is arguably the most important control skill on TZ. [S2][S3]
3. **Town Square bumpers:** positioned beside the huge left outlane and can also eject toward center; this is why the normal skill shot is often avoided. [S2][S3]
4. **Powerball:** lighter, faster, bouncier, and completely unaffected by the Spiral Helper magnets. [S2]
5. **Powerfield during Mania:** concentrating on Magna-Flip while two other balls remain live on the main playfield can turn a 50M opportunity into an immediate Multiball collapse.

## Spoken commentary cues

* “They've got two balls locked, so starting Multiball now gives them the **40-million Jackpot** instead of fifteen.”
* “Piano is the Jackpot; after they collect it, they have to cross over to the **Camera to relight**.”
* “That's the Powerball—the right orbit puts it back in the Gumball Machine and starts **Powerball Mania**.”
* “Every hole at the top of the Powerfield is **50 million**.”
* “Those Mania points are sitting in **bonus**, so a tilt here would wipe them out.”
* “The Door Handle is flashing—they're one collect away from **Lost in the Zone**.”

## Trivia

* Twilight Zone was Pat Lawlor's immediate follow-up to the record-setting **The Addams Family** and became one of Williams/Bally's most mechanically elaborate widebodies. [S3][S4]
* Its white **ceramic Powerball** is lighter than a steel pinball and immune to the game's magnets. [S2][S4]
* The mechanical **clock** nearly disappeared during cost-cutting; the game's tooling budget reportedly ran more than $200,000 over target. [S4]
* Twilight Zone was intended to use Williams' then-new **DCS sound system**, but time constraints prevented it; *Indiana Jones* became the first production DCS title. [S4]
* **Fast Lock** deliberately tunes its radio through music and callouts from earlier Pat Lawlor games including *Banzai Run*, *Earthshaker*, *Whirlwind*, *FunHouse* and *The Addams Family*. [S2][S4]

## Questions for the humans

### Tournament and venue checks

1. Which ROM is installed?
   A. **9.4**
   B. **9.4H home ROM**
   C. 9.2
   D. L-4 or earlier
   E. Other / unknown

2. Is Tournament Mode enabled?
   A. Yes
   B. No
   C. Custom tournament settings
   D. Unknown

3. How are Extra Balls handled?
   A. Disabled
   B. Played normally
   C. Must be plunged
   D. Custom point/rule conversion

4. How is the Powerball configured?
   A. Physical ceramic Powerball, stock six-ball setup
   B. Physical Powerball with tournament-modified ball count
   C. Powerball removed and **software-simulated**
   D. Unknown

5. Is a normal ball saver active?
   A. None
   B. First ball only
   C. All balls / later-ROM adjustment
   D. Unknown

6. Which feed is particularly problematic?
   A. Slot Machine kickout
   B. Lock-lane rejects
   C. Town Square / left outlane
   D. Ramp rejects
   E. Powerfield
   F. Nothing notable

### Uncertainties and conflicts

* **Release date:** contemporary/archival sources vary between **April 1993** and **May 4, 1993**. [S3][S4] Use *Bally 1993* unless an exact date is necessary.
* **Latest ROM terminology:** 9.4 is the latest normal official revision verified here; **9.4H** is Williams' October 22, 1998 **home/free-play** derivative with extra adjustments. [S1]
* **Multiball restart timer:** the exhaustive Sigma rulesheet says **15 seconds** [S2], while other contemporary/current references use **12 seconds** [S5]. Revision/timing presentation may explain the discrepancy; avoid quoting an exact number until tested.
* **Ball save:** early/default TZ is famously saver-less, but **9.2 added additional saver adjustment capability**. [S1][S2]
* **Powerball fairness:** the physical Powerball's location is globally shared between players. Tournament Mode makes several random awards fairer but does not eliminate this physical-state issue; simulation or a tournament-specific ball setup may be used. [S2]
* Slot kickout, Lock rejects, Powerfield leveling and Spiral Helper behavior are strongly copy-dependent.

## Human resolutions

1. Which ROM is installed?
   A. **9.4**
   B. **9.4H home ROM**
   C. 9.2
   D. L-4 or earlier
   E. Other / unknown
   **Human answer:** A. **9.4**

2. Is Tournament Mode enabled?
   A. Yes
   B. No
   C. Custom tournament settings
   D. Unknown
   **Human answer:** A. Yes

3. How are Extra Balls handled?
   A. Disabled
   B. Played normally
   C. Must be plunged
   D. Custom point/rule conversion
   **Human answer:** A. Disabled

4. How is the Powerball configured?
   A. Physical ceramic Powerball, stock six-ball setup
   B. Physical Powerball with tournament-modified ball count
   C. Powerball removed and **software-simulated**
   D. Unknown
   **Human answer:** A. Physical ceramic Powerball, stock six-ball setup

5. Is a normal ball saver active?
   A. None
   B. First ball only
   C. All balls / later-ROM adjustment
   D. Unknown
   **Human answer:** default

6. Which feed is particularly problematic?
   A. Slot Machine kickout
   B. Lock-lane rejects
   C. Town Square / left outlane
   D. Ramp rejects
   E. Powerfield
   F. Nothing notable
   **Human answer:** F. Nothing notable

## Sources

**[S1]** *Twilight Zone ROM Revisions* — Williams/Bally archive via Planetary Pinball. **Primary software source.** L-1 through L-4, 9.2, 9.4/9.4H, tournament-module and ball-save changes.
[Planetary Pinball ROM revision archive](https://www.planetarypinball.com/mm5/Williams/tech/roms/twilight.html?utm_source=chatgpt.com)

**[S2]** *Twilight Zone Rule Sheet* — Kevin Martin (“Sigma”), 1994–1997. **Detailed contemporary technical/rules source.** Gumball/Powerball, jackpots, Door, skill shots, LITZ, persistence, Tournament Mode and physical behavior.
[Twilight Zone detailed rulesheet](https://gamefaqs.gamespot.com/pinball/915948-twilight-zone/faqs/1467?utm_source=chatgpt.com)

**[S3]** *Ready to Battle? Twilight Zone Pinball Tutorial* — James McFatter, Kineticist; updated April 29, 2026. **Modern competitive strategy source.** Multiball-first route, Powerball Mania, shot priorities and danger feeds.
[Kineticist Twilight Zone tutorial](https://www.kineticist.com/news/twilight-zone-pinball-tutorial?utm_source=chatgpt.com)

**[S4]** *Twilight Zone Machine Archive* — Pinside. **Identity/history source.** Production, credits, WPC hardware, Powerball, clock, sound-system history and code listing.
[Pinside Twilight Zone archive](https://pinside.com/pinball/machine/twilight-zone/details?utm_source=chatgpt.com)

**[S5]** *Twilight Zone Strategy Card* — Pinball Cards; updated July 21, 2026. **Current concise tournament reference.** Skill-shot priorities, Multiball flow, Powerball Mania and restart shorthand.
[Pinball Cards Twilight Zone strategy](https://pinballcards.net/twilight-zone-1993/?utm_source=chatgpt.com)
