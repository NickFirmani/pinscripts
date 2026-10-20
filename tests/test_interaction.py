import io
import unittest
from unittest.mock import patch

import pinscripts.interaction as interaction


class TtyInput(io.StringIO):
    def isatty(self):
        return True

    def fileno(self):
        return 42


class InteractionTests(unittest.TestCase):
    @staticmethod
    def terminal_settings():
        control_character_count = max(
            interaction.termios.VMIN, interaction.termios.VTIME
        ) + 1
        control_characters = [0] * control_character_count
        return [
            0,
            0,
            0,
            interaction.termios.ICANON | interaction.termios.ECHO,
            0,
            0,
            control_characters,
        ]

    def test_tty_reader_preserves_a_long_single_line_paste(self):
        pasted = '{"rules":"' + ("valuable mode. " * 500) + '"}'
        stream = TtyInput(pasted + "\n::end\nignored")
        settings = self.terminal_settings()

        with (
            patch.object(interaction.termios, "tcgetattr", return_value=settings),
            patch.object(interaction.termios, "tcsetattr") as set_attributes,
        ):
            result = interaction.read_until_end(stream)

        self.assertEqual(result, pasted)
        paste_settings = set_attributes.call_args_list[0].args[2]
        self.assertEqual(paste_settings[3] & interaction.termios.ICANON, 0)
        self.assertNotEqual(paste_settings[3] & interaction.termios.ECHO, 0)
        set_attributes.assert_called_with(
            42, interaction.termios.TCSADRAIN, settings
        )

    def test_tty_reader_treats_ctrl_d_as_end_of_input(self):
        stream = TtyInput("first line\nsecond line\x04ignored")

        with (
            patch.object(
                interaction.termios,
                "tcgetattr",
                return_value=self.terminal_settings(),
            ),
            patch.object(interaction.termios, "tcsetattr"),
        ):
            result = interaction.read_until_end(stream)

        self.assertEqual(result, "first line\nsecond line")

    def test_non_tty_reader_keeps_input_compatible_behavior(self):
        with patch("builtins.input", side_effect=["first", "second", "::end"]):
            result = interaction.read_until_end(io.StringIO())

        self.assertEqual(result, "first\nsecond")


if __name__ == "__main__":
    unittest.main()
