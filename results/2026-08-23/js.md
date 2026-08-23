# cyberiadaml-js 1.2.3 — defect report

Generated 2026-08-23 from fixture corpus revision `9c194e3`; standard PNST 1044-2025; the library claims CORE.
Summary: 9 defects (9 major). Verdict counts per requirement are in `REPORT.md`.

## JS-1 — writer invents default geometry rect 0 0 0 0

| | |
|---|---|
| kind | write |
| severity | major |
| channel | dump-equality |
| violates | 33 requirements of the affected fixtures (highest level MUST) |
| fixtures | 9 of 19: `core/F-ESC-ENT`, `core/F-ESC-RAW`, `core/F-FLAT`, `core/F-MIN`, `core/F-MIN-comments`, `core/F-MIN-nokeys`, … |
| impact | round-trip loses fidelity on 9 fixture(s) |

Note: elements carrying no dGeometry gain one on write; breaks the geometry-mode consistency of §7

Evidence (`core/F-ESC-ENT`):

    line 13: expected '  comment "nMeta" formal:', got '    geometry: rect 0.00 0.00 0.00 0.00'

Reproduce:

    drivers/js/driver convert fixtures/core/F-ESC-ENT.graphml out.graphml
    python3 -m cgmlval dump out.graphml | diff fixtures/core/F-ESC-ENT.expected.txt -

## JS-2 — writer re-emits point geometry as rect with size -1

| | |
|---|---|
| kind | write |
| severity | major |
| channel | dump-equality |
| violates | `CGML-7.1-1` (MUST, CORE, §7.1); `CGML-7.2-1-1` (MUST, CORE, §7.2); `CGML-7.2-1-2` (MUST, CORE, §7.2); `CGML-7.2-1-3` (MUST, CORE, §7.2); `CGML-7.2-2` (MUST, CORE, §7.2) |
| fixtures | 1 of 19: `geometry/F-GEO-S` |
| impact | round-trip loses fidelity on 1 fixture(s) |

Evidence (`geometry/F-GEO-S`):

    line 13: expected '    geometry: point -60.50 20.00', got '    geometry: rect -60.50 20.00 -1.00 -1.00'

Reproduce:

    drivers/js/driver convert fixtures/geometry/F-GEO-S.graphml out.graphml
    python3 -m cgmlval dump out.graphml | diff fixtures/geometry/F-GEO-S.expected.txt -

## JS-3 — writer appends a trailing blank line to meta comment bodies

| | |
|---|---|
| kind | write |
| severity | major |
| channel | dump-equality |
| violates | `CGML-6.1-2` (MUST, CORE, §6.1); `CGML-6.9-1` (MUST, CORE, §6.9); `CGML-6.9-2` (MUST, CORE, §6.9); `CGML-6.9-3` (MUST, CORE, §6.9) |
| fixtures | 1 of 19: `core/F-EMPTY-SM` |
| impact | round-trip loses fidelity on 1 fixture(s) |

Evidence (`core/F-EMPTY-SM`):

    line 12: expected '    body: "standardVersion/ 1.0"', got '    body: "standardVersion/ 1.0\\n\\n"'

Reproduce:

    drivers/js/driver convert fixtures/core/F-EMPTY-SM.graphml out.graphml
    python3 -m cgmlval dump out.graphml | diff fixtures/core/F-EMPTY-SM.expected.txt -

## JS-4 — state machine formal name (dFormalName) dropped on write

| | |
|---|---|
| kind | write |
| severity | major |
| channel | dump-equality |
| violates | `CGML-10.1-2` (MUST, EXT-PLATFORM, §10.1); `CGML-10.1-3` (MUST, EXT-PLATFORM, §10.1) |
| fixtures | 1 of 19: `ext/F-EXT-P` |
| impact | round-trip loses fidelity on 1 fixture(s) |

Evidence (`ext/F-EXT-P`):

    line 10: expected '  formal-name: "platform_sm"', got '  comment "cComp" formal:'

Reproduce:

    drivers/js/driver convert fixtures/ext/F-EXT-P.graphml out.graphml
    python3 -m cgmlval dump out.graphml | diff fixtures/ext/F-EXT-P.expected.txt -

## JS-5 — reader rejects formal comments other than CGML_META and CGML_COMPONENT

| | |
|---|---|
| kind | read |
| severity | major |
| channel | round-trip |
| violates | `CGML-6.6-1` (MUST, CORE, §6.6); `CGML-6.7-1` (MUST, CORE, §6.7); `CGML-6.7-2` (MUST, CORE, §6.7) |
| fixtures | 1 of 19: `core/F-CMT` |
| impact | the driver cannot read 1 of 19 positive fixtures |

Note: §6.7 admits arbitrary formal comment names

Evidence (`core/F-CMT`):

    rejected by cyberiadaml-js: Неизвестный тип мета-информации traceId/ REQ-42. Ожидается CGML_META или CGML_COMPONENT.

Reproduce:

    drivers/js/driver convert fixtures/core/F-CMT.graphml out.graphml   # exits 2 (rejected)

## JS-6 — reader rejects rect-valued transition label geometry

| | |
|---|---|
| kind | read |
| severity | major |
| channel | round-trip |
| violates | `CGML-6.3-5` (MUST, CORE, §6.3); `CGML-7.1-1` (MUST, CORE, §7.1); `CGML-7.2-1-5` (MUST, CORE, §7.2); `CGML-7.2-1-6` (MUST, CORE, §7.2); `CGML-7.2-2` (MUST, CORE, §7.2) |
| fixtures | 1 of 19: `geometry/F-GEO-F` |
| impact | the driver cannot read 1 of 19 positive fixtures |

Note: dLabelGeometry admits rect in full geometry mode (§7)

Evidence (`geometry/F-GEO-F`):

    rejected by cyberiadaml-js: Нет дочернего <point> у <data> с ключом dLabelGeometry

Reproduce:

    drivers/js/driver convert fixtures/geometry/F-GEO-F.graphml out.graphml   # exits 2 (rejected)

## JS-7 — writer emits a node with an empty id for a multi-machine document

| | |
|---|---|
| kind | write |
| severity | major |
| channel | validate-on-output |
| violates | `CGML-5.9-3` (MUST, CORE, §5.9) |
| fixtures | 1 of 19: `core/F-MULTI` |
| impact | affected outputs are invalid; 4 fixture requirement(s) blocked |

Evidence (`core/F-MULTI`):

    ERROR CGML-5.9-3: node with an empty id

Reproduce:

    drivers/js/driver convert fixtures/core/F-MULTI.graphml out.graphml
    python3 -m cgmlval validate out.graphml

## JS-8 — region graph id replaced by the parent node id

| | |
|---|---|
| kind | write |
| severity | major |
| channel | validate-on-output |
| violates | `CGML-5.9-4` (MUST, CORE, §5.9) |
| fixtures | 1 of 19: `core/F-HIER` |
| impact | affected outputs are invalid; 5 fixture requirement(s) blocked |

Note: duplicates the parent id, violating document-wide id uniqueness (§5.9)

Evidence (`core/F-HIER`):

    ERROR CGML-5.9-4: graph id 'c0' duplicates the id of a node

Reproduce:

    drivers/js/driver convert fixtures/core/F-HIER.graphml out.graphml
    python3 -m cgmlval validate out.graphml

## JS-9 — writer places dNote after dGeometry on comment nodes

| | |
|---|---|
| kind | write |
| severity | major |
| channel | validate-on-output |
| violates | `CGML-6.6-1` (MUST, CORE, §6.6) |
| fixtures | 3 of 19: `ext/F-EXT-C`, `ext/F-EXT-D`, `field/F-FIELD-ros-cycle` |
| impact | affected outputs are invalid; 4 fixture requirement(s) blocked |

Note: dNote must be the first data key of a comment node (§6.6)

Evidence (`ext/F-EXT-C`):

    ERROR CGML-6.6-1: dNote is not the first data key (found after dGeometry)

Reproduce:

    drivers/js/driver convert fixtures/ext/F-EXT-C.graphml out.graphml
    python3 -m cgmlval validate out.graphml

## Missing rejections

Invalid documents the library accepted (`crash` rows crashed instead of rejecting):

| fixture | requirement | level | outcome |
|---|---|---|---|
| `negative/X-10.1-2-bad-formal-name` | `CGML-10.1-2` | MUST | accepted |
| `negative/X-5.4-2-wrong-format` | `CGML-5.4-2` | MUST | accepted |
| `negative/X-5.5-3-data-without-key` | `CGML-5.5-3` | MUST | accepted |
| `negative/X-5.5-4-duplicate-data` | `CGML-5.5-4` | MUST | accepted |
| `negative/X-5.8-1-empty-endpoint` | `CGML-5.8-1` | MUST | accepted |
| `negative/X-5.9-1-missing-id` | `CGML-5.9-1` | MUST | accepted |
| `negative/X-5.9-2-bad-id-char` | `CGML-5.9-2` | MUST | accepted |
| `negative/X-5.9-4-duplicate-id` | `CGML-5.9-4` | MUST | accepted |
| `negative/X-6.1-2-no-name` | `CGML-6.1-2` | MUST | accepted |
| `negative/X-6.3-2-dangling-target` | `CGML-6.3-2` | MUST | accepted |
| `negative/X-6.4-1-vertex-not-first` | `CGML-6.4-1` | MUST | accepted |
| `negative/X-6.4-2-bad-vertex` | `CGML-6.4-2` | MUST | accepted |
| `negative/X-6.4-4-1-two-initials` | `CGML-6.4-4-1` | MUST | accepted |
| `negative/X-6.7-2-dangling-link` | `CGML-6.7-2` | MUST | accepted |
| `negative/X-6.8-1-missing-slash` | `CGML-6.8-1` | MUST | accepted |
| `negative/X-6.9-1-no-meta` | `CGML-6.9-1` | MUST | accepted |
| `negative/X-6.9-4-5-bad-propagation` | `CGML-6.9-4-5` | MAY | accepted |
| `negative/X-appendix-A-1-foreign-tag` | `CGML-appendix-A-1` | MUST | accepted |
| `negative/X-appendix-B-1-wrong-for` | `CGML-appendix-B-1` | MUST | accepted |

## Tolerance notes (unclaimed profiles)

Fixtures of unclaimed profiles the library refused (spec §2.1 tolerance):

- geometry/F-GEO-F: rejected (rejected by cyberiadaml-js: Нет дочернего <point> у <data> с ключом dLabelGeometry)

