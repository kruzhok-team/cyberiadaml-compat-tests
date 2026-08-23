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

## Tests

The validator's own test suite runs with pytest:

    python3 -m pytest tests/ -q

It covers the two text grammars (behaviour and metadata), each validation
layer with accept/reject document pairs, the canonical dump against the
hand-written expected dumps in `tests/examples/`, the registry-vs-requirements
coverage audit, and a report-only smoke run over the sample corpora of the
sibling repositories (skipped when absent).

Copyright (c) Alexey Fedoseev aleksey@fedoseev.net, 2026.
The code and the documentation were designed using AI participation.

The code is distributed under the GNU Public License (version 3), the documentation -- under
the GNU Free Documentation License (version 1.3).
