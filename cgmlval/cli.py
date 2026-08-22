# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The validator command-line interface
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

import argparse
import json
import sys

from cgmlval import VERSION, rules
from cgmlval.requirements import REQUIREMENTS

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


def _read(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as err:
        print("cgmlval: %s" % err, file=sys.stderr)
        return None


def _cmd_validate(args):
    results = []
    code = EXIT_OK
    for path in args.files:
        data = _read(path)
        if data is None:
            return EXIT_USAGE
        ctx = rules.run_document(data, path)
        report = ctx.report
        if args.json:
            results.append(report.to_json(path, args.strict))
        else:
            for line in report.render_text(path):
                print(line)
            print("%s: %s" % (path, report.verdict(args.strict)))
        if not report.valid(args.strict):
            code = EXIT_FINDINGS
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return code


def _cmd_rules(args):
    rules.load_checks()
    entries = sorted(rules.REGISTRY.values(), key=lambda r: (r.layer, r.name))
    if args.json:
        out = []
        for r in entries:
            req = REQUIREMENTS.get(r.req)
            out.append({
                "rule": r.name,
                "req": r.req,
                "layer": r.layer,
                "severity": r.severity,
                "level": req.level if req else None,
                "profile": req.profile if req else None,
                "title": r.title,
                "note": r.note,
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return EXIT_OK
    for r in entries:
        req = REQUIREMENTS.get(r.req)
        print("%-20s %-18s L%d %-6s %-16s %-7s %s" % (
            r.name, r.req or "-", r.layer,
            req.level if req else "-",
            req.profile if req else "-",
            r.severity, r.title))
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cgmlval",
        description="CyberiadaML-GraphML 1.0 document validator")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser(
        "validate", help="validate documents through the layers L1-L4")
    p_validate.add_argument("files", nargs="+", metavar="FILE")
    p_validate.add_argument("--strict", action="store_true",
                            help="fail on warnings as well as errors")
    p_validate.add_argument("--json", action="store_true",
                            help="emit the reports as JSON")
    p_validate.set_defaults(func=_cmd_validate)

    p_rules = sub.add_parser("rules", help="list the registered checks")
    p_rules.add_argument("--json", action="store_true",
                         help="emit the rule list as JSON")
    p_rules.set_defaults(func=_cmd_rules)

    args = parser.parse_args(argv)
    return args.func(args)
