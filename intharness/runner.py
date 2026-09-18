# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The compatibility matrix runner: the five judgement channels
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

from cgmlval import dump as dump_mod
from cgmlval import rules
from intharness import drivers as drv


def _judge(path):
    """Validate one produced document; return (error lines, dump or None)."""
    data = pathlib.Path(path).read_bytes()
    ctx = rules.run_document(data, str(path))
    errors = ["%s %s: %s" % (f.severity, f.req or f.rule, f.message)
              for f in ctx.report.findings if f.severity == "ERROR"]
    text = None
    if not ctx.report.has_errors() and ctx.model is not None:
        text = dump_mod.render(ctx.model)
    return errors, text


# a rect whose size the fixture leaves unset in short geometry mode (7.2-3):
# the writer may reconstruct any size at the same origin
_LOOSE_RECT = re.compile(r"^(\s*[a-z-]+: rect -?[0-9.]+ -?[0-9.]+) 0\.00 0\.00$")
_ANY_RECT = re.compile(r"^(\s*[a-z-]+: rect -?[0-9.]+ -?[0-9.]+) -?[0-9.]+ -?[0-9.]+$")


def _same_loose_rect(exp, act):
    loose, any_ = _LOOSE_RECT.match(exp), _ANY_RECT.match(act)
    return bool(loose and any_ and loose.group(1) == any_.group(1))


def _first_diff(expected, got):
    exp_lines = expected.splitlines()
    got_lines = got.splitlines()
    short = "geometry-mode: short" in exp_lines
    for index, (exp, act) in enumerate(zip(exp_lines, got_lines), 1):
        if exp != act and not (short and _same_loose_rect(exp, act)):
            return "line %d: expected %r, got %r" % (index, exp, act)
    if len(exp_lines) != len(got_lines):
        return "line %d: the dumps differ in length" % \
            (min(len(exp_lines), len(got_lines)) + 1)
    return None


class Corpus:

    def __init__(self, fixtures_dir):
        self.root = pathlib.Path(fixtures_dir)
        manifest = json.loads((self.root / "manifest.json")
                              .read_text(encoding="utf-8"))
        self.entries = manifest["fixtures"]
        self.twins = manifest["twins"]
        self.positive = sorted(n for n, e in self.entries.items()
                               if "reject" not in e)
        self.negative = sorted(n for n, e in self.entries.items()
                               if "reject" in e)

    def document(self, name):
        return self.root / (name + ".graphml")

    def golden(self, name):
        return (self.root / (name + ".expected.txt")) \
            .read_text(encoding="utf-8")


def _run_positive(driver, corpus, workdir, log):
    results = {}
    outputs = {}
    for name in corpus.positive:
        target = workdir / driver.name / (name + ".graphml")
        target.parent.mkdir(parents=True, exist_ok=True)
        outcome, diagnostic = driver.convert(corpus.document(name), target)
        entry = {"outcome": outcome}
        if diagnostic:
            entry["diagnostic"] = diagnostic
        if outcome == drv.CONVERTED:
            outputs[name] = target
            errors, text = _judge(target)
            entry["validate_errors"] = errors
            if text is None:
                entry["dump_equal"] = False
            else:
                diff = _first_diff(corpus.golden(name), text)
                entry["dump_equal"] = diff is None
                if diff:
                    entry["dump_diff"] = diff
        results[name] = entry
        log("  %s %s: %s" % (driver.name, name, outcome))
    return results, outputs


def _run_negative(driver, corpus, workdir, log):
    results = {}
    for name in corpus.negative:
        target = workdir / driver.name / (name + ".graphml")
        target.parent.mkdir(parents=True, exist_ok=True)
        outcome, diagnostic = driver.convert(corpus.document(name), target)
        if outcome == drv.CONVERTED:
            outcome = drv.ACCEPTED
        entry = {"outcome": outcome}
        if diagnostic:
            entry["diagnostic"] = diagnostic
        results[name] = entry
        log("  %s %s: %s" % (driver.name, name, outcome))
    return results


def _run_twins(driver, corpus, outputs):
    results = []
    for first, second in corpus.twins:
        entry = {"pair": [first, second]}
        if first not in outputs or second not in outputs:
            entry["outcome"] = "skipped"
        else:
            _, text_a = _judge(outputs[first])
            _, text_b = _judge(outputs[second])
            if text_a is None or text_b is None:
                entry["outcome"] = "invalid-output"
            elif text_a == text_b:
                entry["outcome"] = "equal"
            else:
                entry["outcome"] = "different"
                entry["diff"] = _first_diff(text_a, text_b)
        results.append(entry)
    return results


def _run_interop(writers, readers, corpus, outputs, workdir, log):
    matrix = {}
    for writer in writers:
        for reader in readers:
            if reader.name == writer.name:
                continue
            cell = {}
            for name in corpus.positive:
                source = outputs.get(writer.name, {}).get(name)
                if source is None:
                    cell[name] = "skipped"
                    continue
                target = workdir / ("%s-%s" % (writer.name, reader.name)) / \
                    (name + ".graphml")
                target.parent.mkdir(parents=True, exist_ok=True)
                outcome, _ = reader.convert(source, target)
                if outcome != drv.CONVERTED:
                    cell[name] = outcome
                    continue
                errors, text = _judge(target)
                if errors or text is None:
                    cell[name] = "invalid-output"
                elif _first_diff(corpus.golden(name), text) is None:
                    cell[name] = "ok"
                else:
                    cell[name] = "dump-diff"
            key = "%s->%s" % (writer.name, reader.name)
            matrix[key] = cell
            log("  interop %s: %d/%d ok" %
                (key, sum(1 for v in cell.values() if v == "ok"), len(cell)))
    return matrix


def run(fixtures_dir, drivers_dir, workdir, names=None, log=lambda line: None):
    """Run all channels; return the report data structure."""
    corpus = Corpus(fixtures_dir)
    workdir = pathlib.Path(workdir)
    report = {"corpus": str(fixtures_dir), "drivers": {}, "results": {},
              "interop": {}}
    fleet = drv.discover(drivers_dir, names)
    outputs = {}
    for driver in fleet:
        report["drivers"][driver.name] = {
            "available": driver.available,
            "info": driver.info, "error": driver.error}
        if not driver.available:
            log("driver %s unavailable: %s" % (driver.name, driver.error))
            continue
        log("driver %s (%s %s)" % (driver.name, driver.info.get("name"),
                                   driver.info.get("version")))
        positive, produced = _run_positive(driver, corpus, workdir, log)
        outputs[driver.name] = produced
        report["results"][driver.name] = {
            "positive": positive,
            "negative": _run_negative(driver, corpus, workdir, log),
            "twins": _run_twins(driver, corpus, produced),
        }
    active = [d for d in fleet if d.available]
    report["interop"] = _run_interop(active, active, corpus, outputs,
                                     workdir, log)
    return report
