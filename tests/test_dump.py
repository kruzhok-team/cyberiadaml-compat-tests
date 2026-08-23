# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The canonical dump tests
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

import pytest

from cgmlval import cli, dump, rules
from docbuilder import minimal

EXAMPLES = pathlib.Path(__file__).parent / "examples"


def validated(data, filename="test.graphml"):
    ctx = rules.run_document(data, filename)
    assert not ctx.report.has_errors(), \
        [f.rule for f in ctx.report.findings]
    return ctx


def expected(name):
    return (EXAMPLES / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["minimal", "hierarchy", "extensions"])
def test_dump_matches_expected(name):
    path = EXAMPLES / (name + ".graphml")
    ctx = validated(path.read_bytes(), str(path))
    assert ctx.report.findings == []
    assert dump.render(ctx.model) == expected(name + ".expected.txt")


def test_dump_deterministic():
    path = EXAMPLES / "hierarchy.graphml"
    first = validated(path.read_bytes())
    second = validated(path.read_bytes())
    assert dump.render(first.model) == dump.render(second.model)
    assert dump.render(first.model) == dump.render(first.model)


def test_default_and_declared_key_twins_dump_identically():
    declared = validated(minimal())
    defaults = validated(minimal(keys=""))
    assert dump.render(declared.model) == dump.render(defaults.model)


def test_cli_dump_prints_the_dump(capsys):
    code = cli.main(["dump", str(EXAMPLES / "minimal.graphml")])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == expected("minimal.expected.txt")
    assert captured.err == ""


def test_cli_dump_refuses_an_invalid_document(tmp_path, capsys):
    bad = tmp_path / "bad.graphml"
    bad.write_bytes(minimal().replace(b"Cyberiada-GraphML-1.0", b"Wrong"))
    code = cli.main(["dump", str(bad)])
    captured = capsys.readouterr()
    assert code == 1
    assert "cgml-canonical-dump" not in captured.out
    assert "CGML-5.4-2" in captured.out
    assert "invalid" in captured.out
