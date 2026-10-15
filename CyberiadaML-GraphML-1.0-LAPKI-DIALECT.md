# CyberiadaML-GraphML 1.0 — Lapki Dialect Specification

Companion to `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` (v1.9) and
`CyberiadaML-GraphML-1.0-VALIDATOR-SPEC.md` (v1.10). Informative: it describes the pre-standard
dialect written by the Lapki IDE (lapki-client through cyberiadaml-js 1.x) and read by
lapki-compiler (through cyberiadaml-py 1.x), and the normalisation a non-strict reader applies to
bring such a document to the standard model. It adds no requirement to the standard and changes no
verdict of `cgmlval`: a dialect document stays invalid.

**Document version:** 0.2 (2026-10-15)

## 1. Purpose

Three readers accept the dialect — libcyberiadaml (non-strict mode, partial), cyberiadaml-py and
cyberiadaml-js — and lapki-client keeps writing it until its library moves to the standard writer.
One definition and one corpus keep the readers normalising the same way:

- the patterns D-1…D-9 below, each a violation of the standard, with the repair;
- the findings a reader reports for each repair;
- the corpus of real dialect documents with their normalised canonical dumps (§6).

## 2. Reading pipeline

```
                       xmlload                 dialect pass               reader
  document    +----------------+  tree  +--------------------+  tree  +------------------+
  ----------> |  L1: XML parse | -----> |  D-1 ... D-9       | -----> |  L2 - L4, model  | --> model
              +----------------+        +--------------------+        +------------------+
                                                  |                            |
                                                  | LAPKI-D<n> findings        | CGML-* findings
                                                  v                            v
                                        +----------------------------------------------+
                                        |  document findings, format label             |
                                        +----------------------------------------------+
```

- **non-strict** reading runs the pass between L1 and L2; it rewrites the tree, the standard layers
  then see a repaired document;
- **strict** reading skips the pass; every pattern surfaces as its `CGML-*` error and the document
  is rejected;
- each pattern is a violation of the standard, so the pass changes nothing in a valid document and
  is safe to run on every non-strict read.

The reference implementation is `cgmlval/dialect.py`, run by `python3 -m cgmlval validate|dump
--dialect lapki FILE`. Its order: D-6, D-5, D-9, D-1 with the meta edges of D-2, D-2, D-7f, D-3,
D-7a, D-4 / D-7b / D-7d per node, D-7e / D-8b per machine — removals before renames, so no
finding names an element removed later.

## 3. Detection

The dialect has no marker: its `gFormat` is `Cyberiada-GraphML-1.0` or `Cyberiada-GraphML`. A
reader labels a document `Cyberiada-GraphML-Lapki` when any repair fired or any metadata node has
the `lapkiVisual` parameter (the Lapki IDE writes it, no other writer does). The label is reported,
never written: writers emit `Cyberiada-GraphML-1.0`.

## 4. Patterns and repairs

| D | pattern | repair | libcyberiadaml 91bc761 |
|---|---|---|---|
| 1 | several `CGML_META` nodes, or one outside the first machine; repeated, `undefined` or empty-version parameters | one document meta; the others become machine parameters | drops the others |
| 2 | component comment named `CGML_COMPONENT` with `id/` in the body; meta→component edges | `CGML_COMPONENT <id>`, edges removed | — |
| 3 | region graph id equal to a node id | `<node id>::region` | ✓ |
| 4 | `-1 × -1` rect on a point node; point on a rect node | point; loose rect | ✓ |
| 5 | undeclared `dLapki*` keys, a point inside them | implicit declaration, text value | — |
| 6 | `gFormat` without the version; not the first child | read as 1.0 | — |
| 7 | duplicate edge ids, `dNote` not first, empty `dNote`, no `edgedefault`, node ids repeated in a later machine | `#N` ids, reordered, `<graph id>::<id>` | — |
| 8 | `transitionOrder/transitionFirst`; machine without `dName` | `actionFirst`; graph id as name | — |
| 9 | top-level `dFunction` graphs (cyberiadaml-py 1.4+) | removed from the standard model | — |

### D-1 Several metadata nodes

- **Pattern:** more than one formal comment named `CGML_META`, or a `CGML_META` that is not at the
  top level of the first state machine. Written by cyberiadaml-js 1.1.6+ (one meta per machine,
  lapki-client id `coreMeta` repeated, `id=""` and `standardVersion/ undefined` on machines
  without own metadata) and by cyberiadaml-py 1.2+.
- **Repair:** the first `CGML_META` of the first machine — or, if that machine has none, the first
  one in document order — becomes the document metadata at the top level of the first machine.
  Every other `CGML_META` node is removed with the edges touching it; its parameters become the
  *machine parameters* of the machine it was in. In the document metadata a repeated parameter
  keeps its first occurrence (the reading rule of §6.9), parameters whose value is `undefined`
  are dropped, and a missing or empty `standardVersion` becomes `1.0` — lapki-client fills these
  from platform data that may be absent.
- **Machine parameters** are a reader-side notion: a reader exposes, per machine, its own
  parameters over the document ones (lapki-compiler takes `platform` and `platformVersion` per
  machine). A standard writer does not write them; a multi-platform project is several documents
  (§6.9.2 of the standard).

### D-2 Old component comments

- **Pattern:** a formal comment whose `dName`, with the surrounding blanks removed, is exactly
  `CGML_COMPONENT` and whose body has an `id` parameter; edges whose source is the id of a
  `CGML_META` node of any machine (the older component attachment — hand-copied machines keep
  the edges of the first one).
- **Repair:** the name becomes `CGML_COMPONENT <id>` (the trimmed `id` value); the `id` parameter
  is removed from the body, the other parameters keep their order; the meta→component edges are
  removed. A comment without `id` is left as it is and reported by the standard checks
  (`CGML-10.3-1`).

### D-3 Region graph id equal to a node id

- **Pattern:** a graph inside a node whose id equals the id of a node of the document (in practice
  the parent node; cyberiadaml-js copies the parent id).
- **Repair:** the id becomes `<parent id>::region`, or `<parent id>::region-<N>` with the smallest
  free `N` from 2 when taken — the libcyberiadaml naming.

### D-4 Geometry kinds

- **Pattern (a):** a rect with `width = -1` and `height = -1` on a node whose geometry is a point
  (`initial`, `final`, `terminate`, `shallowHistory`, `deepHistory`, `entryPoint`, `exitPoint`) —
  cyberiadaml-js stores a point as a rect of size -1 and writes it back so.
- **Pattern (b):** a point on a node whose geometry is a rect (state, comment, `choice`) —
  lapki-client writes comments with a point.
- **Repair:** (a) the point `(x, y)`; (b) the loose rect `(x, y, 0, 0)`, sized later by a
  geometry update if the application wants one. Both as libcyberiadaml.

### D-5 Private keys of the Lapki IDE

- **Pattern:** a `data` key whose id starts with `dLapki` that has no `key` declaration, or that
  carries a `point` or `rect` child. Known keys: `dLapkiSchemePosition` (a component node; the
  component position on the IDE scheme screen, a `point`) and `dLapkiNoteFormat` (a comment node;
  `bgColor/`, `fontSize/`, `textColor/` parameters as text).
- **Repair:** (a) the key is declared implicitly: `<key id="dLapki<X>" for="<element kind>"
  attr.name="lapki<X>" attr.type="string"/>`; (b) a single `point` child becomes the text value
  `x/ <x>` and `y/ <y>` separated by an empty line — the parameter syntax of §6.9. Readers keep
  the value as extension data of the element, standard writers write it back as a declared text
  key (§5.5 item 3).

### D-6 Format label

- **Pattern:** `gFormat` equal to `Cyberiada-GraphML`; `gFormat` not the first child of
  `graphml`.
- **Repair:** read as `Cyberiada-GraphML-1.0`; the position is ignored.

### D-7 Structural leniency

- **Pattern / repair:**
  - (a) a duplicate edge id inside a machine — the later edge gets `<id>#<N>`, the smallest free
    `N` from 1 (the template of §5.8.1);
  - (b) `dNote` not the first `data` of a comment — accepted; writers put it first;
  - (c) obsolete key declarations (`dInitial`) and declarations without `attr.name` — no repair:
    a declared non-standard key and a standard key without `attr.name` break no rule;
  - (d) an empty `dNote` — `informal`;
  - (e) a state machine graph without `edgedefault` — `directed`;
  - (f) a node id already used by an earlier machine (a component node `c<id>` of every machine,
    a hand-copied machine) — `<graph id>::<id>`, or `<graph id>::<id>-<N>` with the smallest
    free `N` from 2, the edges of that machine follow.

### D-8 Values

- **Pattern / repair:**
  - (a) `transitionOrder/transitionFirst` — `actionFirst`;
  - (b) a state machine without `dName`, or with an empty one — the graph id becomes its name.

### D-9 Function graphs

- **Pattern:** a top-level graph marked with `dFunction` instead of `dStateMachine` (data-flow
  functions of cyberiadaml-py 1.4+).
- **Repair:** the graph is removed from the standard model. cyberiadaml-py keeps it as an
  extension graph of its v1 interface; the other readers drop it with the finding.

## 5. Findings

Each repair reports one finding per occurrence, in the form of the validator (§3 of the validator
specification):

| field | value |
|---|---|
| rule | `lapki-d<n>`, `lapki-d<n><letter>` for the lettered cases: d1, d2, d3, d4a, d4b, d5a, d5b, d6, d7a, d7b, d7d, d7e, d7f, d8a, d8b, d9 |
| req | `LAPKI-D<n>` |
| layer | 0 (before L2) |
| severity | WARNING |
| message, line, column, path | as for the `CGML-*` findings |

Repair findings never stop reading. The standard layers run after the pass and report what the
repairs leave (e.g. the WARNING `CGML-7.2-1-5` on transition geometry in a `none`-mode document).

## 6. Corpus

```
fixtures/dialect/lapki/
  manifest.json            source repository, path, revision, writer, patterns per document
  <name>.graphml           the document as the IDE wrote it, byte for byte
  <name>.expected.txt      canonical dump (validator §7) of the normalised model
  <name>.repairs.txt       the expected LAPKI-D<n> findings: id and count, one per line
```

Sources (39 unique documents written by the Lapki tools plus one synthetic, duplicates by
content removed; the legacy yEd files of `lapki-compiler/examples/old/` and `авто.graphml` are
out of scope):

| source | documents | licence |
|---|---|---|
| lapki-client `resources/templates/`, `demos/` | 9 | GPL-3 |
| lapki-compiler `examples/` | 21 | GPL-3 |
| cyberiadaml-py `demos/` | 4 | LGPL-3 |
| cyberiadaml-js `demos/` (Lapki-written only) | 5 | LGPL-3 |
| libcyberiadaml `tests/diagrams/lapki-js.graphml` (synthetic) | 1 | LGPL-3 |

The expected files are produced by the reference implementation, `cgmlval` with the dialect pass
(`python3 -m cgmlval dump --dialect lapki FILE`), and reviewed by hand when recorded. Library test
suites take a snapshot of the corpus with its revision; the documents keep their licence there.

## 7. Reader conformance

A reader supports the dialect when, for every corpus document:

1. non-strict reading succeeds, the canonical dump equals `<name>.expected.txt`, and the repair
   findings equal `<name>.repairs.txt`;
2. writing the model gives a document `cgmlval` validates;
3. strict reading rejects it.

The dialect is not a profile of the testing specification: the harness report does not score it,
the library test suites and the `cgmlval` tests do.

## 8. Open items

- the text form of `dLapkiSchemePosition` (D-5) — to be confirmed with lapki-client, which is
  expected to write it directly once it moves to the standard writer;
- per-machine platforms of multi-machine Lapki projects (D-1) — the standard way is one document
  per platform;
- libcyberiadaml covers D-3, D-4 and part of D-1 (machine parameters dropped); the rest is a
  follow-up there.
