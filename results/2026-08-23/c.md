# libcyberiadaml v1.0-45-ga14b6b6 — defect report

Generated 2026-08-23 from fixture corpus revision `9c194e3`; standard PNST 1044-2025; the library claims CORE, EXT-COMPLETENESS, EXT-DISPLAY, EXT-PLATFORM.
Summary: 2 defects (2 major). Verdict counts per requirement are in `REPORT.md`.

## C-1 — writer declares dRegion with for="node"

| | |
|---|---|
| kind | write |
| severity | major |
| channel | validate-on-output |
| violates | `CGML-appendix-B-1` (MUST, CORE, appendix Б) |
| fixtures | 17 of 19: `core/F-CMT`, `core/F-EMPTY-SM`, `core/F-ESC-ENT`, `core/F-ESC-RAW`, `core/F-FLAT`, `core/F-HIER`, … |
| impact | affected outputs are invalid; 52 fixture requirement(s) blocked |

Note: appendix Б requires for="graph"; every produced document is invalid

Evidence (`core/F-CMT`):

    ERROR CGML-appendix-B-1: standard key dRegion redeclared for 'node'

Reproduce:

    drivers/c/driver convert fixtures/core/F-CMT.graphml out.graphml
    python3 -m cgmlval validate out.graphml

## C-2 — reader rejects multi-machine and completeness documents

| | |
|---|---|
| kind | read |
| severity | major |
| channel | round-trip |
| violates | `CGML-5.6-2` (MUST, CORE, §5.6); `CGML-5.9-4` (MUST, CORE, §5.9); `CGML-6.1-2` (MUST, CORE, §6.1); `CGML-6.7-2` (MUST, CORE, §6.7); `CGML-6.9-1` (MUST, CORE, §6.9); `CGML-8.5-2` (MUST, EXT-COMPLETENESS, §8.5) |
| fixtures | 2 of 19: `core/F-MULTI`, `ext/F-EXT-C` |
| impact | the driver cannot read 2 of 19 positive fixtures |

Note: cybparser exits 2 without a diagnostic; F-MULTI carries two state machines, F-EXT-C submachine/history/entry-exit points

Evidence (`core/F-MULTI`):

    rejected by libcyberiadaml (cybparser exit 2)

Reproduce:

    drivers/c/driver convert fixtures/core/F-MULTI.graphml out.graphml   # exits 2 (rejected)

## Missing rejections

Invalid documents the library accepted (`crash` rows crashed instead of rejecting):

| fixture | requirement | level | outcome |
|---|---|---|---|
| `negative/X-10.1-2-bad-formal-name` | `CGML-10.1-2` | MUST | accepted |
| `negative/X-5.6-2-no-graphs` | `CGML-5.6-2` | MUST | crash |
| `negative/X-5.9-2-bad-id-char` | `CGML-5.9-2` | MUST | accepted |
| `negative/X-6.1-1-no-marker` | `CGML-6.1-1` | MUST | accepted |
| `negative/X-6.1-2-no-name` | `CGML-6.1-2` | MUST | accepted |
| `negative/X-6.4-1-vertex-not-first` | `CGML-6.4-1` | MUST | accepted |
| `negative/X-6.8-1-missing-slash` | `CGML-6.8-1` | MUST | accepted |
| `negative/X-6.9-1-no-meta` | `CGML-6.9-1` | MUST | accepted |
| `negative/X-appendix-A-1-foreign-tag` | `CGML-appendix-A-1` | MUST | accepted |
| `negative/X-appendix-B-1-wrong-for` | `CGML-appendix-B-1` | MUST | accepted |

