# Pinball Streaming Quick Reference Generator

Create a one-page color-commentary quick reference for the following
pinball machine.

GAME:

{{GAME}}

The audience for this document is a pinball commentator who may know
pinball well but may not know this particular machine.

The document will be referenced DURING LIVE PLAY.

Prioritize:
1. What the player is trying to accomplish.
2. Why the player is shooting a particular shot.
3. What scoring opportunities materially change the match.
4. Risk/reward decisions.
5. What the commentator should notice before a drain.
6. Useful terminology.
7. Brief historical/trivia material for dead air.

Do NOT create a comprehensive rulesheet.

A commentator should be able to understand the game's core tournament
strategy in roughly 30 seconds.

Be particularly careful about:
- rules that differ by software revision
- tournament settings
- extra balls being disabled or converted to points
- progressive jackpots
- modes or features that carry between balls
- player-specific state
- manufacturer/year/designer facts
- similarly named games

When uncertain about a fact, omit it rather than invent it.

Return ONLY YAML that validates against the following JSON Schema. Include
every required property, use no properties the schema does not define, and
respect all array, string, pattern, numeric, and enum constraints.

```json
{{SCHEMA}}
```

Content guidance:

- Commentary cues should sound natural when spoken aloud.
- Avoid generic statements that could describe any pinball machine.
- Explain abbreviations when first used.
- `summary` should be approximately 3-7 concepts joined by arrows.
- Do not put citations, URLs, markdown, or footnotes in the YAML.
