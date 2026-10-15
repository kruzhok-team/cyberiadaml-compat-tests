# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The Lapki dialect corpus against the reference dialect pass
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

import collections
import json
import pathlib

import pytest

from cgmlval import dump, rules

CORPUS = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / \
    "dialect" / "lapki"
DOCUMENTS = json.loads((CORPUS / "manifest.json")
                       .read_text(encoding="utf-8"))["documents"]


def run(name, dialect="lapki"):
    data = (CORPUS / (name + ".graphml")).read_bytes()
    return rules.run_document(data, name + ".graphml", dialect=dialect)


def errors(ctx):
    return sorted({f.req or f.rule for f in ctx.report.findings
                   if f.severity == "ERROR"})


def test_manifest_lists_the_documents():
    files = sorted(p.stem for p in CORPUS.glob("*.graphml"))
    assert files == sorted(DOCUMENTS)
    for name, entry in DOCUMENTS.items():
        assert entry["status"] in ("valid", "invalid"), name
        expected = (CORPUS / (name + ".expected.txt")).exists()
        assert expected == (entry["status"] == "valid"), name


@pytest.mark.parametrize("name", sorted(DOCUMENTS))
def test_repairs(name):
    ctx = run(name)
    counts = collections.Counter(f.req for f in ctx.report.findings
                                 if f.layer == 0)
    text = "".join("%s %d\n" % item for item in sorted(counts.items()))
    assert text == (CORPUS / (name + ".repairs.txt")).read_text(
        encoding="utf-8")


@pytest.mark.parametrize("name", sorted(DOCUMENTS))
def test_result(name):
    ctx = run(name)
    entry = DOCUMENTS[name]
    if entry["status"] == "valid":
        assert errors(ctx) == []
        assert dump.render(ctx.model) == (
            CORPUS / (name + ".expected.txt")).read_text(encoding="utf-8")
    else:
        assert errors(ctx) == entry["errors"]


@pytest.mark.parametrize("name", sorted(DOCUMENTS))
def test_standard_reading_rejects_a_repaired_document(name):
    if not (CORPUS / (name + ".repairs.txt")).read_text(encoding="utf-8"):
        pytest.skip("no repair: a dialect document by its hint only")
    assert errors(run(name, dialect=None))
