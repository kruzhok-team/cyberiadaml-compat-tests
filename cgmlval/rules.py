# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The validation rule registry and the layer runner
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

from dataclasses import dataclass
from typing import Callable, Optional

from cgmlval.findings import Finding, Report
from cgmlval.requirements import REQUIREMENTS


@dataclass
class Rule:
    name: str
    req: Optional[str]
    layer: int
    severity: str
    title: str
    func: Optional[Callable] = None
    note: Optional[str] = None


REGISTRY = {}


def _register(rule_obj):
    if rule_obj.name in REGISTRY:
        raise ValueError("duplicate rule name: %s" % rule_obj.name)
    if rule_obj.req is not None and rule_obj.req not in REQUIREMENTS:
        raise ValueError("unknown requirement: %s" % rule_obj.req)
    REGISTRY[rule_obj.name] = rule_obj


def rule(name, req, layer, severity, title):
    """Register a callable check; the callable receives the layer context."""
    def decorator(func):
        _register(Rule(name, req, layer, severity, title, func))
        return func
    return decorator


def declare(name, req, layer, severity, title, note=None):
    """Register a rule emitted by a walker or the parser, without a callable."""
    _register(Rule(name, req, layer, severity, title, None, note))


class Context:
    """The state passed to the checks of one validation layer."""

    def __init__(self, report, filename):
        self.report = report
        self.filename = filename
        self.layer = 0
        self.parsed = None   # xmlload.ParsedDocument after L1
        self.model = None    # model.Document after the model build

    def emit(self, name, message, elem=None, line=None, column=None, path=None):
        rule_obj = REGISTRY[name]
        if elem is not None and self.parsed is not None:
            info = self.parsed.info.get(id(elem))
            if info is not None:
                line = info[0] if line is None else line
                column = info[1] if column is None else column
                path = info[2] if path is None else path
        self.report.add(Finding(name, rule_obj.req, rule_obj.layer,
                                rule_obj.severity, message, line, column, path))


def load_checks():
    """Import the check modules so that their rules register."""
    from cgmlval import xmlload  # noqa: F401


def run_layer(ctx, layer):
    ctx.layer = layer
    for rule_obj in REGISTRY.values():
        if rule_obj.layer == layer and rule_obj.func is not None:
            rule_obj.func(ctx)
    ctx.report.layers_run.append(layer)


def run_document(data, filename="<data>"):
    """Run the validation layers over the document bytes; return the context."""
    from cgmlval import xmlload

    load_checks()
    ctx = Context(Report(), filename)
    ctx.layer = 1
    ctx.parsed = xmlload.load(data, ctx)
    ctx.report.layers_run.append(1)
    if ctx.report.has_errors(layer=1) or ctx.parsed is None:
        return ctx
    return ctx
