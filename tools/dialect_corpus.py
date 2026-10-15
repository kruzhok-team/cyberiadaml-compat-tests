#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# The Lapki dialect corpus: collect the documents, record the expected output
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

"""Usage:
    tools/dialect_corpus.py collect [SOURCES_DIR]   copy the documents in
    tools/dialect_corpus.py record                  write .expected/.repairs
"""

import collections
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cgmlval import dump, rules  # noqa: E402
from cgmlval.dialect import LAPKI  # noqa: E402

CORPUS = ROOT / "fixtures" / "dialect" / LAPKI
MANIFEST = CORPUS / "manifest.json"

TEMPLATES = "resources/templates/"
COMPILER = "examples/"

# (corpus name, repository, path in it); a document equal to an earlier one
# by content is recorded as a further source of that one
SOURCES = [
    ("client-template-blinker", "lapki-client",
     TEMPLATES + "Arduino Uno/Мигалка.graphml"),
    ("client-template-autoborder", "lapki-client",
     TEMPLATES + "Защита пасеки/Автобортник.graphml"),
    ("client-template-generator", "lapki-client",
     TEMPLATES + "Защита пасеки/Генератор.graphml"),
    ("client-template-smoker", "lapki-client",
     TEMPLATES + "Защита пасеки/Дымарь.graphml"),
    ("client-template-stapler", "lapki-client",
     TEMPLATES + "Защита пасеки/Степлер.graphml"),
    ("client-demo-blinker", "lapki-client", "demos/blinker.graphml"),
    ("client-demo-autoborder", "lapki-client",
     "demos/CyberiadaSchemas/CyberiadaFormat-Autoborder.graphml"),
    ("client-demo-cyberiada-blinker", "lapki-client",
     "demos/CyberiadaSchemas/CyberiadaFormat-Blinker.graphml"),
    ("client-demo-tjc-ms1-blinker", "lapki-client",
     "demos/CyberiadaSchemas/tjc-ms1-blinker.graphml"),
] + [
    ("compiler-" + stem.lower().replace("_", "-"), "lapki-compiler",
     COMPILER + stem + ".graphml")
    for stem in (
        "CyberiadaFormat-Blinker", "IRPCB_LED_EXAMPLE", "choices",
        "initial_states", "ms-button-all", "ms-lmp-all", "ms-main-all",
        "ms-mtrx-all", "ms1-btn", "ms1-lmp", "ms1-main", "ms1-mtrx",
        "test_cyberbear", "test_initial_states", "test_parent_transitions",
        "test_shallow_history", "two-blinkers", "two_choices", "with-final",
        "with-optional-parameter", "with-propagate-block")
] + [
    ("py-demo-autoborder", "cyberiadaml-py",
     "demos/CyberiadaFormat-Autoborder.graphml"),
    ("py-demo-blinker", "cyberiadaml-py",
     "demos/CyberiadaFormat-Blinker.graphml"),
    ("py-demo-two-blinkers", "cyberiadaml-py", "demos/two-blinkers.graphml"),
    ("py-demo-shallow-history", "cyberiadaml-py",
     "demos/with-shallow-history.graphml"),
    ("js-demo-arduino-blinker", "cyberiadaml-js",
     "demos/arduino-blinker.graphml"),
    ("js-demo-autoborder", "cyberiadaml-js", "demos/autoborder.graphml"),
    ("js-demo-nested", "cyberiadaml-js", "demos/nested.graphml"),
    ("js-demo-two-blinkers", "cyberiadaml-js", "demos/two-blinkers.graphml"),
    ("js-demo-empty-state", "cyberiadaml-js",
     "demos/with-empty-state.graphml"),
    ("js-demo-local-history", "cyberiadaml-js",
     "demos/with_local_history.graphml"),
    ("lib-lapki-js", "libcyberiadaml", "tests/diagrams/lapki-js.graphml"),
]


def _revision(repo):
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def collect(sources_dir):
    CORPUS.mkdir(parents=True, exist_ok=True)
    documents = {}
    by_hash = {}
    for name, repo, path in SOURCES:
        data = (sources_dir / repo / path).read_bytes()
        source = {"repository": repo, "path": path,
                  "revision": _revision(sources_dir / repo)}
        digest = hashlib.sha256(data).hexdigest()
        if digest in by_hash:
            documents[by_hash[digest]]["also"].append(source)
            continue
        by_hash[digest] = name
        documents[name] = dict(source, also=[])
        (CORPUS / (name + ".graphml")).write_bytes(data)
    _write_manifest(documents)
    return documents


def _write_manifest(documents):
    MANIFEST.write_text(json.dumps({"documents": documents},
                                   ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")


def run(name):
    data = (CORPUS / (name + ".graphml")).read_bytes()
    return rules.run_document(data, name + ".graphml", dialect=LAPKI)


def repairs_text(ctx):
    counts = collections.Counter(f.req for f in ctx.report.findings
                                 if f.layer == 0)
    return "".join("%s %d\n" % item for item in sorted(counts.items()))


def errors_of(ctx):
    return sorted({f.req or f.rule for f in ctx.report.findings
                   if f.severity == "ERROR"})


def record():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    documents = manifest["documents"]
    for name, entry in documents.items():
        ctx = run(name)
        (CORPUS / (name + ".repairs.txt")).write_text(repairs_text(ctx),
                                                       encoding="utf-8")
        expected = CORPUS / (name + ".expected.txt")
        errors = errors_of(ctx)
        if errors:
            entry["status"] = "invalid"
            entry["errors"] = errors
            if expected.exists():
                expected.unlink()
        else:
            entry["status"] = "valid"
            entry.pop("errors", None)
            expected.write_text(dump.render(ctx.model), encoding="utf-8")
    _write_manifest(documents)
    return documents


def main(argv):
    if len(argv) >= 2 and argv[1] == "collect":
        sources = pathlib.Path(argv[2]) if len(argv) > 2 else ROOT.parent
        print("%d documents" % len(collect(sources)))
        return 0
    if len(argv) == 2 and argv[1] == "record":
        documents = record()
        invalid = [n for n, e in documents.items() if e["status"] != "valid"]
        print("%d documents, %d invalid: %s" %
              (len(documents), len(invalid), " ".join(invalid)))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
