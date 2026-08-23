# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# Per-requirement verdicts from the channel results
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

import re

from cgmlval.requirements import REQUIREMENTS, VALIDATOR

PASS = "pass"
FAIL = "fail"
BLOCKED = "blocked"
NOT_CLAIMED = "not-claimed"
NOT_TESTED = "not-tested"
NOT_COVERED = "not-covered"

_ERROR_REQ = re.compile(r"^ERROR (CGML-[^:]+):")

# fail dominates; blocked keeps a requirement out of pass
_RANK = {FAIL: 3, BLOCKED: 2, PASS: 1}


class DriverVerdicts:
    """The per-requirement verdict table of one driver."""

    def __init__(self, profiles):
        self.profiles = profiles
        self.verdicts = {}
        self.reasons = {}
        self.tolerance = []   # not-claimed fixtures the library refused

    def _set(self, req, verdict, reason=None):
        if req not in REQUIREMENTS \
                or REQUIREMENTS[req].scope != VALIDATOR:
            return
        current = self.verdicts.get(req)
        if current is not None and _RANK.get(current, 0) >= \
                _RANK.get(verdict, 0):
            return
        self.verdicts[req] = verdict
        if reason:
            self.reasons[req] = reason

    def table(self):
        """Every validator requirement resolved to a verdict."""
        table = {}
        for req, entry in REQUIREMENTS.items():
            if entry.scope != VALIDATOR:
                table[req] = NOT_TESTED
            elif req in self.verdicts:
                table[req] = self.verdicts[req]
            elif entry.profile not in self.profiles:
                table[req] = NOT_CLAIMED
            else:
                table[req] = NOT_COVERED
        return table


def _cited(validate_errors):
    for line in validate_errors:
        match = _ERROR_REQ.match(line)
        if match:
            yield match.group(1)


def judge_driver(result, manifest, profiles):
    """Fold one driver's channel results into requirement verdicts."""
    verdicts = DriverVerdicts(profiles)
    for name, entry in result["positive"].items():
        meta = manifest[name]
        claimed = meta.get("profile", "CORE") in profiles
        reqs = meta.get("requirements", [])
        outcome = entry["outcome"]
        if outcome != "converted":
            reason = "%s: %s (%s)" % (name, outcome,
                                      entry.get("diagnostic", ""))
            if claimed:
                for req in reqs:
                    verdicts._set(req, FAIL, reason)
            else:
                verdicts.tolerance.append(reason)
            continue
        errors = entry.get("validate_errors", [])
        for req in _cited(errors):
            verdicts._set(req, FAIL,
                          "%s: invalid output (%s)" % (name, errors[0]))
        if errors:
            for req in reqs:
                verdicts._set(req, BLOCKED, "%s: output invalid" % name)
        elif not entry.get("dump_equal"):
            reason = "%s: %s" % (name, entry.get("dump_diff",
                                                 "dump differs"))
            for req in reqs:
                verdicts._set(req, FAIL, reason)
        else:
            for req in reqs:
                verdicts._set(req, PASS)
    for name, entry in result["negative"].items():
        req = manifest[name]["reject"]
        if entry["outcome"] == "rejected":
            verdicts._set(req, PASS)
        else:
            verdicts._set(req, FAIL, "%s: invalid document %s" %
                          (name, entry["outcome"]))
    return verdicts
