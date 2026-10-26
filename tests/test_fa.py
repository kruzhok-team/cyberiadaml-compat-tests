# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The EXT-FA rule tests: finite automaton documents
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

FA_META = META_NODE.replace("standardVersion/ 1.0",
                            "standardVersion/ 1.0\n\ntype/ fa")

HEAD = """\
  <graph id="G" edgedefault="directed">
    <data key="dStateMachine"/>
    <data key="dName">Automaton</data>
"""

NODES = """\
    <node id="init">
      <data key="dVertex">initial</data>
    </node>
    <node id="q0">
      <data key="dName">q0</data>
    </node>
    <node id="q1">
      <data key="dName">q1</data>
      <data key="dData">entry/
1</data>
    </node>
    <node id="fin">
      <data key="dVertex">final</data>
    </node>
"""

EDGES = """\
    <edge id="init-q0" source="init" target="q0"/>
    <edge id="q0-q1" source="q0" target="q1">
      <data key="dData">a/
0</data>
    </edge>
    <edge id="q1-q1" source="q1" target="q1">
      <data key="dData">b/</data>
    </edge>
    <edge id="q1-fin" source="q1" target="fin">
      <data key="dData">EOF/</data>
    </edge>
"""

COMPOSITE = """\
    <node id="c0">
      <data key="dName">C</data>
      <graph id="c0:" edgedefault="directed">
        <data key="dRegion"/>
%s\
        <node id="c1">
          <data key="dName">c1</data>
        </node>
      </graph>
    </node>
"""

INNER_INITIAL = """\
        <node id="c0init">
          <data key="dVertex">initial</data>
        </node>
"""

# edges sit in the state machine graph (CGML-6.5-3), the region holds nodes
INNER_EDGE = '    <edge id="c0init-c1" source="c0init" target="c1"/>\n'
NESTED = NODES + COMPOSITE % INNER_INITIAL

SECOND_MACHINE = """\
  <graph id="G2" edgedefault="directed">
    <data key="dStateMachine"/>
    <data key="dName">Second</data>
    <node id="g2n0">
      <data key="dName">Idle</data>
    </node>
  </graph>
"""


def comment(name, body, ident="alpha", kind="formal"):
    return ('    <node id="%s">\n      <data key="dNote">%s</data>\n'
            '      <data key="dName">%s</data>\n'
            '      <data key="dData">%s</data>\n    </node>\n' %
            (ident, kind, name, body))


def fa(nodes=NODES, edges=EDGES, meta=FA_META, extra=""):
    machine = HEAD + meta + nodes + edges + "  </graph>\n" + extra
    return minimal(keys="", machines=machine)


def run(data):
    return rules.run_document(data, "test.graphml")


def errors(ctx):
    return [f.rule for f in ctx.report.findings if f.severity == "ERROR"]


def fa_errors(ctx):
    return [name for name in errors(ctx) if name.startswith("fa-")]


def test_fa_document_clean():
    ctx = run(fa())
    assert ctx.report.findings == []
    assert ctx.model.is_fa


def test_fa_rules_silent_without_type_fa():
    edges = EDGES.replace("a/\n0", "a [x] propagate/\n0\n1")
    ctx = run(fa(edges=edges, meta=META_NODE))
    assert not ctx.model.is_fa
    assert fa_errors(ctx) == []


def test_type_value_is_stripped():
    meta = META_NODE.replace("standardVersion/ 1.0",
                             "standardVersion/ 1.0\n\ntype/  fa ")
    assert run(fa(meta=meta)).model.is_fa


def test_event_propagation():
    meta = FA_META.replace("type/ fa", "type/ fa\n\neventPropagation/ block")
    assert fa_errors(run(fa(meta=meta))) == []
    meta = meta.replace("/ block", "/ propagate")
    assert fa_errors(run(fa(meta=meta))) == ["fa-event-propagation"]


def test_single_machine():
    assert "fa-single-machine" in errors(run(fa(extra=SECOND_MACHINE)))


def test_element_set():
    choice = ('    <node id="ch">\n      <data key="dVertex">choice</data>\n'
              '    </node>\n')
    assert "fa-element-set" in errors(run(fa(nodes=NODES + choice)))
    collapsed = NESTED.replace('<data key="dName">C</data>',
                               '<data key="dName">C</data>\n'
                               '      <data key="dCollapsed"/>')
    ctx = run(fa(nodes=collapsed, edges=EDGES + INNER_EDGE))
    assert "fa-element-set" in errors(ctx)


def test_state_behaviour():
    exit_block = NODES.replace("entry/\n1", "exit/\n1")
    assert "fa-state-behaviour" in errors(run(fa(nodes=exit_block)))
    two_lines = NODES.replace("entry/\n1", "entry/\n1\n2")
    assert "fa-state-behaviour" in errors(run(fa(nodes=two_lines)))
    internal = NODES.replace("entry/\n1", "entry/\n1\n\nc/ x")
    assert "fa-state-behaviour" in errors(run(fa(nodes=internal)))


def test_composite_accepted_with_one_region_and_initial():
    edges = EDGES + INNER_EDGE + (
        '    <edge id="q0-c0" source="q0" target="c0">\n'
        '      <data key="dData">c/</data>\n    </edge>\n')
    ctx = run(fa(nodes=NESTED, edges=edges))
    assert ctx.report.findings == []


def test_composite_entry_and_regions():
    with_entry = NESTED.replace(
        '<data key="dName">C</data>',
        '<data key="dName">C</data>\n      <data key="dData">entry/\n1</data>')
    ctx = run(fa(nodes=with_entry, edges=EDGES + INNER_EDGE))
    assert "fa-composite" in errors(ctx)
    second = ('        <graph id="c0:2" edgedefault="directed">\n'
              '          <data key="dRegion"/>\n        </graph>\n')
    two = NESTED.replace("      </graph>\n    </node>",
                         "      </graph>\n" + second + "    </node>")
    ctx = run(fa(nodes=two, edges=EDGES + INNER_EDGE))
    assert "fa-composite" in errors(ctx)


def test_composite_entered_without_initial():
    edges = EDGES + ('    <edge id="q0-c0" source="q0" target="c0">\n'
                     '      <data key="dData">c/</data>\n    </edge>\n')
    ctx = run(fa(nodes=NODES + COMPOSITE % "", edges=edges))
    assert "fa-composite-initial" in errors(ctx)
    ctx = run(fa(nodes=NODES + COMPOSITE % ""))
    assert "fa-composite-initial" not in errors(ctx)


def test_deterministic():
    edges = EDGES + ('    <edge id="q0-q0" source="q0" target="q0">\n'
                     '      <data key="dData">a/</data>\n    </edge>\n')
    assert "fa-deterministic" in errors(run(fa(edges=edges)))
    edges = EDGES + ('    <edge id="q0-q0" source="q0" target="q0">\n'
                     '      <data key="dData">c/</data>\n    </edge>\n')
    assert "fa-deterministic" not in errors(run(fa(edges=edges)))


def test_child_transition_shadows_the_parent():
    edges = EDGES + INNER_EDGE + (
        '    <edge id="q0-c0" source="q0" target="c0">\n'
        '      <data key="dData">c/</data>\n    </edge>\n'
        '    <edge id="c0-q0" source="c0" target="q0">\n'
        '      <data key="dData">a/</data>\n    </edge>\n'
        '    <edge id="c1-q1" source="c1" target="q1">\n'
        '      <data key="dData">a/</data>\n    </edge>\n')
    ctx = run(fa(nodes=NESTED, edges=edges))
    assert ctx.report.findings == []


def test_top_initial():
    nodes = NODES.replace('    <node id="init">\n      <data key="dVertex">'
                          'initial</data>\n    </node>\n', "")
    edges = EDGES.replace('    <edge id="init-q0" source="init" '
                          'target="q0"/>\n', "")
    assert "fa-top-initial" in errors(run(fa(nodes=nodes, edges=edges)))


def test_initial_transition_label():
    edges = EDGES.replace('<edge id="init-q0" source="init" target="q0"/>',
                          '<edge id="init-q0" source="init" target="q0">\n'
                          '      <data key="dData">a/</data>\n    </edge>')
    assert "fa-initial-transition" in errors(run(fa(edges=edges)))


def test_final_top_level():
    nested_final = NESTED.replace('<data key="dName">c1</data>',
                                  '<data key="dVertex">final</data>')
    assert "fa-final-top-level" in errors(run(fa(nodes=nested_final)))


def test_eof_final():
    edges = EDGES.replace("b/", "EOF/")
    assert "fa-eof-final" in errors(run(fa(edges=edges)))
    edges = EDGES.replace('target="fin">\n      <data key="dData">EOF/',
                          'target="fin">\n      <data key="dData">c/')
    assert "fa-eof-final" in errors(run(fa(edges=edges)))
    edges = EDGES.replace('target="q0"/>', 'target="fin"/>')
    assert "fa-eof-final" in errors(run(fa(edges=edges)))


def test_transition_label():
    for label in ("a [x]/", "a propagate/", "a/\n\nb/", "/", "[x]/", ""):
        edges = EDGES.replace("b/", label)
        assert "fa-transition-label" in errors(run(fa(edges=edges))), label


def test_transition_action():
    edges = EDGES.replace("a/\n0", "a/\n0\n1")
    assert "fa-transition-action" in errors(run(fa(edges=edges)))


def test_symbol_reserved():
    assert "fa-symbol-reserved" in errors(run(fa(edges=EDGES.replace(
        "b/", "ANY/"))))
    assert "fa-symbol-reserved" in errors(run(fa(edges=EDGES.replace(
        "a/\n0", "a/\nelse"))))
    assert "fa-symbol-reserved" in errors(run(fa(nodes=NODES.replace(
        "entry/\n1", "entry/\nEOF"))))
    nodes = NODES + comment("FA_OUTPUT", "0\nblock")
    assert "fa-symbol-reserved" in errors(run(fa(nodes=nodes)))


def test_alphabet_comments():
    nodes = NODES + comment("FA_INPUT", "a\nb") + \
        comment("FA_INPUT_RE", "[ab]", ident="beta")
    assert "fa-alphabet-comments" in errors(run(fa(nodes=nodes)))
    nodes = NODES + comment("FA_INPUT", "a\nb", kind="informal")
    assert "fa-alphabet-comments" in errors(run(fa(nodes=nodes)))
    inner = NESTED.replace(
        "        <node id=\"c1\">",
        comment("FA_INPUT", "a\nb\nc").replace("\n    ", "\n        ") +
        "        <node id=\"c1\">")
    ctx = run(fa(nodes=inner, edges=EDGES + INNER_EDGE))
    assert "fa-alphabet-comments" in errors(ctx)


def test_alphabet_syntax():
    nodes = NODES + comment("FA_INPUT_RE", "[ab]\nc*")
    assert "fa-alphabet-syntax" in errors(run(fa(nodes=nodes)))
    nodes = NODES + comment("FA_OUTPUT", "0\n\n1")
    assert "fa-alphabet-syntax" in errors(run(fa(nodes=nodes)))


def test_alphabet_membership():
    nodes = NODES + comment("FA_INPUT", "a\nb") + \
        comment("FA_OUTPUT_RE", "[01]", ident="beta")
    assert fa_errors(run(fa(nodes=nodes))) == []
    nodes = NODES + comment("FA_INPUT", "a")
    assert errors(run(fa(nodes=nodes))) == ["fa-alphabet-membership"]
    nodes = NODES + comment("FA_OUTPUT", "1")
    assert errors(run(fa(nodes=nodes))) == ["fa-alphabet-membership"]
    nodes = NODES + comment("FA_OUTPUT_RE", "[1]*")
    assert "fa-alphabet-membership" not in errors(run(fa(nodes=nodes)))
