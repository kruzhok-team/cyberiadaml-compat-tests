# CyberiadaML-GraphML 1.0 — Library Conformance Report

Generated 2026-08-23 from fixture corpus revision `9c194e3` by the intharness runner
(see `CyberiadaML-GraphML-1.0-HARNESS-SPEC.md` for the channel, verdict and defect semantics).

## Implementations

- **c** — libcyberiadaml v1.0-45-ga14b6b6, claims CORE, EXT-COMPLETENESS, EXT-DISPLAY, EXT-PLATFORM: 2 defects (2 major), defect report [`c.md`](c.md)
- **js** — cyberiadaml-js 1.2.3, claims CORE: 9 defects (9 major), defect report [`js.md`](js.md)
- **py** — cyberiadaml-py 1.4.1, claims CORE: 1 defect (1 major), defect report [`py.md`](py.md)

## Requirement scoreboard

| Library | Profile | pass | fail | blocked | not-claimed | not-covered | not-tested |
|---|---|---|---|---|---|---|---|
| c | CORE | 5 | 11 | 38 | 0 | 14 | 14 |
| c | EXT-COMPLETENESS | 0 | 1 | 0 | 0 | 0 | 7 |
| c | EXT-DISPLAY | 0 | 0 | 2 | 0 | 0 | 3 |
| c | EXT-PLATFORM | 0 | 1 | 1 | 0 | 0 | 3 |
| js | CORE | 0 | 47 | 4 | 0 | 17 | 14 |
| js | EXT-COMPLETENESS | 0 | 0 | 1 | 0 | 0 | 7 |
| js | EXT-DISPLAY | 0 | 0 | 2 | 0 | 0 | 3 |
| js | EXT-PLATFORM | 0 | 2 | 0 | 0 | 0 | 3 |
| py | CORE | 4 | 47 | 0 | 0 | 17 | 14 |
| py | EXT-COMPLETENESS | 0 | 0 | 0 | 1 | 0 | 7 |
| py | EXT-DISPLAY | 0 | 0 | 0 | 2 | 0 | 3 |
| py | EXT-PLATFORM | 1 | 0 | 0 | 1 | 0 | 3 |

## Failed requirements

Each failure names the defect record explaining it (`<library>.md`).

### c

- `CGML-10.1-2` — missing rejection (`negative/X-10.1-2-bad-formal-name`)
- `CGML-5.6-2` — C-2
- `CGML-5.9-2` — missing rejection (`negative/X-5.9-2-bad-id-char`)
- `CGML-5.9-4` — C-2
- `CGML-6.1-1` — missing rejection (`negative/X-6.1-1-no-marker`)
- `CGML-6.1-2` — C-2
- `CGML-6.4-1` — missing rejection (`negative/X-6.4-1-vertex-not-first`)
- `CGML-6.7-2` — C-2
- `CGML-6.8-1` — missing rejection (`negative/X-6.8-1-missing-slash`)
- `CGML-6.9-1` — C-2
- `CGML-8.5-2` — C-2
- `CGML-appendix-A-1` — missing rejection (`negative/X-appendix-A-1-foreign-tag`)
- `CGML-appendix-B-1` — C-1

### js

- `CGML-10.1-2` — JS-4
- `CGML-10.1-3` — JS-4
- `CGML-5.1-1` — JS-1
- `CGML-5.1-2` — JS-1
- `CGML-5.2-1` — JS-1
- `CGML-5.3-1` — JS-1
- `CGML-5.4-1` — JS-1
- `CGML-5.4-2` — JS-1
- `CGML-5.5-1` — JS-1
- `CGML-5.5-2` — JS-1
- `CGML-5.5-3` — missing rejection (`negative/X-5.5-3-data-without-key`)
- `CGML-5.5-4` — missing rejection (`negative/X-5.5-4-duplicate-data`)
- `CGML-5.6-1` — JS-1
- `CGML-5.6-2` — JS-1
- `CGML-5.6-3` — JS-1
- `CGML-5.7-1` — JS-1
- `CGML-5.8-1` — JS-1
- `CGML-5.8-2` — JS-1
- `CGML-5.9-1` — JS-1
- `CGML-5.9-2` — JS-1
- `CGML-5.9-3` — JS-1
- `CGML-5.9-4` — JS-8
- `CGML-6.1-1` — JS-1
- `CGML-6.1-2` — JS-1
- `CGML-6.1-4` — JS-1
- `CGML-6.2-3` — JS-1
- `CGML-6.3-2` — missing rejection (`negative/X-6.3-2-dangling-target`)
- `CGML-6.4-1` — JS-1
- `CGML-6.4-2` — JS-1
- `CGML-6.4-4-1` — missing rejection (`negative/X-6.4-4-1-two-initials`)
- `CGML-6.6-1` — JS-5
- `CGML-6.7-1` — JS-5
- `CGML-6.7-2` — JS-5
- `CGML-6.8-1` — JS-1
- `CGML-6.8-2` — JS-1
- `CGML-6.8-3` — JS-1
- `CGML-6.8-4` — JS-1
- `CGML-6.8-7` — JS-1
- `CGML-6.9-1` — JS-1
- `CGML-6.9-2` — JS-1
- `CGML-6.9-3` — JS-1
- `CGML-6.9-4-5` — missing rejection (`negative/X-6.9-4-5-bad-propagation`)
- `CGML-7.1-1` — JS-2
- `CGML-7.2-1-1` — JS-2
- `CGML-7.2-1-2` — JS-2
- `CGML-7.2-1-3` — JS-2
- `CGML-7.2-2` — JS-2
- `CGML-appendix-A-1` — JS-1
- `CGML-appendix-B-1` — JS-1

### py

- `CGML-5.1-1` — PY-1
- `CGML-5.1-2` — PY-1
- `CGML-5.2-1` — PY-1
- `CGML-5.3-1` — PY-1
- `CGML-5.4-1` — PY-1
- `CGML-5.4-2` — PY-1
- `CGML-5.5-1` — PY-1
- `CGML-5.5-2` — PY-1
- `CGML-5.5-3` — missing rejection (`negative/X-5.5-3-data-without-key`)
- `CGML-5.6-1` — PY-1
- `CGML-5.6-2` — PY-1
- `CGML-5.6-3` — PY-1
- `CGML-5.7-1` — PY-1
- `CGML-5.7-2` — PY-1
- `CGML-5.8-1` — PY-1
- `CGML-5.8-2` — PY-1
- `CGML-5.9-1` — PY-1
- `CGML-5.9-2` — PY-1
- `CGML-5.9-3` — PY-1
- `CGML-5.9-4` — PY-1
- `CGML-6.1-1` — PY-1
- `CGML-6.1-2` — PY-1
- `CGML-6.1-4` — PY-1
- `CGML-6.2-3` — PY-1
- `CGML-6.4-1` — PY-1
- `CGML-6.4-2` — PY-1
- `CGML-6.5-1` — PY-1
- `CGML-6.5-2` — PY-1
- `CGML-6.5-4` — PY-1
- `CGML-6.6-1` — PY-1
- `CGML-6.7-1` — PY-1
- `CGML-6.7-2` — PY-1
- `CGML-6.8-1` — PY-1
- `CGML-6.8-2` — PY-1
- `CGML-6.8-3` — PY-1
- `CGML-6.8-4` — PY-1
- `CGML-6.8-7` — PY-1
- `CGML-6.9-1` — PY-1
- `CGML-6.9-2` — PY-1
- `CGML-6.9-3` — PY-1
- `CGML-7.1-1` — PY-1
- `CGML-7.2-1-1` — PY-1
- `CGML-7.2-1-2` — PY-1
- `CGML-7.2-1-3` — PY-1
- `CGML-7.2-2` — PY-1
- `CGML-appendix-A-1` — PY-1
- `CGML-appendix-B-1` — PY-1

## Interoperability matrix

Cell: positive fixtures exchanged cleanly (writer → reader → canonical dump equals the golden dump) / total.

| writer \ reader | c | js | py |
|---|---|---|---|
| c | — | 0/19 | 0/19 |
| js | 0/19 | — | 0/19 |
| py | 0/19 | 0/19 | — |

