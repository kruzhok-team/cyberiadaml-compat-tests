# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The parser of the 6.8 behaviour text (triggers, guards, behaviour blocks)
#
# Copyright (C) 2026 Alexey Fedoseev <aleksey@fedoseev.net>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/
#
# -----------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Optional

ENTRY = "entry"
EXIT = "exit"
DO = "do"
EVENT = "event"

KEYWORDS = (ENTRY, EXIT, DO)
EVENT_PARAMS = ("propagate", "block", "defer")


@dataclass
class Block:
    kind: str                      # entry | exit | do | event
    trigger: str = ""              # event name, verbatim (event blocks)
    param: Optional[str] = None    # propagate | block | defer
    guard: Optional[str] = None    # guard text with the bracket escapes resolved
    behaviour: list = field(default_factory=list)
    verbatim: str = ""


def _escaped(line, idx):
    return idx > 0 and line[idx - 1] == "\\"


def _find_separator(line):
    """The header '/' separator: the first '/' followed by a space or EOL."""
    idx = 0
    while True:
        idx = line.find("/", idx)
        if idx < 0:
            return -1
        if idx == len(line) - 1 or line[idx + 1] == " ":
            return idx
        idx += 1


def _find_guard(line, sep):
    """The last unescaped [...] pair directly before the '/' separator."""
    close = sep - 1
    while close >= 0 and line[close] == " ":
        close -= 1
    if close < 0 or line[close] != "]" or _escaped(line, close):
        return None
    start = close - 1
    while start >= 0:
        if line[start] == "[" and not _escaped(line, start):
            return start, close
        start -= 1
    return None


def _resolve_brackets(text):
    return text.replace("\\[", "[").replace("\\]", "]")


def _parse_header(line, lineno, errors):
    """Parse a block header; return (block, inline behaviour or None)."""
    stripped = line.rstrip()
    for keyword in KEYWORDS:
        prefix = keyword + "/"
        if stripped.startswith(prefix):
            inline = stripped[len(prefix):]
            if inline.startswith(" "):
                inline = inline[1:]
            return Block(keyword), inline or None
    sep = _find_separator(stripped)
    if sep < 0:
        errors.append((lineno, "missing '/' in the event description"))
        return Block(EVENT, trigger=stripped), None
    guard = None
    head = stripped[:sep].rstrip()
    span = _find_guard(stripped, sep)
    if span is not None:
        start, close = span
        guard = _resolve_brackets(stripped[start + 1:close])
        head = stripped[:start].rstrip()
    param = None
    words = head.split()
    if words and words[-1] in EVENT_PARAMS:
        param = words[-1]
        head = head[:head.rfind(param)].rstrip()
    trigger = head
    if not trigger and guard is None:
        errors.append((lineno, "empty event name in the event description"))
    inline = stripped[sep + 1:]
    if inline.startswith(" "):
        inline = inline[1:]
    return Block(EVENT, trigger=trigger, param=param, guard=guard), \
        inline or None


def parse(text):
    """Parse a dData behaviour value; return (blocks, errors).

    Blocks are separated by blank lines; an empty value is zero blocks.
    Errors are (line index, message) pairs for the L3 checks.
    """
    blocks = []
    errors = []
    if text is None:
        return blocks, errors
    lines = text.split("\n")
    run = []      # (line index, line) of the current block
    for lineno, line in enumerate(lines + [""]):
        if line.strip():
            run.append((lineno, line))
            continue
        if not run:
            continue
        header_lineno, header = run[0]
        block, inline = _parse_header(header, header_lineno, errors)
        if inline:
            block.behaviour.append(inline)
        block.behaviour.extend(text for _, text in run[1:])
        block.verbatim = "\n".join(text for _, text in run)
        blocks.append(block)
        run = []
    return blocks, errors
