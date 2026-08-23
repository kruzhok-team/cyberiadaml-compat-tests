# CyberiadaML-GraphML Standard Compatibility Tests

This repository contains the set of specifications and tools for checking
CyberiadaML GraphML standard compatibilty of libraries and tools.

See the PNST 1044-2025 and PNST 984-2024 Russian national standard documents for
details.

## Documentation

* `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` - the testing specification: what must be
  checked, requirement identifiers, conformance profiles;
* `CyberiadaML-GraphML-1.0-TEST-CATALOG.md` - the conformance test catalog: the layered
  validation procedure and the test list;
* `CyberiadaML-GraphML-1.0-VALIDATOR-SPEC.md` - the document validator specification:
  the `cgmlval` tool and the canonical dump format.
* `CyberiadaML-GraphML-1.0-HARNESS-SPEC.md` - the compatibility harness specification:
  the fixture corpus, the library driver contract and the conformance report.

## Usage

The `cgmlval` validator runs on Python 3 (stdlib only) from the repository root:

    python3 -m cgmlval validate [--strict] [--json] FILE...
    python3 -m cgmlval dump [--json] FILE
    python3 -m cgmlval rules [--json]

`validate` checks documents through the layers L1 (XML), L2 (tag tree),
L3 (attributes and values) and L4 (document integrity); an error at a layer
stops the layers above it. Exit code 0 means no errors; `--strict` also fails
on warnings. `dump` prints the canonical dump of a valid document (the golden
file format of the test catalog); `rules` lists the registered checks with
their requirement identifiers.

## The compatibility harness

The `intharness` runner compares the CGML libraries against the fixture corpus in
`fixtures/` through per-library drivers in `drivers/` (see the harness specification):

    python3 -m intharness run                              # writes report.json
    python3 -m intharness report --out-dir results/<date>  # summary + per-library defect reports

The report renders the summary `REPORT.md` and one defect report per library
into `results/<date>/` (generated, not tracked); the stable defect ids are
curated in `defects.json`. The cyberiadaml-js driver requires a one-time
`npm install && npm run build` in the library checkout; the C# driver a
user-local .NET SDK 8 (`~/.dotnet`) and a one-time
`dotnet build -c Release drivers/cs`.

## Tests

The validator's own test suite runs with pytest:

    python3 -m pytest tests/ -q

It covers the two text grammars (behaviour and metadata), each validation
layer with accept/reject document pairs, the canonical dump against the
hand-written expected dumps in `tests/examples/`, the registry-vs-requirements
coverage audit, and a report-only smoke run over the sample corpora of the
sibling repositories (skipped when absent).

Copyright (c) Alexey Fedoseev aleksey@fedoseev.net, 2026.

The code is distributed under the GNU Public License (version 3), the documentation -- under
the GNU Free Documentation License (version 1.3).
