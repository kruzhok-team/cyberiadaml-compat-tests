# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The harness driver-contract tests
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

import stat

from intharness import drivers as drv
from intharness.runner import _first_diff


def fake_driver(tmp_path, body):
    root = tmp_path / "fake"
    root.mkdir(parents=True, exist_ok=True)
    path = root / "driver"
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_info_success_and_failure(tmp_path):
    good = drv.Driver("good", fake_driver(
        tmp_path, 'echo \'{"name": "fake", "version": "1", '
                  '"profiles": ["CORE"]}\'\n'))
    good.load_info()
    assert good.available and good.info["name"] == "fake"
    bad = drv.Driver("bad", fake_driver(
        tmp_path / "sub", "echo broken >&2\nexit 1\n"))
    bad.load_info()
    assert not bad.available and "broken" in bad.error


def test_convert_outcomes(tmp_path):
    src = tmp_path / "in.graphml"
    src.write_text("<x/>")
    out = tmp_path / "out.graphml"
    copier = drv.Driver("ok", fake_driver(tmp_path, 'cp "$2" "$3"\n'))
    assert copier.convert(src, out)[0] == drv.CONVERTED
    rejecter = drv.Driver("no", fake_driver(
        tmp_path / "r", "echo nope >&2\nexit 2\n"))
    outcome, diagnostic = rejecter.convert(src, out)
    assert (outcome, diagnostic) == (drv.REJECTED, "nope")
    crasher = drv.Driver("cr", fake_driver(tmp_path / "c", "exit 9\n"))
    assert crasher.convert(src, out)[0] == drv.CRASH
    silent = drv.Driver("si", fake_driver(tmp_path / "s", "exit 0\n"))
    assert silent.convert(src, tmp_path / "missing.graphml")[0] == drv.CRASH


def test_first_diff():
    assert _first_diff("a\nb\n", "a\nb\n") is None
    assert "line 2" in _first_diff("a\nb\n", "a\nc\n")
    assert "length" in _first_diff("a\n", "a\nb\n")


def test_verdict_mapping():
    from intharness import verdicts as vmod
    manifest = {
        "core/F-A": {"profile": "CORE",
                     "requirements": ["CGML-5.4-2", "CGML-6.1-1"]},
        "ext/F-B": {"profile": "EXT-DISPLAY",
                    "requirements": ["CGML-9.2-1"]},
        "negative/X-1": {"reject": "CGML-5.9-4"},
    }
    result = {
        "positive": {
            "core/F-A": {"outcome": "converted", "validate_errors": [
                "ERROR CGML-appendix-B-1: bad key"], "dump_equal": False},
            "ext/F-B": {"outcome": "rejected", "diagnostic": "nope"},
        },
        "negative": {"X-1": None},
    }
    result["negative"] = {"negative/X-1": {"outcome": "accepted"}}
    verdicts = vmod.judge_driver(result, manifest, ["CORE"])
    table = verdicts.table()
    assert table["CGML-appendix-B-1"] == vmod.FAIL
    assert table["CGML-5.4-2"] == vmod.BLOCKED
    assert table["CGML-5.9-4"] == vmod.FAIL
    assert table["CGML-9.2-1"] == vmod.NOT_CLAIMED
    assert verdicts.tolerance and "ext/F-B" in verdicts.tolerance[0]
    assert table["CGML-6.2-1"] == vmod.NOT_TESTED
    assert table["CGML-5.1-1"] == vmod.NOT_COVERED


def test_crash_headline():
    dotnet = ("Unhandled exception. System.ArgumentOutOfRangeException: "
              "length ('-1') must be a non-negative value.\n"
              "   at System.Foo()\n   at Program.Main(String[] args)\n")
    assert drv._headline(dotnet, crashed=True).startswith(
        "Unhandled exception. System.ArgumentOutOfRangeException")
    python = ("Traceback (most recent call last):\n  File x, line 1\n"
              "ValueError: bad value\n")
    assert drv._headline(python, crashed=True) == "ValueError: bad value"
    assert drv._headline("first\nlast line\n", crashed=False) == "last line"
    assert drv._headline("", crashed=True) == ""
