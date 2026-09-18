# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The testing specification as a test source: the requirement rows
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

import pathlib
import re
from collections import namedtuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "CyberiadaML-GraphML-1.0-TESTING-SPEC.md"

# a row starts with its id; the level and the sense marker may be absent on
# sub-rows, which then inherit them from the enclosing row
_ROW = re.compile(r"^(\s*)[-*]?\s*`(CGML-[\w.*-]+)`:?\s*(MUST|SHOULD|MAY)?")
_SENSES = re.compile(r"\[([RWX](?:/[RWX])*)\]")
_HEADING = re.compile(r"^\*\*([0-9.]+ [^*]+)\*\*")
_ORDER = "RWX"

Row = namedtuple("Row", "id level senses section line")


class _Node(object):
    def __init__(self, indent, ident, level, senses, section, line):
        self.indent, self.id, self.section, self.line = indent, ident, section, line
        self.level, self.senses, self.children = level, senses, []


def _normalise(senses):
    return "".join(s for s in _ORDER if s in senses)


def parse(text=None):
    """The requirement rows of the testing specification, in document order.

    Group rows (`CGML-6.9-4-*`) are not requirements: they only pass their
    level and senses down.  A row without a sense marker takes the union of
    its sub-rows' senses."""
    if text is None:
        text = SPEC.read_text(encoding="utf-8")
    nodes, stack, section, current = [], [], None, None
    for number, raw in enumerate(text.splitlines(), 1):
        heading = _HEADING.match(raw)
        if heading:
            section, current = heading.group(1).strip(), None
            continue
        match = _ROW.match(raw)
        if match:
            indent = len(match.group(1).expandtabs(4))
            while stack and stack[-1].indent >= indent:
                stack.pop()
            marker = _SENSES.search(raw[match.end():])
            node = _Node(indent, match.group(2), match.group(3),
                         set(marker.group(1).replace("/", "")) if marker
                         else set(), section, number)
            if stack:
                stack[-1].children.append(node)
            nodes.append((node, stack[-1] if stack else None))
            stack.append(node)
            current = node
        elif current is not None and raw.strip() and raw[:1].isspace() \
                and not raw.lstrip().startswith(("|", "```", "#")):
            marker = _SENSES.search(raw)
            if marker and not current.senses:
                current.senses = set(marker.group(1).replace("/", ""))
        else:
            current = None
    for node, parent in nodes:
        if parent is not None:
            node.level = node.level or parent.level
            node.senses = node.senses or set(parent.senses)
    for node, _ in reversed(nodes):
        if not node.senses:
            for child in node.children:
                node.senses |= child.senses
    return [Row(n.id, n.level, _normalise(n.senses), n.section, n.line)
            for n, _ in nodes if not n.id.endswith("*")]


def by_id(text=None):
    rows = parse(text)
    table = {row.id: row for row in rows}
    assert len(table) == len(rows), "duplicate requirement ids in the spec"
    return table
