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


def _find_separator(text):
    """The header '/' separator: the first '/' followed by a space, a
    newline or the end of the text."""
    idx = 0
    while True:
        idx = text.find("/", idx)
        if idx < 0:
            return -1
        if idx == len(text) - 1 or text[idx + 1] in " \n":
            return idx
        idx += 1


def _find_guard(text, end):
    """The last unescaped [...] pair directly before position end."""
    close = end - 1
    while close >= 0 and text[close] in " \n\t\r":
        close -= 1
    if close < 0 or text[close] != "]" or _escaped(text, close):
        return None
    start = close - 1
    while start >= 0:
        if text[start] == "[" and not _escaped(text, start):
            return start, close
        start -= 1
    return None


def _strip_param(head):
    """Split a trailing event parameter keyword off the header text."""
    words = head.split()
    if words and words[-1] in EVENT_PARAMS:
        return head[:head.rfind(words[-1])].rstrip(), words[-1]
    return head, None


def _resolve_brackets(text):
    return text.replace("\\[", "[").replace("\\]", "]")


def _parse_header(text, lineno, errors):
    """Parse a block header (possibly several lines up to the '/'
    separator, or the whole block when there is none); return (block,
    inline behaviour or None)."""
    stripped = text.rstrip()
    for keyword in KEYWORDS:
        prefix = keyword + "/"
        if stripped.startswith(prefix):
            inline = stripped[len(prefix):]
            if inline.startswith(" "):
                inline = inline[1:]
            return Block(keyword), inline or None
    sep = _find_separator(stripped)
    if sep < 0:
        head, inline = stripped, None
    else:
        head = stripped[:sep].rstrip()
        inline = stripped[sep + 1:]
        if inline.startswith(" "):
            inline = inline[1:]
    # the event parameter may follow the guard or the event name
    head, param = _strip_param(head)
    guard = None
    span = _find_guard(head, len(head))
    if span is not None:
        start, close = span
        guard = _resolve_brackets(head[start + 1:close])
        head = head[:start].rstrip()
    if param is None:
        head, param = _strip_param(head)
    trigger = head
    if not trigger and guard is None:
        errors.append((lineno, "empty event name in the event description"))
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
        # the header runs up to the first line carrying the separator;
        # without one the whole block is an event description
        header_end = len(run) - 1
        for offset, (_, text_line) in enumerate(run):
            if _find_separator(text_line.rstrip()) >= 0:
                header_end = offset
                break
        header = "\n".join(text_line for _, text_line in run[:header_end + 1])
        block, inline = _parse_header(header, run[0][0], errors)
        if inline:
            block.behaviour.append(inline)
        block.behaviour.extend(text_line for _, text_line in
                               run[header_end + 1:])
        block.verbatim = "\n".join(text for _, text in run)
        blocks.append(block)
        run = []
    return blocks, errors
