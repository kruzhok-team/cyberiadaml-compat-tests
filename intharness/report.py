# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The conformance report renderer
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
from intharness import verdicts as verdicts_mod

ORDER = ("pass", "fail", "blocked", "not-claimed", "not-covered",
         "not-tested")


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


def render(report, manifest, date, corpus_rev):
    """Render REPORT.md from the run data; return the text."""
    lines = ["# CyberiadaML-GraphML 1.0 — Library Conformance Report", ""]
    lines.append("Generated %s from fixture corpus revision `%s` by the "
                 "intharness runner" % (date, corpus_rev))
    lines.append("(see `CyberiadaML-GraphML-1.0-HARNESS-SPEC.md` for the "
                 "channel and verdict semantics).")
    lines.append("")
    lines.append("## Implementations")
    lines.append("")
    for name, entry in sorted(report["drivers"].items()):
        if entry["available"]:
            info = entry["info"]
            lines.append("- **%s** — %s %s, claims %s" %
                         (name, info.get("name"), info.get("version"),
                          ", ".join(info.get("profiles", []))))
        else:
            lines.append("- **%s** — unavailable: %s" %
                         (name, entry.get("error")))
    lines.append("")

    judged = {}
    for name, result in sorted(report["results"].items()):
        profiles = report["drivers"][name]["info"].get("profiles", [])
        judged[name] = verdicts_mod.judge_driver(result, manifest, profiles)

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
    for name, verdicts in judged.items():
        failed = sorted(req for req, verdict in verdicts.verdicts.items()
                        if verdict == verdicts_mod.FAIL)
        lines.append("### %s" % name)
        lines.append("")
        if not failed:
            lines.append("No failed requirements.")
        for req in failed:
            lines.append("- `%s` — %s" %
                         (req, verdicts.reasons.get(req, "")))
        lines.append("")
        if verdicts.tolerance:
            lines.append("Tolerance deviations (unclaimed-profile fixtures "
                         "refused, spec §2.1):")
            for reason in verdicts.tolerance:
                lines.append("- %s" % reason)
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

    lines.append("## Finding appendix")
    lines.append("")
    for name, result in sorted(report["results"].items()):
        lines.append("### %s" % name)
        lines.append("")
        for fixture, entry in sorted(result["positive"].items()):
            notes = []
            if entry["outcome"] != "converted":
                notes.append("%s (%s)" % (entry["outcome"],
                                          entry.get("diagnostic", "")))
            else:
                notes.extend(entry.get("validate_errors", []))
                if entry.get("dump_diff"):
                    notes.append("dump: %s" % entry["dump_diff"])
            if notes:
                lines.append("- `%s`: %s" % (fixture, "; ".join(notes)))
        accepted = [f for f, e in sorted(result["negative"].items())
                    if e["outcome"] != "rejected"]
        if accepted:
            lines.append("- invalid documents not rejected: " +
                         ", ".join("`%s`" % f for f in accepted))
        lines.append("")
    return "\n".join(lines) + "\n"
