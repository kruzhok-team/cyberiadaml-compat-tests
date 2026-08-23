# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The report-only smoke run over the sibling sample corpora
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

# The corpora contain documents with known defects: the run only asserts
# that validation never crashes and prints a per-file verdict summary.

import pathlib

import pytest

from cgmlval import rules

CORPORA = (
    pathlib.Path.home() / "sources/libcyberiadaml/graph-samples",
    pathlib.Path.home() / "sources/libcyberiadaml/tests",
    pathlib.Path.home() / "sources/lapki-compiler/examples",
)


def _corpus_files():
    for corpus in CORPORA:
        if corpus.is_dir():
            yield from sorted(corpus.rglob("*.graphml"))


@pytest.mark.parametrize("path", list(_corpus_files()),
                         ids=lambda p: str(p.relative_to(pathlib.Path.home())))
def test_corpus_document_never_crashes_the_validator(path):
    ctx = rules.run_document(path.read_bytes(), str(path))
    report = ctx.report
    counts = {}
    for finding in report.findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    print("%s: %s (%s)" % (path.name, report.verdict(False),
                           ", ".join("%d %s" % (n, s.lower())
                                     for s, n in sorted(counts.items()))
                           or "clean"))
    assert report.layers_run


def test_corpora_present_or_skip():
    if not any(corpus.is_dir() for corpus in CORPORA):
        pytest.skip("no sibling sample corpora on this machine")
