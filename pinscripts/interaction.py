"""Shared terminal interaction helpers."""

import re
import sys

try:
    import termios
except ImportError:  # pragma: no cover - non-POSIX fallback
    termios = None


def set_terminal_title(title, stream=None):
    stream = stream or sys.stderr
    if not stream.isatty():
        return False

    safe_title = re.sub(r"[\x00-\x1f\x7f]", "", title).strip()
    if not safe_title:
        return False

    stream.write(f"\033]0;{safe_title}\007")
    stream.flush()
    return True


def _read_tty_until_end(stream):
    """Read pasted text without the terminal's per-line input-size limit."""
    descriptor = stream.fileno()
    original_settings = termios.tcgetattr(descriptor)
    paste_settings = original_settings.copy()
    paste_settings[6] = original_settings[6].copy()
    paste_settings[3] &= ~termios.ICANON
    paste_settings[6][termios.VMIN] = 1
    paste_settings[6][termios.VTIME] = 0
    termios.tcsetattr(descriptor, termios.TCSANOW, paste_settings)
    lines = []
    current_line = []
    try:
        while True:
            character = stream.read(1)
            if character in {"", "\x04"}:
                break
            if character in {"\n", "\r"}:
                line = "".join(current_line)
                current_line = []
                if line == "::end":
                    break
                lines.append(line)
            else:
                current_line.append(character)
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, original_settings)

    if current_line:
        lines.append("".join(current_line))
    return "\n".join(lines).strip()


def read_until_end(stream=None):
    """Read lines through ``::end`` or EOF, including very long TTY pastes."""
    stream = stream or sys.stdin
    if termios is not None and stream.isatty():
        try:
            return _read_tty_until_end(stream)
        except (OSError, termios.error):
            pass

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "::end":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def read_chatgpt_response(kind):
    print(
        f"\nPaste the ChatGPT {kind} response below. "
        "Finish with a line containing only ::end (or press Ctrl-D):"
    )
    return read_until_end()


def confirm_overwrite(path):
    if not path.exists():
        return True

    try:
        answer = input(f"{path} already exists. Overwrite? [y/N] ")
    except EOFError:
        answer = ""
    return answer.strip().lower() in {"y", "yes"}
