# CyberiadaML-GraphML 1.0 — Compatibility Harness Specification

Companion to `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` (v1.0),
`CyberiadaML-GraphML-1.0-TEST-CATALOG.md` (v1.2) and
`CyberiadaML-GraphML-1.0-VALIDATOR-SPEC.md` (v1.0). Specifies the conformance fixture corpus,
the implementation driver contract and the `intharness` runner that compares the CGML libraries
against the standard and against each other.

**Document version:** 1.1 (2026-08-23)

## 1. Purpose

The harness answers two questions per implementation:

- **conformance** — does the library read and write documents as the standard requires?
  (per-requirement verdicts, aggregated per profile CORE / EXT-*);
- **interoperability** — can documents written by one library be read by another?
  (the pairwise exchange matrix).

`cgmlval` is the single referee: every judgement is either a validation of a produced document
(layers L1–L4) or a comparison of canonical dumps (VALIDATOR-SPEC §7). Drivers never judge;
they only convert.

## 2. Architecture

```
 fixtures/                       corpus: documents + frozen golden dumps
   core/ geometry/ ext/ field/     positive fixtures  <name>.graphml
   negative/                       rejection fixtures X-<req>-<slug>.graphml
   manifest.json                   fixture -> requirements, twins, profiles
        |
        |            drivers/c  drivers/py  drivers/js     one executable per library
        |                 \         |         /
        v                  v        v        v
   +---------------------------------------------+
   |            intharness (Python)              |
   |  ch.1 dump equality   (round-trip == golden)|
   |  ch.2 validate output (cgmlval L1-L4)       |
   |  ch.3 reject protocol (negative fixtures)   |
   |  ch.4 twin dumps      (pairs dump equal)    |
   |  ch.5 interop         (A writes -> B reads) |
   +---------------------------------------------+
        |
        v
   REPORT.md + report.json          scoreboard, matrix, defect references
   <driver>.md per library          defect records for the developers
   results/<date>/                  committed snapshots
```

## 3. Fixture corpus

The positive fixtures transcribe the catalog's fixture table: `F-MIN`, `F-EMPTY-SM`, `F-TWO`,
`F-HIER`, `F-MULTI`, `F-FLAT`, `F-CMT` (core), `F-GEO-S`, `F-GEO-F` (geometry), `F-EXT-C`,
`F-EXT-D`, `F-EXT-P` (extensions), `F-FIELD-*` (real-world documents admitted after passing
L1–L4). Every positive fixture ships with its frozen golden dump `<name>.expected.txt`.

Golden dump policy: a dump is produced by `cgmlval dump`, reviewed line by line against the
standard, then committed and **frozen** — it is never regenerated to make a test pass; a
mismatch is a defect in the fixture, the validator or the reviewed dump, and the standard
decides which.

`manifest.json` is the machine-readable index:

```json
{
  "fixtures": {
    "core/F-MIN": {"profile": "CORE", "requirements": ["CGML-5.4-2", "..."]},
    "negative/X-5.4-2-wrong-format": {"reject": "CGML-5.4-2"}
  },
  "twins": [["core/F-MIN", "core/F-MIN-nokeys"]]
}
```

- `requirements` — the requirement ids a positive fixture exercises (from the catalog rows);
- `reject` — the requirement a negative fixture violates; the file carries exactly one fault;
- `twins` — fixture pairs that must produce byte-identical canonical dumps (declared vs
  appendix Б default keys, with vs without XML text comments, escaped vs raw characters).

## 4. Driver contract

A driver is one executable `drivers/<name>/driver` (any language). Commands:

    driver info
    driver convert IN.graphml OUT.graphml

- `info` prints one JSON object to stdout: `{"name": "...", "version": "...",
  "profiles": ["CORE", ...]}` — the profiles the library claims. Exit 0. A driver whose
  library is not built or importable exits non-zero from `info`; the harness records the
  library as **unavailable** and skips it.
- `convert` reads `IN.graphml` with the library, writes the loaded model back to
  `OUT.graphml` with the library's writer. Exit codes: `0` — success; `2` — the library
  rejected the input (one-line diagnostic on stderr); anything else — a **crash** verdict.
  The driver must not validate, normalize or repair beyond what the library itself does.

Drivers receive no other arguments; the harness controls timeouts (default 30 s per call)
and treats a timeout as a crash.

## 5. Channels and verdicts

For every available driver:

| # | Channel | Input | Judgement |
|---|---|---|---|
| 1 | dump equality | positive fixtures | `convert` succeeds and `cgmlval dump OUT` equals the golden dump |
| 2 | validate output | positive fixtures | `cgmlval validate OUT` reports no errors |
| 3 | reject protocol | negative fixtures | `convert` exits 2 (rejected); exit 0 = silently accepted, other = crash |
| 4 | twin dumps | twin pairs | both round-trips succeed and their `cgmlval dump` outputs are equal |
| 5 | interop | positive fixtures × driver pairs | A `convert` fixture → B `convert` A's output → dump of B's output equals the golden dump |

Channel results map to per-requirement verdicts through `manifest.json` and the requirement
table of `cgmlval.requirements`:

- **pass** — every channel run covering the requirement succeeded;
- **fail** — at least one covering run failed (the report lists the fixture, channel and
  the cgmlval findings or dump diff);
- **not-claimed** — the requirement's profile is outside the driver's `info` profiles;
  the fixture still runs and §2.1 tolerance applies: the library must not error on it;
- **not-tested** — no channel covers the requirement (the INTEGRATION-scoped rows:
  interpretation semantics need per-library probes, a later phase);
- **crash / unavailable** — propagated as such, never counted as pass or fail.

A requirement of sense [R] or [W] is covered by channels 1–2 (the round-trip observes the
composition read∘write; the harness does not attribute a failure to the reader or the writer);
sense [X] by channel 3.

## 6. Report

`python3 -m intharness run` executes the matrix and writes `report.json`;
`python3 -m intharness report --out-dir results/<date>/` renders the Markdown reports from it:
the summary `REPORT.md` plus one defect report `<driver>.md` per available library (§7).
The directory is committed as the certification evidence trail; `report.json` is not committed.

`REPORT.md` contains:

1. the run header — date, driver versions, fixture corpus revision;
2. per-library scoreboard — requirements by profile: passed / failed / blocked / not-claimed /
   not-covered / not-tested counts;
3. the failed requirement list — `CGML-<clause>-<n> — <defect id>`, each failure referencing
   the defect record that explains it;
4. the interop matrix — writers × readers, per-cell: fixtures exchanged cleanly / total.

## 7. Defect reports

The per-requirement view of §5 is the certification view; developers need the inverse: one
record per root cause. The renderer folds a driver's channel results into **clusters** keyed
by a signature:

| Channel result | Signature |
|---|---|
| positive fixture rejected | `reject:<stderr diagnostic>` |
| positive fixture crashed | `crash:<first diagnostic line>` |
| output validation error | `validate:<cited requirement id>` (one cluster per requirement) |
| dump difference | `dump:<expected line>|<got line>`, whitespace-stripped, numbers normalized to `#` |

Rejections with byte-identical diagnostics are indistinguishable to the harness and form one
cluster listing all affected fixtures. The dump signature is approximate by design — one root
cause can surface as several signatures; the registry below merges them. Accepted negative
fixtures are not clustered: they collapse into a single per-driver *missing rejections* table
(fixture, requirement, level).

**Registry.** `defects.json` at the repository root maps signatures to stable, hand-curated
records:

```json
{"defects": [
  {"id": "C-1", "driver": "c",
   "title": "writer declares dRegion with for=\"node\"",
   "note": "optional pointer for the developers",
   "signatures": ["validate:CGML-appendix-B-1"]}
]}
```

A cluster whose signature is listed takes the record's id and title; several signatures may
share one record. An unmatched cluster gets the provisional id `<DRIVER>-NEW-<n>` and is
flagged `unregistered` in the report — curating it into `defects.json` is part of accepting a
run. Ids are never renumbered; a fixed defect simply stops matching and drops out.

**Record.** Each defect record in `<driver>.md` carries:

- id and title;
- kind — `write` (dump difference or invalid output), `read` (a valid document rejected),
  `robustness` (crash);
- severity — from the highest violated requirement level: MUST → major, SHOULD → minor,
  MAY → info;
- the violated requirements with level, profile and the standard clause derived from the id;
- the channel, the affected fixtures, and the impact (requirements blocked by invalid output,
  the driver's interop rows);
- evidence — the cgmlval finding lines or the expected/got dump pair from one representative
  fixture;
- a reproduction command sequence using only the committed driver and fixtures.

## 8. Scope

Out of scope for this phase: the INTEGRATION-probe channel (a neutral-JSON `read` command
interrogating the library model), fixes to the libraries under test, drivers beyond the three
listed (libcyberiadamlpp shares the C writer — its results follow libcyberiadaml's), CI wiring,
performance measurement.
