# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The requirement table vs the testing specification rows
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

from cgmlval import rules
from cgmlval.requirements import (REQUIREMENTS, VALIDATOR, INTEGRATION,
                                  WRITE_ONLY, PENDING)
from tests import spec_rows

SPEC = spec_rows.by_id()

rules.load_checks()


def test_the_spec_rows_are_complete():
    for row in SPEC.values():
        assert row.level and row.senses, row


def test_the_table_lists_exactly_the_spec_rows():
    assert sorted(set(SPEC) - set(REQUIREMENTS)) == []
    assert sorted(set(REQUIREMENTS) - set(SPEC)) == []


def test_the_table_levels_and_senses_follow_the_spec():
    drift = [(ident, row.level, row.senses, entry.level, entry.senses)
             for ident, entry in REQUIREMENTS.items()
             for row in [SPEC[ident]]
             if (row.level, row.senses) != (entry.level, entry.senses)]
    assert drift == []


def test_the_table_scopes_are_known():
    for ident, entry in REQUIREMENTS.items():
        assert entry.scope in (VALIDATOR, INTEGRATION, WRITE_ONLY, PENDING), \
            ident


def test_a_pending_requirement_has_no_rule_yet():
    cited = {r.req for r in rules.REGISTRY.values() if r.req is not None}
    stale = sorted(ident for ident, entry in REQUIREMENTS.items()
                   if entry.scope == PENDING and ident in cited)
    assert stale == []
