# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The standard's own example documents must conform to the standard
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

from cgmlval import rules
from tests import standard_text

FIXTURES = standard_text.ROOT / "fixtures" / "standard"
DOCUMENTS = standard_text.appendix_documents()
IDS = [label for label, _ in DOCUMENTS]


def test_appendix_documents_found():
    assert IDS == ["Г.1", "Г.2", "Г.3", "Г.4"]


@pytest.mark.parametrize("label,document", DOCUMENTS, ids=IDS)
def test_appendix_document_is_clean(label, document):
    ctx = rules.run_document(document.encode("utf-8"), label)
    findings = [f for f in ctx.report.findings
                if f.severity in ("ERROR", "WARNING")]
    assert findings == [], [f.message for f in findings]


@pytest.mark.parametrize("label,document", DOCUMENTS, ids=IDS)
def test_standard_fixture_mirrors_the_text(label, document):
    name = "F-STD-G%s.graphml" % label.split(".")[1]
    fixture = (FIXTURES / name).read_text(encoding="utf-8")
    assert fixture.strip() == document.strip()
