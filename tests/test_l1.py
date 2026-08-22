# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The L1 layer tests: encoding, declaration, well-formedness
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

from cgmlval import cli, rules
from docbuilder import DECLARATION, minimal


def run(data):
    return rules.run_document(data, "test.graphml")


def rule_names(ctx):
    return [f.rule for f in ctx.report.findings]


def test_minimal_document_is_clean():
    ctx = run(minimal())
    assert ctx.report.findings == []
    assert ctx.report.verdict() == "valid"
    assert 1 in ctx.report.layers_run
    assert ctx.parsed.root.tag == "graphml"


def test_cyrillic_content_preserved():
    doc = minimal().replace(b"Test machine",
                            "Машина состояний".encode("utf-8"))
    ctx = run(doc)
    assert ctx.report.findings == []
    text = [d.text for g in ctx.parsed.root.iter("graph")
            for d in g.findall("data")]
    assert "Машина состояний" in text


def test_escaped_characters_unescaped_on_read():
    doc = minimal().replace(b"<data key=\"dName\">Idle</data>",
                            b"<data key=\"dName\">&quot;A&quot; &gt;= &amp; b</data>")
    ctx = run(doc)
    assert ctx.report.findings == []
    names = [d.text for n in ctx.parsed.root.iter("node")
             for d in n.findall("data") if d.get("key") == "dName"]
    assert '"A" >= & b' in names


def test_xml_comments_ignored():
    doc = minimal(
        gformat='<!-- top --><data key="gFormat">Cyberiada-GraphML-1.0</data>\n')
    doc = doc.replace(b"<edge", b"<!-- between nodes and edges --><edge")
    doc = doc.replace(b'<node id="n0">', b'<node id="n0"><!-- inside node -->')
    ctx = run(doc)
    assert ctx.report.findings == []


def test_utf16_document_reported():
    text = minimal().decode("utf-8").replace('encoding="UTF-8"',
                                             'encoding="UTF-16"')
    ctx = run(text.encode("utf-16"))
    assert "doc-encoding" in rule_names(ctx)
    assert ctx.report.has_warnings()
    assert not ctx.report.has_errors()
    assert not ctx.report.valid(strict=True)


def test_declared_non_utf8_encoding_reported():
    ctx = run(minimal(
        declaration='<?xml version="1.0" encoding="windows-1251"?>\n'))
    assert "doc-encoding" in rule_names(ctx)
    assert not ctx.report.has_errors()


def test_broken_utf8_reported():
    ctx = run(minimal().replace(b"Idle", b"Idl\xff"))
    assert "doc-encoding" in rule_names(ctx)


def test_missing_declaration_reported():
    ctx = run(minimal(declaration=""))
    assert rule_names(ctx) == ["xml-declaration"]
    assert ctx.report.has_warnings()


def test_declaration_without_encoding_reported():
    ctx = run(minimal(declaration='<?xml version="1.0"?>\n'))
    assert rule_names(ctx) == ["xml-declaration"]


def test_truncated_file_rejected():
    ctx = run(minimal()[:-40])
    findings = ctx.report.findings
    assert [f.rule for f in findings] == ["xml-well-formed"]
    assert findings[0].line is not None
    assert ctx.report.verdict() == "invalid"
    assert ctx.report.layers_run == [1]


def test_empty_file_rejected():
    for data in (b"", b"   \n"):
        ctx = run(data)
        assert "xml-not-empty" in rule_names(ctx)
        assert ctx.report.has_errors()


def test_binary_junk_rejected():
    ctx = run(bytes(range(256)))
    assert ctx.report.has_errors()
    assert ctx.parsed is None


def test_unescaped_ampersand_rejected():
    doc = minimal().replace(b"standardVersion/ 1.0", b"a && b")
    ctx = run(doc)
    errors = [f for f in ctx.report.findings if f.rule == "xml-well-formed"]
    assert errors and errors[0].line is not None


def test_registry_contains_l1_rules():
    rules.load_checks()
    for name in ("xml-well-formed", "doc-encoding", "char-escaping",
                 "data-escaping", "xml-comments"):
        assert name in rules.REGISTRY


def test_cli_validate_exit_codes(tmp_path):
    good = tmp_path / "good.graphml"
    good.write_bytes(minimal())
    bad = tmp_path / "bad.graphml"
    bad.write_bytes(minimal()[:-40])
    warn = tmp_path / "warn.graphml"
    warn.write_bytes(minimal(declaration=""))
    assert cli.main(["validate", str(good)]) == cli.EXIT_OK
    assert cli.main(["validate", str(bad)]) == cli.EXIT_FINDINGS
    assert cli.main(["validate", str(warn)]) == cli.EXIT_OK
    assert cli.main(["validate", "--strict", str(warn)]) == cli.EXIT_FINDINGS
    assert cli.main(["validate", str(tmp_path / "missing.graphml")]) == \
        cli.EXIT_USAGE
    assert cli.main(["rules"]) == cli.EXIT_OK
