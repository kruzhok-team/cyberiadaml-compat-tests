# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The EXT-FA alphabet grammar tests
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

import re

import pytest

from cgmlval.alphabet import (FA_INPUT, FA_INPUT_RE, FA_OUTPUT_RE,
                              AlphabetError, parse, translate)


def matches(expr, symbol):
    return re.fullmatch(translate(expr), symbol) is not None


def test_ranges_and_counts():
    assert matches("[a-z]{1,10}", "abc")
    assert not matches("[a-z]{1,10}", "ABC")
    assert not matches("[a-z]{1,10}", "abcdefghijk")
    assert matches("[0-9]{2}", "42")
    assert not matches("[0-9]{2}", "4")


def test_group_alternatives_and_optional():
    assert matches("(START|STOP)", "STOP")
    assert not matches("(START|STOP)", "START|STOP")
    assert matches("ab?", "a")
    assert matches("ab?", "ab")
    assert matches("(ab){2}c?", "abab")


def test_escapes_and_any_character():
    assert matches(r"(__|\-\-)", "--")
    assert matches(r"a\.b", "a.b")
    assert not matches(r"a\.b", "axb")
    assert matches(r"\\", "\\")
    assert matches(".", "x")
    assert not matches(".", " ")
    assert matches("[\\]\\-]", "-")


@pytest.mark.parametrize("expr", [
    "a*", "a+", "^a", "a$",          # infinite or anchored constructs
    "{2}", "?", "a{3,1}", "a{1, 2}", "a{x}",
    "(a", "a)", "a|b", "[a", "a]", "a}",
    "a-b", "a,b", "a\\", "a\\x", "[]", "()", "(a|)", "[b-a]", "[^a]", "",
])
def test_rejected_expressions(expr):
    with pytest.raises(AlphabetError):
        translate(expr)


def test_plain_alphabet_lines():
    table = parse(FA_INPUT, "Start\nStop\nPause\n")
    assert table.errors == []
    assert table.symbols == ["Start", "Stop", "Pause"]
    assert table.contains("Stop")
    assert not table.contains("stop")


def test_empty_and_blank_lines_reported():
    table = parse(FA_INPUT, "a\n\nb")
    assert [line for line, _ in table.errors] == [1]
    assert parse(FA_INPUT, "  \n").errors == [(0, "the alphabet is empty")]


def test_regex_alphabet_membership_excludes_reserved():
    table = parse(FA_INPUT_RE, "[a-z]{1,10}\n[0-9]{1,2}\n(__|\\-\\-)")
    assert table.errors == []
    assert table.contains("exits")
    assert table.contains("--")
    assert not table.contains("exit")
    assert not table.contains("Exit")


def test_regex_alphabet_error_names_the_line():
    table = parse(FA_OUTPUT_RE, "[01]\nx*")
    assert len(table.errors) == 1
    line, message = table.errors[0]
    assert line == 1
    assert "'*'" in message
