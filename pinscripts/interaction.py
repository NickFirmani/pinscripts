"""Shared terminal interaction helpers."""

import re
import sys


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


def read_chatgpt_response(kind):
    print(
        f"\nPaste the ChatGPT {kind} response below. "
        "Finish with a line containing only ::end (or press Ctrl-D):"
    )
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


def confirm_overwrite(path):
    if not path.exists():
        return True

    try:
        answer = input(f"{path} already exists. Overwrite? [y/N] ")
    except EOFError:
        answer = ""
    return answer.strip().lower() in {"y", "yes"}
