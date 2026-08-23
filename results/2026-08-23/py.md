# cyberiadaml-py 1.4.1 — defect report

Generated 2026-08-23 from fixture corpus revision `9c194e3`; standard PNST 1044-2025; the library claims CORE.
Summary: 1 defect (1 major). Verdict counts per requirement are in `REPORT.md`.

## PY-1 — reader requires the optional platform meta parameter

| | |
|---|---|
| kind | read |
| severity | major |
| channel | round-trip |
| violates | 54 requirements of the affected fixtures (highest level MUST) |
| fixtures | 19 of 19: `core/F-CMT`, `core/F-EMPTY-SM`, `core/F-ESC-ENT`, `core/F-ESC-RAW`, `core/F-FLAT`, `core/F-HIER`, … |
| impact | the driver cannot read 19 of 19 positive fixtures |

Note: platform is MAY per §6.9 (CGML-6.9-4-2); every standard document without it is rejected with 'No platform or standardVersion.'

Evidence (`core/F-CMT`):

    rejected by cyberiadaml-py: No platform or standardVersion.

Reproduce:

    drivers/py/driver convert fixtures/core/F-CMT.graphml out.graphml   # exits 2 (rejected)

## Missing rejections

Invalid documents the library accepted (`crash` rows crashed instead of rejecting):

| fixture | requirement | level | outcome |
|---|---|---|---|
| `negative/X-5.4-1-gformat-missing` | `CGML-5.4-1` | MUST | crash |
| `negative/X-5.5-3-data-without-key` | `CGML-5.5-3` | MUST | crash |
| `negative/X-5.9-1-missing-id` | `CGML-5.9-1` | MUST | crash |
| `negative/X-6.9-1-no-meta` | `CGML-6.9-1` | MUST | accepted |
| `negative/X-appendix-A-1-foreign-tag` | `CGML-appendix-A-1` | MUST | crash |

## Tolerance notes (unclaimed profiles)

Fixtures of unclaimed profiles the library refused (spec §2.1 tolerance):

- ext/F-EXT-C: rejected (rejected by cyberiadaml-py: No platform or standardVersion.)
- ext/F-EXT-D: rejected (rejected by cyberiadaml-py: No platform or standardVersion.)
- ext/F-EXT-P: rejected (rejected by cyberiadaml-py: No platform or standardVersion.)
- geometry/F-GEO-F: rejected (rejected by cyberiadaml-py: No platform or standardVersion.)

