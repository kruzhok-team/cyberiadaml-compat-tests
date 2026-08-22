# CyberiadaML-GraphML 1.0 — Document Validator Specification

Companion to `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` (v1.0) and
`CyberiadaML-GraphML-1.0-TEST-CATALOG.md` (v1.2). Specifies `cgmlval` — the standalone validator
implementing the catalog's document layers L1–L4 and the canonical dump used as the reference
output format by the later test harness.

**Document version:** 1.0 (2026-08-22)

## 1. Purpose

`cgmlval` checks a single CGML document bottom-up through the four catalog layers and reports
findings tied to the requirement identifiers `CGML-<clause>-<n>` of the testing specification.
After a document passes L1–L4 it can emit the canonical dump — the stable textual projection of
the document model that the catalog's type-A tests compare against.

The tool is pure Python 3 (standard library only), runnable in place:

    python3 -m cgmlval validate diagram.graphml

This document closes two open items of the test catalog (§5):

- **L2 tooling.** The catalog assumed an XSD/`xmllint` stack. XSD 1.0 cannot express the
  key-dependent content of the CGML tag tree (`data` content depends on its `key` attribute), and
  the validator must not require external tooling. L2 is therefore implemented as an internal
  walker over declarative tables transcribing the testing specification §2.8.1 tag tree. A schema
  export may be generated from the same tables later.
- **Canonical dump format.** Defined normatively in §7 below.

Out of scope (later phases): the test corpus F-MIN…F-FIELD-* and its reference dumps, the
integration harness and implementation drivers, per-profile certification reports, schema export.

## 2. Architecture

```
     cli.py                    xmlload.py                tagtree.py
    +----------------+        +----------------+        +----------------+
    |   validate /   | -file->|   L1: bytes,   | -tree->|  L2: tag tree  |
    |   dump / rules |        |   XML parse    |        |     walker     |
    +----------------+        +----------------+        +----------------+
            |                         |                         |
            | run                     | findings                | findings
            v                         v                         v
    +----------------+        +----------------+        +----------------+
    |    rules.py    |        |    model.py    | -model>|  checks_l3.py  |
    |   registry +   | -----> |    builder     |        |  checks_l4.py  |
    |     gating     |        | (actions, meta)|        +----------------+
    +----------------+        +----------------+                |
            |                         |                         | findings
            | verdict                 | model                   v
            v                         v                 +----------------+
    +----------------+        +----------------+        |  findings.py   |
    |  requirements  |        |    dump.py     |        |  text / JSON   |
    | CGML-* mapping |        | (L1-L4 clean)  |        |    reports     |
    +----------------+        +----------------+        +----------------+
```

- `cli.py` — argument parsing and the three subcommands; delegates to the layer runner.
- `xmlload.py` — L1: byte-level checks (encoding, declaration) and the well-formedness parse
  producing a position-annotated element tree.
- `tagtree.py` — L2: declarative admissible-tag-tree tables (testing spec §2.8.1) and the
  recursive walker checking tag placement, child order, first-key constraints and geometry
  sub-tag shapes.
- `model.py` — builds the document model from an L2-clean tree; uses `actions.py` (§6.8 behaviour
  text) and `meta.py` (§6.9 parameter text). Building records, it does not judge — rules do.
- `checks_l3.py`, `checks_l4.py` — value rules over the tree and integrity rules over the model.
- `rules.py`, `requirements.py`, `findings.py` — the rule registry with layer gating, the
  requirement table, and finding collection/rendering.
- `dump.py` — the canonical dump writer; runs only on a document with no L1–L4 errors.

## 3. Command line interface

    python3 -m cgmlval validate [--strict] [--json] FILE...
    python3 -m cgmlval dump [--json] FILE
    python3 -m cgmlval rules [--json]

Exit codes: `0` — no errors (dump emitted); `1` — errors found (with `--strict`: errors or
warnings); `2` — usage or input/output failure.

Text finding line:

    file.graphml:12:5: ERROR CGML-5.4-2 [L3] gFormat value must be "Cyberiada-GraphML-1.0" (at /graphml/data[key=gFormat])

`--json` emits one object per file: `{"file", "verdict", "layers_run", "findings": [{"rule",
"req", "layer", "severity", "message", "line", "column", "path"}]}`. `dump` prints the
validation report and exits `1` instead of dumping when the document has errors. `rules` lists
the registry: check name, requirement, layer, level, profile, severity, title.

When source positions are unavailable the `line:column` part is omitted and only the element
path locates the finding.

## 4. Validation pipeline

Layers run in order L1 → L2 → L3 → L4. An **error** at layer N stops the layers above N (the
report names the layers not evaluated); warnings never gate. The severity of every check is
fixed at registration:

| Severity | Assigned to | Effect |
|---|---|---|
| ERROR | MUST violations the catalog marks "rejected" | fails validation, gates higher layers |
| WARNING | catalog "rejected or reported" rows; SHOULD deviations | reported; fails only under `--strict` |
| INFO | MAY-level observations (e.g. edge-id template) | reported |

`--strict` changes the exit code only — the report text is identical with and without it.

Warning-level rows include: non-UTF-8 encoding, `edgedefault` other than `directed`, edge tags
not in a trailing block, duplicate `else` triggers, reserved `fork`/`join` vertices, and the
geometry-mode consistency rows of §7.2.

## 5. Rules and requirement mapping

Every check registers with the rule registry:

    @rule("gformat-value", req="CGML-5.4-2", layer=3, severity=ERROR,
          title='gFormat value must be "Cyberiada-GraphML-1.0"')

- The rule name identifies the check; `req` names exactly one requirement (a requirement may
  have several rules). Level (MUST/SHOULD/MAY) and profile come from the requirement table,
  never duplicated in the rule.
- L1 and L2 are each implemented as one walker emitting findings under several registered rule
  names; such names register without a callable so listing and coverage audit still see them.
- `requirements.py` transcribes all requirement identifiers of the testing specification with
  level, senses, profile and a scope class: `validator` (checkable on a document — the union of
  the catalog's L1–L4 rows), `integration` (implementation behaviour, INT layer), `write-only`
  ([W]-sense only). The self-test suite asserts that every `validator`-scoped requirement has at
  least one rule and that no rule cites a requirement outside the validator scope.

## 6. Document model

Built after L2 passes. Element kinds mirror the standard's Table 2:

- `Document` — format string, key declarations, state machines, resolved metadata,
  geometry mode;
- `StateMachine` — id, name, formal name, geometry, children, transitions, comment links;
- children: `State` (regions, actions), `Vertex` (kind per Table 3), `Comment` (informal/formal,
  verbatim body), `SubmachineState` (reference); `Region` holds nested children;
- `Transition` — endpoints, actions, polyline, source/target points, label geometry, color;
  `CommentLink` — endpoints, pivot, chunk;
- geometry values `Point(x, y)` and `Rect(x, y, width, height)`, real numbers.

An edge whose first data key is `dPivot` is a comment link; any other edge is a transition.

**Behaviour text (§6.8).** `dData` splits into blocks on blank lines; each block's first line is
either `entry/`, `exit/`, `do/` or `Trigger [Guard]/` where the trigger is preserved verbatim
(platform syntax is not validated) and may end with one of the event parameters `propagate`,
`block`, `defer`. The guard is delimited by the last unescaped `[`…`]` pair before the trailing
`/`; `\[` and `\]` inside it denote literal brackets; the guard `else` is recognized. Remaining
block lines are behaviour lines, order preserved. An empty `dData` is zero blocks. Resolved
ambiguity: one optional space is consumed after the header's closing `/`, none is required.

**Metadata text (§6.9).** The `dData` of a formal comment splits into chunks on blank lines;
each chunk is `name/ value` — the name up to the first `/`, one optional space consumed, the
rest of the chunk (including continuation lines) is the value. The same grammar parses
`CGML_COMPONENT` bodies (§10.3). Resolved ambiguity: parameter order is preserved; a repeated
parameter name is reported at L3 and the first occurrence wins.

## 7. Canonical dump format

Normative for reference dumps of the later phases. Line-oriented UTF-8 text, two-space
indentation, one logical item per line. Deterministic: the same model always renders the same
bytes.

- First line: `cgml-canonical-dump 1`.
- Strings are double-quoted; escapes: `\\`, `\"`, `\n`, `\t`, `\r`, `\u00XX` for other control
  characters; all other characters (including non-ASCII) verbatim.
- Numbers render as fixed two-decimal text (`%.2f`, round-half-even), `-0.00` normalized to
  `0.00` — the textual form of the catalog's 0.01 coordinate tolerance.
- Ordering: state machines and every element container sort by id (byte order); transitions and
  comment links sort by (source, target, id); behaviour blocks and metadata parameters keep
  document order (their order is semantic).
- Key declarations and data-key order are not dumped: a document relying on the appendix Б
  defaults and its explicitly-declared twin produce identical dumps.
- Absent optional values are omitted. The resolved values of `geometry`, `transitionOrder`,
  `eventPropagation` and comment markup are materialized in the header/element lines; the raw
  metadata parameters are also listed.
- Formal comment bodies dump verbatim as one quoted string; state and transition behaviour dumps
  as parsed blocks.

Example:

```
cgml-canonical-dump 1
format: "Cyberiada-GraphML-1.0"
geometry-mode: short
transition-order: actionFirst
event-propagation: block
meta:
  param "standardVersion": "1.0"
  param "geometry": "short"
state-machine "g1":
  name: "Мигалка"
  geometry: rect 0.00 0.00 400.00 300.00
  comment "cMeta" formal:
    name: "CGML_META"
    body: "standardVersion/ 1.0\n\ngeometry/ short"
  state "n1":
    name: "Off"
    action entry:
      do: "LED.off()"
    geometry: rect 20.00 40.50 120.00 60.00
    region "n1:":
      state "n1a":
        name: "Deep Off"
        geometry: rect 10.00 10.00 80.00 30.00
  vertex "v0" initial:
    geometry: point 10.00 10.00
  transition "v0-n1#1": "v0" -> "n1"
  transition "n1-n1#1": "n1" -> "n1"
    action event "TIMER(100)" propagate guard "cnt > 0":
      do: "blink()"
      do: "cnt -= 1"
    label-geometry: point 60.00 33.00
```

Further element lines follow the same `key: value` shape: `formal-name:`, `color:`, `markup:`,
`collapsed`, `submachine "id" ref "…"`, `polyline: point … point …`, `source-point:` /
`target-point:`, `comment-link "id": "src" -> "dst" pivot "dName" chunk "…"`. An `else` guard
renders as `guard "else"`; escaped guard brackets render re-escaped (`\[`, `\]`) inside the
quoted guard.

## 8. Self-tests

The validator's own suite (pytest, `tests/`) contains: table-driven unit tests of the two text
parsers; per-rule accept/reject pairs derived from a single minimal base document with exactly
one mutation per rejection case; end-to-end dumps of complete example documents compared against
hand-written expected dumps (derived from the standard, frozen, never regenerated to make a test
pass); the registry-coverage audit of §5; and a report-only smoke run over the sample corpora of
the sibling repositories.
