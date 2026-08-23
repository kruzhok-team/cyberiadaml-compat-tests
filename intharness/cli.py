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

    args = parser.parse_args(argv)
    return args.func(args)
