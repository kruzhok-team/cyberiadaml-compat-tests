# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The rule registry vs requirements coverage audit
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

from cgmlval import rules
from cgmlval.findings import ERROR, INFO, WARNING
from cgmlval.requirements import REQUIREMENTS, VALIDATOR

rules.load_checks()

# the L1 preconditions that have no clause of their own
REQLESS = ("xml-not-empty", "xml-well-formed")


def test_every_rule_cites_a_known_requirement():
    for rule_obj in rules.REGISTRY.values():
        if rule_obj.name in REQLESS:
            assert rule_obj.req is None
        else:
            assert rule_obj.req in REQUIREMENTS, rule_obj.name


def test_no_rule_cites_an_out_of_scope_requirement():
    for rule_obj in rules.REGISTRY.values():
        if rule_obj.req is None:
            continue
        assert REQUIREMENTS[rule_obj.req].scope == VALIDATOR, \
            "%s cites the %s requirement %s" % \
            (rule_obj.name, REQUIREMENTS[rule_obj.req].scope, rule_obj.req)


def test_every_validator_requirement_has_a_rule():
    cited = {r.req for r in rules.REGISTRY.values() if r.req is not None}
    uncovered = sorted(req for req, entry in REQUIREMENTS.items()
                       if entry.scope == VALIDATOR and req not in cited)
    assert uncovered == []


def test_rule_metadata_is_well_formed():
    for rule_obj in rules.REGISTRY.values():
        assert rule_obj.layer in (1, 2, 3, 4), rule_obj.name
        assert rule_obj.severity in (ERROR, WARNING, INFO), rule_obj.name
        assert rule_obj.title, rule_obj.name


def test_every_validator_requirement_has_a_fixture():
    root = pathlib.Path(__file__).resolve().parent.parent
    manifest = json.loads((root / "fixtures" / "manifest.json")
                          .read_text(encoding="utf-8"))["fixtures"]
    cited = set()
    for entry in manifest.values():
        cited.update(entry.get("requirements", []))
        if "reject" in entry:
            cited.add(entry["reject"])
    uncovered = sorted(req for req, entry in REQUIREMENTS.items()
                       if entry.scope == VALIDATOR and req not in cited)
    assert uncovered == []
