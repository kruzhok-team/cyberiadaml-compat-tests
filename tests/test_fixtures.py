# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The conformance fixture corpus tests
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

import json
import pathlib

import pytest

from cgmlval import dump, rules
from cgmlval.requirements import REQUIREMENTS

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))

POSITIVE = sorted(name for name, entry in MANIFEST["fixtures"].items()
                  if "reject" not in entry)
NEGATIVE = sorted(name for name, entry in MANIFEST["fixtures"].items()
                  if "reject" in entry)


def run(name):
    path = FIXTURES / (name + ".graphml")
    return rules.run_document(path.read_bytes(), str(path))


@pytest.mark.parametrize("name", POSITIVE)
def test_positive_fixture_validates_clean(name):
    ctx = run(name)
    assert not ctx.report.has_errors(), \
        [f.rule for f in ctx.report.findings]


@pytest.mark.parametrize("name", POSITIVE)
def test_positive_fixture_matches_frozen_dump(name):
    ctx = run(name)
    golden = (FIXTURES / (name + ".expected.txt")).read_text(encoding="utf-8")
    assert dump.render(ctx.model) == golden


@pytest.mark.parametrize("name", NEGATIVE)
def test_negative_fixture_rejected_for_its_requirement(name):
    ctx = run(name)
    expected = MANIFEST["fixtures"][name]["reject"]
    found = {f.req for f in ctx.report.findings if f.severity == "ERROR"}
    assert expected in found, (expected, sorted(found))


@pytest.mark.parametrize("pair", MANIFEST["twins"],
                         ids=lambda p: "=".join(p))
def test_twin_fixtures_dump_identically(pair):
    first, second = (run(name) for name in pair)
    assert not first.report.has_errors()
    assert not second.report.has_errors()
    assert dump.render(first.model) == dump.render(second.model)


def test_manifest_names_known_files_and_requirements():
    for name, entry in MANIFEST["fixtures"].items():
        assert (FIXTURES / (name + ".graphml")).is_file(), name
        for req in entry.get("requirements", []):
            assert req in REQUIREMENTS, (name, req)
        if "reject" in entry:
            assert entry["reject"] in REQUIREMENTS, name
        else:
            assert (FIXTURES / (name + ".expected.txt")).is_file(), name
    for pair in MANIFEST["twins"]:
        assert len(pair) == 2
        for name in pair:
            assert name in MANIFEST["fixtures"], name
