# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The conformance report renderers: summary and per-library defect reports
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

from collections import Counter

from cgmlval.requirements import REQUIREMENTS
from intharness import defects as defects_mod
from intharness import verdicts as verdicts_mod

ORDER = ("pass", "fail", "blocked", "not-claimed", "not-covered",
         "not-tested")
_MAX_REQ_LIST = 6


def _profiles(table):
    """verdict counters grouped by requirement profile."""
    grouped = {}
    for req, verdict in table.items():
        grouped.setdefault(REQUIREMENTS[req].profile,
                           Counter())[verdict] += 1
    return grouped


def _interop_cell(cell):
    if not cell:
        return "-"
    ok = sum(1 for value in cell.values() if value == "ok")
    return "%d/%d" % (ok, len(cell))


def _defect_index(records):
    """requirement -> defect id; direct violations before blocked fallbacks."""
    index = {}
    for record in records:
        for req in record["requirements"]:
            index.setdefault(req, record["id"])
    for record in records:
        for req in record["blocked"]:
            index.setdefault(req, record["id"])
    return index


def _severity_summary(records):
    counts = Counter(record["severity"] for record in records)
    parts = ["%d %s" % (counts[s], s) for s in ("major", "minor", "info")
             if counts[s]]
    return "%d defect%s (%s)" % (len(records),
                                 "" if len(records) == 1 else "s",
                                 ", ".join(parts) or "none")


def _title(record):
    if record["registered"]:
        return record["title"]
    return record["title"] + " *(unregistered — add to defects.json)*"


def _violates(record):
    reqs = sorted(record["requirements"])
    if not reqs:
        return "—"
    if len(reqs) > _MAX_REQ_LIST:
        known = [r for r in reqs if r in REQUIREMENTS]
        level = max(known, default=None,
                    key=lambda r: defects_mod._LEVEL_RANK[
                        REQUIREMENTS[r].level])
        return "%d requirements of the affected fixtures (highest level " \
            "%s)" % (len(reqs),
                     REQUIREMENTS[level].level if level else "?")
    parts = []
    for req in reqs:
        entry = REQUIREMENTS.get(req)
        if entry:
            parts.append("`%s` (%s, %s, %s)" %
                         (req, entry.level, entry.profile,
                          defects_mod.clause(req)))
        else:
            parts.append("`%s`" % req)
    return "; ".join(parts)


def _impact(record, total_positive):
    kinds = record["kinds"]
    if defects_mod.ROBUSTNESS in kinds:
        return "the driver crashes on %d fixture(s)" % len(record["fixtures"])
    if defects_mod.READ in kinds:
        return "the driver cannot read %d of %d positive fixtures" % \
            (len(record["fixtures"]), total_positive)
    if record["blocked"]:
        return "affected outputs are invalid; %d fixture requirement(s) " \
            "blocked" % len(record["blocked"])
    return "round-trip loses fidelity on %d fixture(s)" % \
        len(record["fixtures"])


def _fixture_list(fixtures, total):
    listed = ", ".join("`%s`" % f for f in fixtures[:_MAX_REQ_LIST])
    if len(fixtures) > _MAX_REQ_LIST:
        listed += ", …"
    return "%d of %d: %s" % (len(fixtures), total, listed)


def _reproduce(driver, record):
    fixture = record["evidence_fixture"]
    convert = "drivers/%s/driver convert fixtures/%s.graphml out.graphml" % \
        (driver, fixture)
    channel = record["evidence_channel"]
    if channel == "round-trip":
        if defects_mod.ROBUSTNESS in record["kinds"]:
            return [convert + "   # crashes"]
        return [convert + "   # exits 2 (rejected)"]
    if channel == "validate-on-output":
        return [convert, "python3 -m cgmlval validate out.graphml"]
    return [convert,
            "python3 -m cgmlval dump out.graphml | "
            "diff fixtures/%s.expected.txt -" % fixture]


def _render_record(driver, record, total_positive):
    lines = ["## %s — %s" % (record["id"], _title(record)), ""]
    lines.append("| | |")
    lines.append("|---|---|")
    lines.append("| kind | %s |" % ", ".join(sorted(record["kinds"])))
    lines.append("| severity | %s |" % record["severity"])
    lines.append("| channel | %s |" % ", ".join(sorted(record["channels"])))
    lines.append("| violates | %s |" % _violates(record))
    lines.append("| fixtures | %s |" %
                 _fixture_list(record["fixtures"], total_positive))
    lines.append("| impact | %s |" % _impact(record, total_positive))
    lines.append("")
    if record["note"]:
        lines.append("Note: %s" % record["note"])
        lines.append("")
    lines.append("Evidence (`%s`):" % record["evidence_fixture"])
    lines.append("")
    for evidence in record["evidence"]:
        for part in evidence.splitlines() or [""]:
            lines.append("    " + part)
    lines.append("")
    lines.append("Reproduce:")
    lines.append("")
    for command in _reproduce(driver, record):
        lines.append("    " + command)
    lines.append("")
    return lines


def render_driver(driver, info, records, missing, tolerance, date,
                  corpus_rev, total_positive):
    """Render the defect report of one library; return the text."""
    lines = ["# %s %s — defect report" % (info.get("name"),
                                          info.get("version")), ""]
    lines.append("Generated %s from fixture corpus revision `%s`; standard "
                 "PNST 1044-2025; the library claims %s." %
                 (date, corpus_rev, ", ".join(info.get("profiles", []))))
    lines.append("Summary: %s. Verdict counts per requirement are in "
                 "`REPORT.md`." % _severity_summary(records))
    lines.append("")
    for record in records:
        lines.extend(_render_record(driver, record, total_positive))
    lines.append("## Missing rejections")
    lines.append("")
    if missing:
        lines.append("Invalid documents the library accepted (`crash` rows "
                     "crashed instead of rejecting):")
        lines.append("")
        lines.append("| fixture | requirement | level | outcome |")
        lines.append("|---|---|---|---|")
        for row in missing:
            lines.append("| `%s` | `%s` | %s | %s |" %
                         (row["fixture"], row["requirement"], row["level"],
                          row["outcome"]))
    else:
        lines.append("None — every negative fixture was rejected.")
    lines.append("")
    if tolerance:
        lines.append("## Tolerance notes (unclaimed profiles)")
        lines.append("")
        lines.append("Fixtures of unclaimed profiles the library refused "
                     "(spec §2.1 tolerance):")
        lines.append("")
        for reason in tolerance:
            lines.append("- %s" % reason)
        lines.append("")
    return "\n".join(lines) + "\n"


def render_summary(report, judged, defect_records, date, corpus_rev):
    """Render REPORT.md; return the text."""
    lines = ["# CyberiadaML-GraphML 1.0 — Library Conformance Report", ""]
    lines.append("Generated %s from fixture corpus revision `%s` by the "
                 "intharness runner" % (date, corpus_rev))
    lines.append("(see `CyberiadaML-GraphML-1.0-HARNESS-SPEC.md` for the "
                 "channel, verdict and defect semantics).")
    lines.append("")
    lines.append("## Implementations")
    lines.append("")
    for name, entry in sorted(report["drivers"].items()):
        if entry["available"]:
            info = entry["info"]
            lines.append("- **%s** — %s %s, claims %s: %s, "
                         "defect report [`%s.md`](%s.md)" %
                         (name, info.get("name"), info.get("version"),
                          ", ".join(info.get("profiles", [])),
                          _severity_summary(defect_records.get(name, [])),
                          name, name))
        else:
            lines.append("- **%s** — unavailable: %s" %
                         (name, entry.get("error")))
    lines.append("")

    lines.append("## Requirement scoreboard")
    lines.append("")
    lines.append("| Library | Profile | " + " | ".join(ORDER) + " |")
    lines.append("|---|---|" + "---|" * len(ORDER))
    for name, verdicts in judged.items():
        for profile, counts in sorted(_profiles(verdicts.table()).items()):
            lines.append("| %s | %s | " % (name, profile) +
                         " | ".join(str(counts.get(v, 0)) for v in ORDER) +
                         " |")
    lines.append("")

    lines.append("## Failed requirements")
    lines.append("")
    lines.append("Each failure names the defect record explaining it "
                 "(`<library>.md`).")
    lines.append("")
    for name, verdicts in judged.items():
        index = _defect_index(defect_records.get(name, []))
        failed = sorted(req for req, verdict in verdicts.verdicts.items()
                        if verdict == verdicts_mod.FAIL)
        lines.append("### %s" % name)
        lines.append("")
        if not failed:
            lines.append("No failed requirements.")
        for req in failed:
            reason = verdicts.reasons.get(req, "")
            if "invalid document" in reason:
                lines.append("- `%s` — missing rejection (`%s`)" %
                             (req, reason.split(":", 1)[0]))
            elif req in index:
                lines.append("- `%s` — %s" % (req, index[req]))
            else:
                lines.append("- `%s` — %s" % (req, reason))
        lines.append("")

    lines.append("## Interoperability matrix")
    lines.append("")
    lines.append("Cell: positive fixtures exchanged cleanly "
                 "(writer → reader → canonical dump equals the golden "
                 "dump) / total.")
    lines.append("")
    names = sorted(report["results"])
    lines.append("| writer \\ reader | " + " | ".join(names) + " |")
    lines.append("|---|" + "---|" * len(names))
    for writer in names:
        row = ["| %s |" % writer]
        for reader in names:
            if reader == writer:
                row.append(" — |")
            else:
                cell = report["interop"].get("%s->%s" % (writer, reader), {})
                row.append(" %s |" % _interop_cell(cell))
        lines.append("".join(row))
    lines.append("")
    return "\n".join(lines) + "\n"


def render_all(report, manifest, registry, date, corpus_rev):
    """Render every report file; return a {filename: text} map."""
    total_positive = sum(1 for entry in manifest.values()
                         if "reject" not in entry)
    judged = {}
    defect_records = {}
    files = {}
    for name, result in sorted(report["results"].items()):
        info = report["drivers"][name]["info"]
        profiles = info.get("profiles", [])
        judged[name] = verdicts_mod.judge_driver(result, manifest, profiles)
        clusters = defects_mod.cluster_driver(result, manifest)
        records = defects_mod.assign(name, clusters, registry)
        defect_records[name] = records
        files[name + ".md"] = render_driver(
            name, info, records,
            defects_mod.missing_rejections(result, manifest),
            judged[name].tolerance, date, corpus_rev, total_positive)
    files["REPORT.md"] = render_summary(report, judged, defect_records,
                                        date, corpus_rev)
    return files
