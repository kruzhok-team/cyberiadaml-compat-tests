# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The document model built from an L2-clean element tree
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

from dataclasses import dataclass, field
from typing import Optional

from cgmlval import actions, meta

META_NAME = "CGML_META"
COMPONENT_NAME = "CGML_COMPONENT"

GEOMETRY_MODES = ("none", "short", "full")


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass
class KeyDecl:
    id: str
    for_kind: Optional[str]
    attr_name: Optional[str]
    attr_type: Optional[str]
    elem: object


@dataclass
class Node:
    id: Optional[str]
    elem: object
    name: Optional[str] = None
    formal_name: Optional[str] = None
    geometry: object = None
    color: Optional[str] = None


@dataclass
class State(Node):
    blocks: list = field(default_factory=list)
    block_errors: list = field(default_factory=list)
    data: Optional[str] = None
    regions: list = field(default_factory=list)
    collapsed: bool = False


@dataclass
class Vertex(Node):
    kind: Optional[str] = None


@dataclass
class Comment(Node):
    kind: Optional[str] = None       # informal | formal
    body: Optional[str] = None
    markup: Optional[str] = None


@dataclass
class SubmachineState(Node):
    ref: Optional[str] = None
    regions: list = field(default_factory=list)


@dataclass
class Region:
    id: Optional[str]
    elem: object
    name: Optional[str] = None
    formal_name: Optional[str] = None
    geometry: object = None
    children: list = field(default_factory=list)


@dataclass
class Transition:
    id: Optional[str]
    elem: object
    source: Optional[str] = None
    target: Optional[str] = None
    blocks: list = field(default_factory=list)
    block_errors: list = field(default_factory=list)
    data: Optional[str] = None
    polyline: list = field(default_factory=list)
    source_point: object = None
    target_point: object = None
    label_geometry: object = None
    color: Optional[str] = None


@dataclass
class CommentLink:
    id: Optional[str]
    elem: object
    source: Optional[str] = None
    target: Optional[str] = None
    pivot: Optional[str] = None
    chunk: Optional[str] = None


@dataclass
class StateMachine:
    id: Optional[str]
    elem: object
    name: Optional[str] = None
    formal_name: Optional[str] = None
    geometry: object = None
    marker: bool = False             # dStateMachine key present
    children: list = field(default_factory=list)
    transitions: list = field(default_factory=list)
    links: list = field(default_factory=list)


@dataclass
class Document:
    root: object
    format: Optional[str] = None
    format_elem: object = None
    keys: list = field(default_factory=list)
    machines: list = field(default_factory=list)
    meta_comment: object = None
    meta_params: list = field(default_factory=list)
    meta_errors: list = field(default_factory=list)
    geometry_mode: str = "none"

    def param(self, name):
        for par in self.meta_params:
            if par.name == name:
                return par.value
        return None

    def transition_order(self):
        return self.param("transitionOrder") or "actionFirst"

    def event_propagation(self):
        return self.param("eventPropagation") or "block"

    def markup_language(self):
        return self.param("markupLanguage") or "plain"


def data_items(elem):
    """The ordered (key, data element) pairs of a graph/node/edge."""
    return [(d.get("key"), d) for d in elem if d.tag == "data"]


def data_value(elem, key):
    """The text of the first data tag with the key; None when absent."""
    for name, data in data_items(elem):
        if name == key:
            return data.text or ""
    return None


def _data_elem(elem, key):
    for name, data in data_items(elem):
        if name == key:
            return data
    return None


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _geometry_object(child):
    if child.tag == "rect":
        return Rect(_number(child.get("x")), _number(child.get("y")),
                    _number(child.get("width")), _number(child.get("height")))
    if child.tag == "point":
        return Point(_number(child.get("x")), _number(child.get("y")))
    return None


def _geometry(elem, key="dGeometry"):
    data = _data_elem(elem, key)
    if data is None:
        return None
    for child in data:
        obj = _geometry_object(child)
        if obj is not None:
            return obj
    return None


def _points(elem, key):
    data = _data_elem(elem, key)
    if data is None:
        return []
    return [_geometry_object(c) for c in data if c.tag == "point"]


def _node_common(node):
    return {
        "id": node.get("id"),
        "elem": node,
        "name": data_value(node, "dName"),
        "formal_name": data_value(node, "dFormalName"),
        "geometry": _geometry(node),
        "color": data_value(node, "dColor"),
    }


def _build_region(graph):
    region = Region(graph.get("id"), graph,
                    name=data_value(graph, "dName"),
                    formal_name=data_value(graph, "dFormalName"),
                    geometry=_geometry(graph))
    region.children = [_build_node(n) for n in graph if n.tag == "node"]
    return region


def _build_node(node):
    keys = [k for k, _ in data_items(node)]
    regions = [_build_region(g) for g in node if g.tag == "graph"]
    if "dNote" in keys:
        return Comment(kind=data_value(node, "dNote"),
                       body=data_value(node, "dData"),
                       markup=data_value(node, "dMarkup"),
                       **_node_common(node))
    if "dVertex" in keys:
        return Vertex(kind=data_value(node, "dVertex"), **_node_common(node))
    if "dSubmachineState" in keys:
        return SubmachineState(ref=data_value(node, "dSubmachineState"),
                               regions=regions, **_node_common(node))
    text = data_value(node, "dData")
    blocks, errors = actions.parse(text)
    return State(blocks=blocks, block_errors=errors, data=text,
                 regions=regions,
                 collapsed=data_value(node, "dCollapsed") is not None,
                 **_node_common(node))


def _build_edge(edge):
    items = data_items(edge)
    common = {
        "id": edge.get("id"),
        "elem": edge,
        "source": edge.get("source"),
        "target": edge.get("target"),
    }
    if items and items[0][0] == "dPivot":
        return CommentLink(pivot=data_value(edge, "dPivot"),
                           chunk=data_value(edge, "dChunk"), **common)
    text = data_value(edge, "dData")
    blocks, errors = actions.parse(text)
    label = _geometry(edge, "dLabelGeometry")
    source_points = _points(edge, "dSourcePoint")
    target_points = _points(edge, "dTargetPoint")
    return Transition(blocks=blocks, block_errors=errors, data=text,
                      polyline=_points(edge, "dGeometry"),
                      source_point=source_points[0] if source_points else None,
                      target_point=target_points[0] if target_points else None,
                      label_geometry=label,
                      color=data_value(edge, "dColor"), **common)


def _build_machine(graph):
    machine = StateMachine(graph.get("id"), graph,
                           name=data_value(graph, "dName"),
                           formal_name=data_value(graph, "dFormalName"),
                           geometry=_geometry(graph),
                           marker=data_value(graph, "dStateMachine")
                           is not None)
    for child in graph:
        if child.tag == "node":
            machine.children.append(_build_node(child))
        elif child.tag == "edge":
            built = _build_edge(child)
            if isinstance(built, CommentLink):
                machine.links.append(built)
            else:
                machine.transitions.append(built)
    return machine


def _find_meta(document):
    if not document.machines:
        return
    first = document.machines[0]
    for child in first.children:
        if isinstance(child, Comment) and child.kind == "formal" \
                and child.name == META_NAME:
            document.meta_comment = child
            document.meta_params, document.meta_errors = \
                meta.parse(child.body)
            return


def build(parsed):
    """Build the document model from the parsed L2-clean tree."""
    root = parsed.root
    document = Document(root)
    for child in root:
        if child.tag == "data" and child.get("key") == "gFormat":
            if document.format_elem is None:
                document.format = child.text or ""
                document.format_elem = child
        elif child.tag == "key":
            document.keys.append(KeyDecl(child.get("id"), child.get("for"),
                                         child.get("attr.name"),
                                         child.get("attr.type"), child))
        elif child.tag == "graph":
            document.machines.append(_build_machine(child))
    _find_meta(document)
    mode = document.param("geometry")
    document.geometry_mode = mode if mode in GEOMETRY_MODES else "none"
    return document
