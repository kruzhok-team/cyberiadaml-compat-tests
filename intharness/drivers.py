# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The implementation driver subprocess interface
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
import subprocess

TIMEOUT = 30

CONVERTED = "converted"
REJECTED = "rejected"
ACCEPTED = "accepted"
CRASH = "crash"
TIMEOUT_OUTCOME = "timeout"


class Driver:
    """One implementation driver: an executable named drivers/<name>/driver."""

    def __init__(self, name, path):
        self.name = name
        self.path = pathlib.Path(path)
        self.info = None
        self.error = None

    @property
    def available(self):
        return self.info is not None

    def load_info(self):
        try:
            proc = subprocess.run([str(self.path), "info"],
                                  capture_output=True, text=True,
                                  timeout=TIMEOUT)
        except (OSError, subprocess.TimeoutExpired) as err:
            self.error = str(err)
            return
        if proc.returncode != 0:
            self.error = proc.stderr.strip() or "info exited %d" % \
                proc.returncode
            return
        try:
            self.info = json.loads(proc.stdout)
        except ValueError as err:
            self.error = "unparsable info output: %s" % err

    def convert(self, source, target):
        """Run one conversion; return (outcome, diagnostic)."""
        try:
            proc = subprocess.run([str(self.path), "convert",
                                   str(source), str(target)],
                                  capture_output=True, text=True,
                                  timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return TIMEOUT_OUTCOME, "no result within %d s" % TIMEOUT
        except OSError as err:
            return CRASH, str(err)
        diagnostic = proc.stderr.strip().splitlines()
        diagnostic = diagnostic[-1] if diagnostic else ""
        if proc.returncode == 0:
            if not pathlib.Path(target).is_file():
                return CRASH, "exit 0 but no output file"
            return CONVERTED, diagnostic
        if proc.returncode == 2:
            return REJECTED, diagnostic
        return CRASH, diagnostic or "exit %d" % proc.returncode


def discover(drivers_dir, names=None):
    """The Driver list for the drivers directory, info already probed."""
    drivers = []
    for entry in sorted(pathlib.Path(drivers_dir).iterdir()):
        if names is not None and entry.name not in names:
            continue
        executable = entry / "driver"
        if entry.is_dir() and executable.is_file():
            driver = Driver(entry.name, executable)
            driver.load_info()
            drivers.append(driver)
    return drivers
