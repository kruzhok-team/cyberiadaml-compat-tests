# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The appendix B key inventory and the standard value enumerations
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

# (key id, for) -> attr.name, per the appendix B table of the standard
STANDARD_BINDINGS = {
    ("gFormat", "graphml"): "format",
    ("dName", "graph"): "name",
    ("dName", "node"): "name",
    ("dStateMachine", "graph"): "stateMachine",
    ("dRegion", "graph"): "region",
    ("dSubmachineState", "node"): "submachineState",
    ("dGeometry", "graph"): "geometry",
    ("dGeometry", "node"): "geometry",
    ("dGeometry", "edge"): "geometry",
    ("dSourcePoint", "edge"): "sourcePoint",
    ("dTargetPoint", "edge"): "targetPoint",
    ("dLabelGeometry", "edge"): "labelGeometry",
    ("dNote", "node"): "note",
    ("dVertex", "node"): "vertex",
    ("dData", "node"): "data",
    ("dData", "edge"): "data",
    ("dPivot", "edge"): "pivot",
    ("dChunk", "edge"): "chunk",
    ("dCollapsed", "node"): "collapsed",
    ("dMarkup", "node"): "markup",
    ("dColor", "node"): "color",
    ("dColor", "edge"): "color",
    ("dFormalName", "graph"): "formalName",
    ("dFormalName", "node"): "formalName",
}

STANDARD_KEY_IDS = frozenset(key for key, _ in STANDARD_BINDINGS)

VERTEX_CORE = ("initial", "final", "choice", "terminate")
VERTEX_EXT = ("shallowHistory", "deepHistory", "entryPoint", "exitPoint")
VERTEX_RESERVED = ("fork", "join")

NOTE_KINDS = ("informal", "formal")

GEOMETRY_MODES = ("none", "short", "full")
TRANSITION_ORDERS = ("actionFirst", "exitFirst")
EVENT_PROPAGATIONS = ("block", "propagate")
