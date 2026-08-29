# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The standard text as a test source: shared extraction helpers
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

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
STANDARD = ROOT / "docs" / "PNST_1044-2025.md"
_FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)
_DATA = re.compile(r'<data key="dData">(.*?)</data>', re.S)


def text():
    return STANDARD.read_text(encoding="utf-8")


def fenced_blocks(section=None):
    """The fenced code blocks of the standard, optionally of one section
    given as (start heading, end heading) markers."""
    body = text()
    if section:
        start, end = section
        body = body[body.index(start):body.index(end)]
    return [block for _, block in _FENCE.findall(body)]


def appendix_documents():
    """The complete GraphML documents of appendix Г: [(label, text)]."""
    body = text()
    body = body[body.index("## Приложение Г"):body.index("## Библиография")]
    documents = []
    for match in _FENCE.finditer(body):
        block = match.group(2)
        if "<graphml" in block and "</graphml>" in block:
            heading = re.findall(r"^### (\S+)", body[:match.start()],
                                 re.M)[-1]
            documents.append((heading, block))
    return documents


def fragment(marker):
    """The first fenced block containing the marker text."""
    for block in fenced_blocks():
        if marker in block:
            return block
    raise KeyError(marker)


def behaviour_text(block):
    """The dData value of a fragment with the ↳ marks resolved (↳ at the
    end of a line is the line break itself, ↳↳ an empty line) and XML
    entities unescaped."""
    match = _DATA.search(block)
    value = match.group(1) if match else block
    lines = []
    for line in value.split("\n"):
        text = line.rstrip("↳")
        marks = len(line) - len(text)
        if not text.strip() and marks:
            lines.append("")
            continue
        lines.append(text)
        if marks > 1:
            lines.append("")
    return html.unescape("\n".join(lines))
