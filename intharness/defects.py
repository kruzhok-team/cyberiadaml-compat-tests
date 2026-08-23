# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# Defect clustering and the curated defect registry
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
import re

from cgmlval.requirements import REQUIREMENTS, MUST, SHOULD, MAY

WRITE = "write"
READ = "read"
ROBUSTNESS = "robustness"

_ERROR_REQ = re.compile(r"^ERROR (CGML-[^:]+):")
_DIFF = re.compile(r"^line \d+: expected (.*), got (.*)$")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
_SEVERITY = {MUST: "major", SHOULD: "minor", MAY: "info"}
_LEVEL_RANK = {MUST: 3, SHOULD: 2, MAY: 1}
_APPENDIX = {"A": "А", "B": "Б", "C": "В"}


def _normalize(line):
    return _NUMBER.sub("#", line.strip())


def clause(req):
    """The standard clause a requirement id belongs to."""
    part = req[len("CGML-"):]
    if part.startswith("appendix-"):
        letter = part.split("-")[1]
        return "appendix " + _APPENDIX.get(letter, letter)
    return "§" + part.split("-")[0]


def severity(requirements):
    """Record severity from the highest violated requirement level."""
    best = None
    for req in requirements:
        entry = REQUIREMENTS.get(req)
        if entry and (best is None or
                      _LEVEL_RANK[entry.level] > _LEVEL_RANK[best]):
            best = entry.level
    return _SEVERITY.get(best, "info")


def _add(clusters, signature, channel, kind, fixture, evidence,
         requirements, blocked=()):
    entry = clusters.setdefault(signature, {
        "signature": signature, "channel": channel, "kind": kind,
        "fixtures": [], "evidence_fixture": fixture,
        "evidence": list(evidence), "requirements": set(), "blocked": set()})
    if fixture not in entry["fixtures"]:
        entry["fixtures"].append(fixture)
    entry["requirements"].update(requirements)
    entry["blocked"].update(blocked)


def cluster_driver(result, manifest):
    """Cluster one driver's positive-channel findings by signature."""
    clusters = {}
    for name, entry in sorted(result["positive"].items()):
        reqs = manifest[name].get("requirements", [])
        outcome = entry["outcome"]
        diagnostic = entry.get("diagnostic", "")
        if outcome == "rejected":
            _add(clusters, "reject:" + diagnostic, "round-trip", READ,
                 name, [diagnostic], reqs)
        elif outcome != "converted":
            first = diagnostic.splitlines()[0] if diagnostic else outcome
            _add(clusters, "crash:" + first, "round-trip", ROBUSTNESS,
                 name, [diagnostic or outcome], reqs)
        else:
            errors = entry.get("validate_errors", [])
            if errors:
                groups = {}
                for line in errors:
                    match = _ERROR_REQ.match(line)
                    groups.setdefault(match.group(1) if match else "",
                                      []).append(line)
                for req, lines in sorted(groups.items()):
                    _add(clusters, "validate:" + (req or _normalize(lines[0])),
                         "validate-on-output", WRITE, name, lines,
                         [req] if req else [], reqs)
            elif not entry.get("dump_equal", False):
                diff = entry.get("dump_diff", "")
                match = _DIFF.match(diff)
                if match:
                    signature = "dump:%s|%s" % (_normalize(match.group(1)),
                                                _normalize(match.group(2)))
                else:
                    signature = "dump:" + _normalize(diff)
                _add(clusters, signature, "dump-equality", WRITE,
                     name, [diff], reqs)
    return clusters


def missing_rejections(result, manifest):
    """The invalid documents the driver failed to reject."""
    rows = []
    for name, entry in sorted(result["negative"].items()):
        if entry["outcome"] == "rejected":
            continue
        req = manifest[name]["reject"]
        rows.append({"fixture": name, "requirement": req,
                     "level": REQUIREMENTS[req].level,
                     "outcome": entry["outcome"]})
    return rows


def load_registry(path):
    """defects.json as a (driver, signature) -> record map."""
    registry = {}
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for record in data["defects"]:
        for signature in record["signatures"]:
            registry[(record["driver"], signature)] = record
    return registry


def _id_key(identifier):
    prefix, _, number = identifier.rpartition("-")
    return (prefix, int(number)) if number.isdigit() else (identifier, 0)


def _merge(record, cluster):
    record["signatures"].append(cluster["signature"])
    record["channels"].add(cluster["channel"])
    record["kinds"].add(cluster["kind"])
    for fixture in cluster["fixtures"]:
        if fixture not in record["fixtures"]:
            record["fixtures"].append(fixture)
    record["requirements"].update(cluster["requirements"])
    record["blocked"].update(cluster["blocked"])
    if record["evidence_fixture"] is None:
        record["evidence_fixture"] = cluster["evidence_fixture"]
        record["evidence"] = cluster["evidence"]


def _record(identifier, title, note, registered):
    return {"id": identifier, "title": title, "note": note,
            "registered": registered, "signatures": [], "channels": set(),
            "kinds": set(), "fixtures": [], "requirements": set(),
            "blocked": set(), "evidence_fixture": None, "evidence": []}


def assign(driver, clusters, registry):
    """Fold clusters into defect records; unmatched ones get provisional ids."""
    records = {}
    provisional = []
    for signature in sorted(clusters):
        cluster = clusters[signature]
        known = registry.get((driver, signature))
        if known:
            record = records.setdefault(
                known["id"], _record(known["id"], known["title"],
                                     known.get("note"), True))
            _merge(record, cluster)
        else:
            provisional.append(cluster)
    result = sorted(records.values(), key=lambda r: _id_key(r["id"]))
    for index, cluster in enumerate(provisional, 1):
        title = cluster["evidence"][0].strip() if cluster["evidence"] \
            else cluster["signature"]
        record = _record("%s-NEW-%d" % (driver.upper(), index),
                         title[:70], None, False)
        _merge(record, cluster)
        result.append(record)
    for record in result:
        record["fixtures"].sort()
        record["severity"] = severity(record["requirements"])
    return result
