# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The L3 layer tests: attributes and values
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

from cgmlval import rules
from docbuilder import META_NODE, minimal


def run(data):
    return rules.run_document(data, "test.graphml")


def rule_names(ctx):
    return [f.rule for f in ctx.report.findings]


def errors(ctx):
    return [f.rule for f in ctx.report.findings if f.severity == "ERROR"]


def warnings(ctx):
    return [f.rule for f in ctx.report.findings if f.severity == "WARNING"]


def with_meta(body):
    meta = META_NODE.replace("standardVersion/ 1.0", body)
    return minimal().replace(META_NODE.encode(), meta.encode())


def test_minimal_document_clean_at_l3():
    ctx = run(minimal())
    assert ctx.report.findings == []
    assert 3 in ctx.report.layers_run


def test_wrong_gformat_value_rejected():
    doc = minimal().replace(b"Cyberiada-GraphML-1.0</data>",
                            b"Cyberiada-GraphML-2.0</data>")
    assert "gformat-value" in errors(run(doc))


def test_empty_gformat_value_rejected():
    doc = minimal().replace(b">Cyberiada-GraphML-1.0</data>", b"></data>")
    assert "gformat-value" in errors(run(doc))


def test_no_key_block_defaults_apply():
    ctx = run(minimal(keys=""))
    assert ctx.report.findings == []
    assert ctx.model.param("standardVersion") == "1.0"


def test_key_redeclared_differently_rejected():
    # dName redeclared for edges
    doc = minimal().replace(
        b'<key id="dName" for="graph" attr.name="name" attr.type="string"/>',
        b'<key id="dName" for="edge" attr.name="name" attr.type="string"/>')
    assert "key-declarations" in errors(run(doc))
    # dVertex redeclared with another attr.name
    doc = minimal().replace(
        b'<key id="dVertex" for="node" attr.name="vertex" attr.type="string"/>',
        b'<key id="dVertex" for="node" attr.name="vrtx" attr.type="string"/>')
    assert "key-declarations" in errors(run(doc))


def test_declared_custom_key_tolerated():
    doc = minimal().replace(
        b'  <graph id="G"',
        b'  <key id="dCustom" for="node" attr.name="custom" attr.type="string"/>\n'
        b'  <graph id="G"')
    doc = doc.replace(b'      <data key="dName">Idle</data>',
                      b'      <data key="dName">Idle</data>\n'
                      b'      <data key="dCustom">anything</data>')
    ctx = run(doc)
    assert ctx.report.findings == []


def test_undeclared_custom_key_rejected():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dCustom">anything</data>')
    assert "key-declarations" in errors(run(doc))


def test_data_without_key_rejected():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data>Idle</data>')
    assert "data-key-attr" in errors(run(doc))


def test_graph_without_id_rejected():
    doc = minimal().replace(b'<graph id="G" edgedefault="directed">',
                            b'<graph edgedefault="directed">')
    assert "element-ids" in errors(run(doc))


def test_undirected_graph_reported():
    doc = minimal().replace(b'edgedefault="directed"',
                            b'edgedefault="undirected"')
    ctx = run(doc)
    assert "edgedefault" in warnings(ctx)
    assert not ctx.report.has_errors()


def test_edge_attribute_variants_rejected():
    base = b'<edge id="init-n0#1" source="init" target="n0"/>'
    for repl, expected in (
            (b'<edge id="init-n0#1" target="n0"/>', "edge-endpoints"),
            (b'<edge id="init-n0#1" source="init"/>', "edge-endpoints"),
            (b'<edge source="init" target="n0"/>', "element-ids"),
            (b'<edge id="init-n0#1" source="" target="n0"/>',
             "edge-endpoints")):
        ctx = run(minimal().replace(base, repl))
        assert expected in errors(ctx)


def test_edge_id_template_informational():
    doc = minimal().replace(b'id="init-n0#1"', b'id="myedge"')
    ctx = run(doc)
    assert rule_names(ctx) == ["edge-id-template"]
    assert ctx.report.valid(strict=True)


def test_exotic_ids_accepted():
    doc = minimal() \
        .replace(b'id="init"', b'id="in-it_#!~"') \
        .replace(b'source="init"', b'source="in-it_#!~"')
    doc = doc.replace(b'id="n0"', b'id="n0::n1"') \
             .replace(b'target="n0"', b'target="n0::n1"')
    ctx = run(doc)
    assert errors(ctx) == []


def test_bad_id_characters_rejected():
    for bad in (b'id="a b"', b'id="a&quot;b"', b'id="a\\\\b"',
                'id="имя"'.encode()):
        doc = minimal().replace(b'<node id="n0">', b'<node %s>' % bad)
        ctx = run(doc)
        assert "id-charset" in errors(ctx), bad


def test_id_length_limits():
    long_ok = b"x" * 256
    ctx = run(minimal().replace(b'id="n0"', b'id="%s"' % long_ok)
              .replace(b'target="n0"', b'target="%s"' % long_ok))
    assert errors(ctx) == []
    too_long = b"x" * 257
    ctx = run(minimal().replace(b'id="n0"', b'id="%s"' % too_long)
              .replace(b'target="n0"', b'target="%s"' % too_long))
    assert "id-length" in errors(ctx)
    ctx = run(minimal().replace(b'<node id="n0">', b'<node id="">'))
    assert "id-length" in errors(ctx)


def test_case_sensitive_ids_coexist():
    doc = minimal().replace(b'<node id="n0">', b'<node id="N0">')
    doc = doc.replace(b'target="n0"', b'target="N0"')
    doc = doc.replace(b'</graph>',
                      b'  <node id="nn0"><data key="dName">Other</data></node>\n'
                      b'  </graph>')
    assert errors(run(doc)) == []


def test_statemachine_marker_with_value_rejected():
    doc = minimal().replace(b'<data key="dStateMachine"/>',
                            b'<data key="dStateMachine">yes</data>')
    assert "sm-marker-value" in errors(run(doc))


def test_vertex_value_banana_rejected():
    doc = minimal().replace(b'<data key="dVertex">initial</data>',
                            b'<data key="dVertex">banana</data>')
    assert "vertex-value" in errors(run(doc))


def test_reserved_vertex_reported():
    doc = minimal().replace(b'<data key="dVertex">initial</data>',
                            b'<data key="dVertex">fork</data>')
    ctx = run(doc)
    assert "vertex-reserved" in warnings(ctx)
    assert not ctx.report.has_errors()


def test_extension_vertexes_accepted():
    for kind in (b"final", b"choice", b"terminate", b"shallowHistory",
                 b"deepHistory", b"entryPoint", b"exitPoint"):
        doc = minimal().replace(b'<data key="dVertex">initial</data>',
                                b'<data key="dVertex">%s</data>' % kind)
        assert errors(run(doc)) == [], kind


def test_note_value_casual_rejected():
    doc = minimal().replace(b'<data key="dNote">formal</data>',
                            b'<data key="dNote">casual</data>')
    assert "note-value" in errors(run(doc))


def test_color_values():
    ok = (b'      <data key="dColor">#12AB34</data>',
          b'      <data key="dColor">#12AB34FF</data>',
          b'      <data key="dColor">red</data>')
    for color in ok:
        doc = minimal().replace(b'      <data key="dName">Idle</data>',
                                b'      <data key="dName">Idle</data>\n' + color)
        ctx = run(doc)
        assert warnings(ctx) == [], color
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dColor"></data>')
    assert "color-value" in warnings(run(doc))


def test_markup_on_state_reported():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dMarkup">markdown</data>')
    assert "markup-usage" in warnings(run(doc))


def test_formal_names():
    for name in (b"_x", b"Scan9", b"A_b_1"):
        doc = minimal().replace(b'      <data key="dName">Idle</data>',
                                b'      <data key="dName">Idle</data>\n'
                                b'      <data key="dFormalName">%s</data>' % name)
        assert errors(run(doc)) == [], name
    for name in (b"9x", b"a-b", "имя".encode(), b""):
        doc = minimal().replace(b'      <data key="dName">Idle</data>',
                                b'      <data key="dName">Idle</data>\n'
                                b'      <data key="dFormalName">%s</data>' % name)
        assert "formal-name-syntax" in errors(run(doc)), name


def test_behaviour_parse_error_rejected():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dData">EV\n[guard]</data>')
    ctx = run(doc)
    assert "behaviour-syntax" in errors(ctx)


def test_empty_event_name_node_block_accepted():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dData">/ act()</data>')
    assert errors(run(doc)) == []


def test_transition_label_without_separator_accepted():
    doc = minimal().replace(b'<edge id="init-n0#1" source="init" target="n0"/>',
                            b'<edge id="init-n0#1" source="init" target="n0">'
                            b'<data key="dData">EV\n[x &gt; 1]</data></edge>')
    ctx = run(doc)
    assert "behaviour-syntax" not in errors(ctx)


def test_node_event_without_behaviour_accepted():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dData">EV</data>')
    ctx = run(doc)
    assert "behaviour-syntax" not in errors(ctx)


def test_node_block_without_separator_rejected():
    doc = minimal().replace(b'      <data key="dName">Idle</data>',
                            b'      <data key="dName">Idle</data>\n'
                            b'      <data key="dData">EV\n[x &gt; 1]</data>')
    ctx = run(doc)
    assert "behaviour-syntax" in errors(ctx)


def test_meta_param_name_reported():
    ctx = run(with_meta("standardVersion/ 1.0\n\nимя/ значение"))
    assert "meta-params" in warnings(ctx)


def test_repeated_meta_param_reported():
    ctx = run(with_meta("standardVersion/ 1.0\n\nauthor/ A\n\nauthor/ B"))
    assert "meta-params" in warnings(ctx)


def test_standard_version_missing_rejected():
    ctx = run(with_meta("platform/ Arduino"))
    assert "standard-version" in errors(ctx)


def test_standard_version_wrong_rejected():
    ctx = run(with_meta("standardVersion/ 2.0"))
    assert "standard-version" in errors(ctx)


def test_geometry_mode_values():
    for mode in ("none", "short", "full"):
        ctx = run(with_meta("standardVersion/ 1.0\n\ngeometry/ " + mode))
        assert errors(ctx) == [], mode
    ctx = run(with_meta("standardVersion/ 1.0\n\ngeometry/ big"))
    assert "geometry-mode-value" in errors(ctx)


def test_transition_order_values():
    ctx = run(with_meta("standardVersion/ 1.0\n\ntransitionOrder/ exitFirst"))
    assert ctx.report.findings == []
    ctx = run(with_meta(
        "standardVersion/ 1.0\n\ntransitionOrder/ transitionFirst"))
    assert "transition-order-value" in warnings(ctx)


def test_event_propagation_values():
    ctx = run(with_meta("standardVersion/ 1.0\n\neventPropagation/ propagate"))
    assert ctx.report.findings == []
    ctx = run(with_meta("standardVersion/ 1.0\n\neventPropagation/ defer"))
    assert "event-propagation-value" in errors(ctx)


def test_created_at_informational():
    ctx = run(with_meta(
        "standardVersion/ 1.0\n\ncreatedAt/ 2024-04-24T10:20:30Z"))
    assert ctx.report.findings == []
    ctx = run(with_meta("standardVersion/ 1.0\n\ncreatedAt/ yesterday"))
    assert rule_names(ctx) == ["created-at"]
    assert ctx.report.valid(strict=True)


def test_text_and_custom_params_accepted():
    body = ("standardVersion/ 1.0\n\nplatform/ Arduino\n\nauthor/ A. N.\n\n"
            "description/ multi\nline\ntext\n\nmyParam/ custom value")
    ctx = run(with_meta(body))
    assert ctx.report.findings == []
    assert ctx.model.param("myParam") == "custom value"


def test_l3_errors_stop_the_pipeline():
    doc = minimal().replace(b"Cyberiada-GraphML-1.0</data>",
                            b"Cyberiada-GraphML-2.0</data>")
    ctx = run(doc)
    assert ctx.report.layers_run == [1, 2, 3]
    assert ctx.report.verdict() == "invalid"
