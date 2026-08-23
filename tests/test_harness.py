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
