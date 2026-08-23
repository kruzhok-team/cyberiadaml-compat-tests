# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The harness command-line interface
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
import pathlib
import sys
import tempfile

from intharness import VERSION, runner

ROOT = pathlib.Path(__file__).parent.parent


def _cmd_run(args):
    workdir = args.workdir or tempfile.mkdtemp(prefix="intharness-")
    report = runner.run(args.fixtures, args.drivers_dir, workdir,
                        names=args.driver or None,
                        log=lambda line: print(line, file=sys.stderr))
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print("report written to %s" % out)
    return 0


def _cmd_report(args):
    import datetime
    import subprocess
    from intharness import defects as defects_mod
    from intharness import report as report_mod
    data = json.loads(pathlib.Path(args.infile).read_text(encoding="utf-8"))
    manifest = json.loads(
        (pathlib.Path(args.fixtures) / "manifest.json")
        .read_text(encoding="utf-8"))["fixtures"]
    registry = defects_mod.load_registry(args.registry)
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True,
                             cwd=ROOT).stdout.strip() or "unknown"
    except OSError:
        rev = "unknown"
    files = report_mod.render_all(
        data, manifest, registry,
        args.date or datetime.date.today().isoformat(), rev)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(files):
        (out_dir / name).write_text(files[name], encoding="utf-8")
        print("rendered %s" % (out_dir / name))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="intharness",
        description="CyberiadaML-GraphML 1.0 library compatibility harness")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run the compatibility matrix")
    p_run.add_argument("--fixtures", default=str(ROOT / "fixtures"))
    p_run.add_argument("--drivers-dir", default=str(ROOT / "drivers"))
    p_run.add_argument("--driver", action="append", metavar="NAME",
                       help="restrict the run to the named drivers")
    p_run.add_argument("--workdir", help="keep converted files here")
    p_run.add_argument("--out", default="report.json")
    p_run.set_defaults(func=_cmd_run)

    p_report = sub.add_parser(
        "report", help="render the summary and per-library defect reports")
    p_report.add_argument("--in", dest="infile", default="report.json")
    p_report.add_argument("--fixtures", default=str(ROOT / "fixtures"))
    p_report.add_argument("--registry", default=str(ROOT / "defects.json"))
    p_report.add_argument("--date", help="override the report date stamp")
    p_report.add_argument("--out-dir", default="reports")
    p_report.set_defaults(func=_cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)
