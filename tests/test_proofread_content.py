import tempfile
import unittest
from pathlib import Path

from scripts.proofread_content import (
    guardrail_violations,
    iter_prose,
    replace_spans,
    sentence_spans,
)


class ProofreadContentTests(unittest.TestCase):
    def test_sentence_spans_keeps_initials_and_decimals_together(self):
        text = "Lyman F. Sheats wrote V1.70. It improved the rules."

        sentences = [text[start:end] for start, end in sentence_spans(text)]

        self.assertEqual(
            sentences,
            ["Lyman F. Sheats wrote V1.70.", "It improved the rules."],
        )

    def test_sentence_spans_treats_fragment_as_one_prompt(self):
        text = "Cash now versus build and multiply"

        self.assertEqual(sentence_spans(text), [(0, len(text))])

    def test_iter_prose_excludes_identifiers_names_and_risk(self):
        data = {
            "id": "game-id",
            "name": "Game Name",
            "hook": "A hook.",
            "shots": [
                {
                    "name": "Left Ramp",
                    "value": "It scores points.",
                    "risk": "High",
                    "diagram": 1,
                }
            ],
            "image": "images/game.jpg",
        }

        prose = dict(iter_prose(data))

        self.assertEqual(
            prose,
            {("hook",): "A hook.", ("shots", 0, "value"): "It scores points."},
        )

    def test_guardrails_reject_number_and_proper_term_changes(self):
        self.assertIn(
            "changed numeric tokens",
            guardrail_violations("Hit Bell 3 times.", "Hit Bell three times."),
        )
        self.assertIn(
            "changed protected capitalized terms",
            guardrail_violations("Start Jam at the ramp.", "Start Tour at the ramp."),
        )

    def test_guardrails_allow_small_grammar_correction(self):
        self.assertEqual(
            guardrail_violations("Three hits gets the award.", "Three hits get the award."),
            [],
        )

    def test_guardrails_protect_typographic_dashes_and_large_word_additions(self):
        self.assertIn(
            "changed '\u2014' symbols",
            guardrail_violations("Shots\u2014then jackpot.", "Shots - then jackpot."),
        )
        self.assertIn(
            "added or removed multiple words",
            guardrail_violations(
                "It remains active until changed.",
                "It remains active until it is changed.",
            ),
        )

    def test_replace_spans_preserves_text_between_sentences(self):
        text = "First are wrong.  Second is fine."
        spans = sentence_spans(text)

        corrected = replace_spans(text, [(spans[0][0], spans[0][1], "First is wrong.")])

        self.assertEqual(corrected, "First is wrong.  Second is fine.")


if __name__ == "__main__":
    unittest.main()
