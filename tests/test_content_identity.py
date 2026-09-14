import unittest

from pinscripts.content import suggested_research_id


class ContentIdentityTests(unittest.TestCase):
    def test_stern_premium_and_le_share_a_canonical_id(self):
        self.assertEqual(
            suggested_research_id("JAWS (LE) Stern 2024"),
            "jaws-prem-le-stern-2024",
        )
        self.assertEqual(
            suggested_research_id("JAWS Premium Stern Pinball 2024"),
            "jaws-prem-le-stern-2024",
        )

    def test_jersey_jack_le_and_ce_share_a_canonical_id(self):
        self.assertEqual(
            suggested_research_id("Harry Potter (CE) Jersey Jack 2025"),
            "harry-potter-le-ce-jersey-jack-2025",
        )
        self.assertEqual(
            suggested_research_id("Harry Potter Limited Edition Jersey Jack Pinball 2025"),
            "harry-potter-le-ce-jersey-jack-2025",
        )


if __name__ == "__main__":
    unittest.main()
