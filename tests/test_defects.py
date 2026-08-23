# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# Defect clustering and registry tests
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

from intharness import defects

ROOT = pathlib.Path(__file__).resolve().parent.parent

MANIFEST = {
    "core/F-A": {"profile": "CORE",
                 "requirements": ["CGML-5.4-2", "CGML-5.5-2"]},
    "core/F-B": {"profile": "CORE", "requirements": ["CGML-5.6-1"]},
    "negative/X-1": {"reject": "CGML-5.4-2"},
    "negative/X-2": {"reject": "CGML-5.9-1"},
    "negative/X-3": {"reject": "CGML-5.5-2"},
}


def test_reject_clusters_by_diagnostic():
    result = {"positive": {
        "core/F-A": {"outcome": "rejected", "diagnostic": "no platform"},
        "core/F-B": {"outcome": "rejected", "diagnostic": "no platform"},
    }, "negative": {}}
    clusters = defects.cluster_driver(result, MANIFEST)
    assert list(clusters) == ["reject:no platform"]
    entry = clusters["reject:no platform"]
    assert entry["fixtures"] == ["core/F-A", "core/F-B"]
    assert entry["kind"] == defects.READ
    assert entry["requirements"] == {"CGML-5.4-2", "CGML-5.5-2",
                                     "CGML-5.6-1"}


def test_validate_clusters_per_requirement():
    result = {"positive": {
        "core/F-A": {"outcome": "converted", "validate_errors": [
            "ERROR CGML-appendix-B-1: standard key dRegion redeclared",
            "ERROR CGML-6.9-4-3: inadmissible transitionOrder value"]},
    }, "negative": {}}
    clusters = defects.cluster_driver(result, MANIFEST)
    assert set(clusters) == {"validate:CGML-appendix-B-1",
                             "validate:CGML-6.9-4-3"}
    entry = clusters["validate:CGML-appendix-B-1"]
    assert entry["requirements"] == {"CGML-appendix-B-1"}
    assert entry["blocked"] == {"CGML-5.4-2", "CGML-5.5-2"}
    assert entry["kind"] == defects.WRITE


def test_dump_signature_normalizes_numbers():
    result = {"positive": {
        "core/F-A": {"outcome": "converted", "validate_errors": [],
                     "dump_equal": False, "dump_diff":
                     "line 3: expected '  geometry: point -60.50 20.00', "
                     "got '  geometry: rect -60.50 20.00 -1.00 -1.00'"},
        "core/F-B": {"outcome": "converted", "validate_errors": [],
                     "dump_equal": False, "dump_diff":
                     "line 7: expected '  geometry: point 5.00 8.25', "
                     "got '  geometry: rect 5.00 8.25 -1.00 -1.00'"},
    }, "negative": {}}
    clusters = defects.cluster_driver(result, MANIFEST)
    assert len(clusters) == 1
    entry = next(iter(clusters.values()))
    assert entry["fixtures"] == ["core/F-A", "core/F-B"]
    assert entry["channel"] == "dump-equality"


def test_crash_cluster_kind():
    result = {"positive": {
        "core/F-A": {"outcome": "crash", "diagnostic": "Traceback\n  boom"},
    }, "negative": {}}
    clusters = defects.cluster_driver(result, MANIFEST)
    assert list(clusters) == ["crash:Traceback"]
    assert clusters["crash:Traceback"]["kind"] == defects.ROBUSTNESS


def test_missing_rejections():
    result = {"positive": {}, "negative": {
        "negative/X-1": {"outcome": "accepted"},
        "negative/X-2": {"outcome": "rejected", "diagnostic": "bad id"},
        "negative/X-3": {"outcome": "crash"},
    }}
    rows = defects.missing_rejections(result, MANIFEST)
    assert [row["fixture"] for row in rows] == ["negative/X-1",
                                                "negative/X-3"]
    assert rows[0]["requirement"] == "CGML-5.4-2"
    assert rows[0]["level"] == "MUST"
    assert rows[1]["outcome"] == "crash"


def _clusters():
    result = {"positive": {
        "core/F-A": {"outcome": "converted", "validate_errors": [],
                     "dump_equal": False,
                     "dump_diff": "line 3: expected 'x', got 'y'"},
        "core/F-B": {"outcome": "rejected", "diagnostic": "no platform"},
    }, "negative": {}}
    return defects.cluster_driver(result, MANIFEST)


def test_assign_registered_merges_signatures():
    registry = {("d", "reject:no platform"):
                {"id": "D-1", "driver": "d", "title": "mandatory platform",
                 "signatures": ["reject:no platform", "dump:'x'|'y'"]},
                ("d", "dump:'x'|'y'"):
                {"id": "D-1", "driver": "d", "title": "mandatory platform",
                 "signatures": ["reject:no platform", "dump:'x'|'y'"]}}
    records = defects.assign("d", _clusters(), registry)
    assert len(records) == 1
    record = records[0]
    assert record["id"] == "D-1"
    assert record["registered"]
    assert record["fixtures"] == ["core/F-A", "core/F-B"]
    assert record["channels"] == {"dump-equality", "round-trip"}
    assert record["severity"] == "major"


def test_assign_provisional_ids():
    records = defects.assign("d", _clusters(), {})
    assert [record["id"] for record in records] == ["D-NEW-1", "D-NEW-2"]
    assert not records[0]["registered"]
    assert all(record["title"] for record in records)


def test_severity_and_clause():
    assert defects.severity({"CGML-5.5-2"}) == "minor"
    assert defects.severity({"CGML-5.5-2", "CGML-5.4-2"}) == "major"
    assert defects.clause("CGML-6.9-4-5") == "§6.9"
    assert defects.clause("CGML-appendix-B-1") == "appendix Б"


def test_registry_file_integrity():
    data = json.loads((ROOT / "defects.json").read_text(encoding="utf-8"))
    seen_ids = set()
    seen_signatures = set()
    for record in data["defects"]:
        assert record["id"] not in seen_ids
        seen_ids.add(record["id"])
        assert record["driver"]
        assert record["title"]
        for signature in record["signatures"]:
            key = (record["driver"], signature)
            assert key not in seen_signatures
            seen_signatures.add(key)
    registry = defects.load_registry(ROOT / "defects.json")
    assert len(registry) == len(seen_signatures)
