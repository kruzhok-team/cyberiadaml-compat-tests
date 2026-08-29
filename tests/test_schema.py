# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The RELAX NG schema tests: the corpus against both schema profiles
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

import os
import pathlib
import shutil
import subprocess

import pytest

from cgmlval import rules

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "schema/cgml-1.0.rnc"
STRICT = ROOT / "schema/cgml-1.0-strict.rnc"

POSITIVE_DIRS = ("fixtures/core", "fixtures/ext", "fixtures/field",
                 "fixtures/geometry", "fixtures/standard", "tests/examples")

# The invalid documents the base profile cannot reject: an identity or a
# reference constraint, or a grammar over element text.  See schema/README.md.
UNREACHABLE = frozenset((
    "X-5.5-4-duplicate-data",       # at most one data key per tag (7.4)
    "X-5.9-4-duplicate-id",         # identity
    "X-6.3-2-dangling-target",      # reference resolution
    "X-6.7-2-dangling-link",        # reference resolution
    "X-6.7-4-self-loop",            # identity of two attributes
    "X-8.5-2-link-targets-link",    # reference resolution
    "X-8.5-3-transition-targets-edge",  # reference resolution
    "X-6.3-4-two-else",             # a count over the edges' dData text
    "X-6.8-1-node-no-slash",        # dData behaviour grammar
    "X-6.9-1-no-meta",              # named comment existence and text
    "X-6.9-1-two-meta",             # named comment count
    "X-6.9-2-repeated-param",       # CGML_META parameter grammar
    "X-6.9-4-5-bad-propagation",    # CGML_META parameter grammar
    "X-10.3-1-no-type",             # CGML_COMPONENT parameter grammar
))

# schema/examples: the strict profile rejects each, the base profile accepts it.
# The last two break a requirement cgmlval implements no rule for.
STRICT_ONLY = ("S-choice-point", "S-reserved-vertex",
               "S-region-marker-order", "S-custom-key-for")
UNCHECKED_BY_CGMLVAL = ("S-region-marker-order", "S-custom-key-for")

# The two L1 rules no schema can reach: both are properties of the byte stream,
# which the parser consumes and the XML infoset does not preserve.  Both
# profiles accept these documents; only a byte-level check sees the deviation.
BELOW_THE_SCHEMA = (("L1-encoding", "CGML-5.1-1"),
                    ("L1-no-declaration", "CGML-5.1-2"))


def _runner():
    """The RELAX NG processor: jing on the path, or a jar plus a JVM."""
    jing = shutil.which("jing")
    if jing:
        return [jing, "-c"]
    jar = os.environ.get("CGML_JING_JAR")
    java = os.environ.get("CGML_JAVA") or shutil.which("java")
    if jar and java and pathlib.Path(jar).is_file():
        return [java, "-jar", jar, "-c"]
    return None


RUNNER = _runner()

pytestmark = pytest.mark.skipif(
    RUNNER is None,
    reason="no RELAX NG processor: install jing, or set CGML_JING_JAR "
           "(with CGML_JAVA or java on the path)")


def validate(schema, path):
    """Return the processor report; an empty string means the document is valid."""
    done = subprocess.run(RUNNER + [str(schema), str(path)],
                          capture_output=True, text=True)
    return (done.stdout + done.stderr).strip()


def _documents(*dirs):
    for name in dirs:
        yield from sorted((ROOT / name).glob("*.graphml"))


POSITIVE = list(_documents(*POSITIVE_DIRS))
NEGATIVE = list(_documents("fixtures/negative"))
EXAMPLES = list(_documents("schema/examples"))


def test_the_corpus_is_present():
    assert len(POSITIVE) > 20 and len(NEGATIVE) > 20 and len(EXAMPLES) == 6


@pytest.mark.parametrize("path", POSITIVE, ids=lambda p: p.stem)
def test_valid_documents_pass_both_profiles(path):
    assert validate(BASE, path) == ""
    assert validate(STRICT, path) == ""


@pytest.mark.parametrize("path", NEGATIVE, ids=lambda p: p.stem)
def test_invalid_documents_are_rejected_unless_out_of_reach(path):
    report = validate(BASE, path)
    if path.stem in UNREACHABLE:
        assert report == "", "%s is now caught; update UNREACHABLE" % path.stem
    else:
        assert report != "", "%s is no longer caught" % path.stem


@pytest.mark.parametrize("path", NEGATIVE, ids=lambda p: p.stem)
def test_the_base_profile_never_rejects_what_cgmlval_accepts(path):
    """The soundness invariant: base rejects => cgmlval reports an error."""
    if validate(BASE, path) == "":
        return
    ctx = rules.run_document(path.read_bytes(), str(path))
    assert ctx.report.has_errors(), \
        "%s rejected by the schema but clean for cgmlval" % path.stem


@pytest.mark.parametrize("name", STRICT_ONLY)
def test_the_strict_profile_adds_the_rest_of_the_standard(name):
    path = ROOT / "schema/examples" / (name + ".graphml")
    assert validate(BASE, path) == "", "%s must pass the base profile" % name
    assert validate(STRICT, path) != "", "%s must fail the strict profile" % name


@pytest.mark.parametrize("name", UNCHECKED_BY_CGMLVAL)
def test_the_strict_profile_covers_what_cgmlval_does_not_check(name):
    """These documents break a requirement no cgmlval rule implements."""
    path = ROOT / "schema/examples" / (name + ".graphml")
    ctx = rules.run_document(path.read_bytes(), str(path))
    assert not ctx.report.findings, \
        "%s is now reported by cgmlval: %s" % \
        (name, [f.rule for f in ctx.report.findings])
    assert validate(STRICT, path) != ""


@pytest.mark.parametrize("name,req", BELOW_THE_SCHEMA)
def test_the_byte_level_rules_are_beyond_both_profiles(name, req):
    path = ROOT / "schema/examples" / (name + ".graphml")
    assert validate(BASE, path) == ""
    assert validate(STRICT, path) == ""
    ctx = rules.run_document(path.read_bytes(), str(path))
    assert req in [f.req for f in ctx.report.findings], \
        "%s no longer reports %s" % (name, req)
