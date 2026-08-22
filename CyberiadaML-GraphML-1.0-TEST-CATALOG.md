# CyberiadaML-GraphML 1.0 — Conformance Test Catalog

Companion to `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` (v1.0). Enumerates the tests required to
check every requirement of the testing specification and organizes the testing procedure into
validation layers built on widely available tools. Implementation of these tests on the
available libraries is planned separately.

**Document version:** 1.2 (2026-07-19)

## 1. Testing layers

A CGML document is checked bottom-up through four validation layers. Each layer relies on a
standard, widely available tool class, catches its own class of faults, and is a precondition for
the next: a document failing layer N is not examined at layers above N. Implementation
(integration) testing — how libraries and tools read, write, and round-trip documents — sits on
top of the four document layers and reuses their fixtures.

| Layer | Name | What is checked | Tooling |
|---|---|---|---|
| **L1** | XML compatibility | well-formed XML; UTF-8 encoding and declaration; character escaping; XML comments tolerance | any standard XML parser (`xmllint --noout`, expat, libxml2, `fast-xml-parser`, `xml.etree`) |
| **L2** | Document structure | GraphML skeleton; the CGML tag tree (spec 2.8.1): admissible tags, their nesting and order; geometry sub-tags | GraphML XML Schema + a CGML structural schema (XSD or RelaxNG) generated from the tag tree; `xmllint --schema` |
| **L3** | Attributes and values | key declarations (spec 2.8.2); attribute presence and formats; enumerated values (`gFormat`, `dVertex`, `dNote`, geometry mode, colors, markup); identifier and formal-name syntax; `dData` and metadata text syntax | rule-based validation over the parsed tree: Schematron / XPath assertions / small rule scripts |
| **L4** | Document integrity | cross-element consistency: identifier uniqueness, edge endpoint resolution, name uniqueness, element-count constraints, metadata presence, geometry-mode consistency, reference resolution | custom integrity checker (graph analysis over the parsed document) |
| **INT** | Integration | implementations under test: parse (A), reject (X), write (W), round-trip (RT) against the layered fixtures and golden models | test harness driving the implementations |

Design rules that follow from the layering:

- every **invalid fixture** carries exactly one fault, assigned to exactly one layer — so a
  failure names both the violated requirement and the layer where detection belongs;
- an implementation may legitimately detect a fault at a lower layer than listed (e.g. reject an
  L3 fault while parsing), but must not *accept* a document that carries a fault at or below the
  layer it claims to validate;
- L1–L4 are also the blueprint of the suite's own standalone document validator: L1–L2 come
  almost for free from existing XML tooling, only L3–L4 require CGML-specific code.

## 2. Conventions

**Test identifiers**: `T-<clause>-<req>.<k>` — e.g. `T-5.4-1.2` is the 2nd test of requirement
`CGML-5.4-1`. Every test row names the requirement it checks and the layer it belongs to; every
requirement of the spec is covered by at least one test.

**Test types**

| Type | Meaning | Pass criterion |
|---|---|---|
| **A** (accept) | implementation parses a valid fixture | no error; canonical projection equals the fixture's golden model |
| **X** (reject) | implementation reads an invalid fixture | error/rejection reported; no crash or hang |
| **W** (write) | implementation writes a document (usually via round-trip parse→write) | output independently passes layers L1–L4 |
| **RT** (round-trip) | parse → write → parse | canonical projection preserved (equality level per §2.1) |
| **I** (informational) | SHOULD/MAY-level behavior | recorded in the report as warning/info, never a failure |

**Golden-file convention**: each type-A test compares the implementation's parse result,
projected to a stable textual canonical dump, against a golden file stored next to the fixture
(`<fixture>.expected.txt`). Golden files are derived from the standard by hand, reviewed once,
then frozen; no implementation output is ever used as the source of a golden file.

### 2.1 Equality levels for round-trips

| Level | Meaning | Used for |
|---|---|---|
| `identical` | same structure, same identifiers, same geometry | RT within one implementation when no id regeneration is documented |
| `equal` | same structure and names, ids may differ | default RT acceptance |
| `isomorphic` | same graph shape; names/actions may differ | diagnostic only, never a pass |

Coordinate comparison policy: geometry values compare with a documented tolerance (rounding to
0.01 by default) — implementations may legitimately round or reformat coordinates, so exact
floating-point equality is not portable.

### 2.2 Shared fixtures

Single-fault mutation principle: every invalid fixture differs from a valid base in exactly one
respect, named in its test row.

| Fixture | Content |
|---|---|
| `F-MIN` | minimal CORE document: `graphml` + `gFormat` + Appendix Б key block + one SM (`dStateMachine`, `dName`, `CGML_META` with `standardVersion/ 1.0`) + initial pseudostate + one state + one transition |
| `F-EMPTY-SM` | document whose single SM contains no elements (valid) |
| `F-TWO` | `F-MIN` + second state and transition with trigger/guard/behavior |
| `F-HIER` | composite state with one region, child states, child transitions at top level |
| `F-MULTI` | two state machines at top level |
| `F-GEO-S` | `F-TWO` with `geometry/ short` and full base geometry on all elements, incl. negative and fractional coordinates |
| `F-GEO-F` | `F-GEO-S` with `geometry/ full`, edge polylines, source/target points, label rects, a self-loop with polyline |
| `F-FLAT` | flattened-hierarchy document: states whose ids encode former nesting (`n0::n1`), no composite nodes |
| `F-EXT-C` | EXT-COMPLETENESS features: submachine, histories, entry/exit points, collapsed composite, comment link to transition |
| `F-EXT-D` | EXT-DISPLAY features: colors, markup |
| `F-EXT-P` | EXT-PLATFORM features: formal names, `CGML_COMPONENT` |
| `F-CMT` | comments (informal + formal) with subject links (`dPivot`/`dChunk`) |
| `F-FIELD-*` | real-world documents collected from the ecosystem (converted legacy diagrams, IDE-produced files, generator examples) — admitted after passing L1–L4 |

**Cross-cutting suites** (run automatically, not listed per requirement):
- `RT-ALL`: every valid fixture round-trips through every writing implementation; canonical model preserved at level `equal` or better.
- `VAL-OUT`: every file written by an implementation passes the L1–L4 validation stack.
- `TOL-EXT`: every CORE-only implementation reads every `F-EXT-*` fixture without error, preserving core content (spec §2.1).
- `GEO-AGNOSTIC`: every geometry-bearing fixture is also read in geometry-ignoring mode where the implementation supports one; the resulting topology must equal the geometry-aware read. Implementations without such a mode: `not-applicable`.
- `FIELD`: every `F-FIELD-*` document is read by every implementation; canonical projections must agree with the golden model.

## 3. Test list by layer

### 3.1 Layer L1 — XML compatibility

| Test | Req | Type | Fixture / action → expectation |
|---|---|---|---|
| T-5.1-1.1 | CGML-5.1-1 | A | `F-MIN` with Cyrillic names/behaviors in UTF-8 → parsed intact |
| T-5.1-1.2 | CGML-5.1-1 | X | `F-MIN` re-encoded UTF-16 (declared) → rejected or reported |
| T-5.1-1.3 | CGML-5.1-1 | W | written output is valid UTF-8 with correct declaration |
| T-5.1-2.1 | CGML-5.1-2 | A | proper root + xmlns → parsed |
| T-5.1-3.1 | CGML-5.1-3 | A | extra namespace attribute on `graphml` → parsed, ignored |
| T-5.2-1.1 | CGML-5.2-1 | A | `dName` = `&quot;Имя&quot;`, guard with `&gt;=` → unescaped values in model |
| T-5.2-1.2 | CGML-5.2-1 | RT | state name containing `< > & " '` → written escaped, re-read identical |
| T-5.3-1.1 | CGML-5.3-1 | A | XML comments inside `graphml`, inside `graph`, inside `node`, between edges → all ignored, parse OK |
| T-6.8-7.1 | CGML-6.8-7 | X | raw `&&` in guard (unescaped `&`) → rejection at XML level |
| T-X-1.1 | — | X | truncated file (unclosed tag); binary junk; empty file (3 variants) → rejected, no crash |

### 3.2 Layer L2 — Document structure (tag tree)

| Test | Req | Type | Fixture / action → expectation |
|---|---|---|---|
| T-5.1-2.2 | CGML-5.1-2 | X | root tag `<graph>` instead of `<graphml>`; missing xmlns → rejected |
| T-5.4-1.1 | CGML-5.4-1 | A | `gFormat` first child of `graphml` → parsed |
| T-5.4-1.2 | CGML-5.4-1 | X | `gFormat` absent → rejected |
| T-5.4-1.3 | CGML-5.4-1 | X | `gFormat` after the `key` block → rejected |
| T-5.4-1.4 | CGML-5.4-1 | W | written documents place `gFormat` first |
| T-5.5-1.1 | CGML-5.5-1 | A | full Appendix Б declaration block before graph structure → parsed |
| T-5.5-1.2 | CGML-5.5-1 | W | written key declarations appear before graph structure |
| T-5.6-3.1 | CGML-5.6-3 | X | subgraph directly inside `graph` (not via node) → rejected |
| T-5.7-1.1 | CGML-5.7-1 | X | `node` as direct child of `graphml` → rejected |
| T-5.7-2.1 | CGML-5.7-2 | A | `F-HIER` node with nested graph → composite state |
| T-5.8-3.1 | CGML-5.8-3 | X | edge placed between two nodes → rejected or reported |
| T-5.8-3.2 | CGML-5.8-3 | W | written edges form a single trailing block |
| T-6.1-1.2a | CGML-6.1-1 | X | `dStateMachine` not the first key of the SM graph → rejected |
| T-6.1-4.1 | CGML-6.1-4 | X | data key after first node in SM graph → rejected |
| T-6.4-1.1 | CGML-6.4-1 | X | vertex node with `dName` before `dVertex` → rejected |
| T-6.5-1.1 | CGML-6.5-1 | A | `F-HIER` → children attached to composite via region subgraph |
| T-6.5-2.1 | CGML-6.5-2 | A | region graph with empty `dRegion`; node with **two** region subgraphs → parsed (2 fixtures) |
| T-6.5-4.1 | CGML-6.5-4 | X | edge inside region subgraph → rejected |
| T-6.6-1.2a | CGML-6.6-1 | X | `dNote` not the first key of a comment node → rejected |
| T-6.7-1.2 | CGML-6.7-1 | X | `dPivot` not the first key of the link edge → rejected |
| T-A-1.1 | CGML-appendix-A-1 | X | unknown tag inside `graphml` (`<foo>`) → rejected |
| T-A-1.2 | CGML-appendix-A-1 | X | key on the wrong element kind: `dVertex` on a graph; `dRegion` on a node; `dPivot` on a node (3 variants) → rejected |
| T-A-1.3 | CGML-appendix-A-1 | X | geometry sub-tag misuse: `rect` inside `data<dSourcePoint>` → rejected |
| T-7.2-2.3 | CGML-7.2-2 | X | `rect` missing `width`; `point` missing `y` (2 variants) → rejected |

### 3.3 Layer L3 — Attributes and values

| Test | Req | Type | Fixture / action → expectation |
|---|---|---|---|
| T-5.4-2.1 | CGML-5.4-2 | X | `gFormat` value `Cyberiada-GraphML-2.0` → rejected |
| T-5.4-2.2 | CGML-5.4-2 | X | empty `gFormat` value → rejected |
| T-5.5-2.1 | CGML-5.5-2 | A | no key block → defaults of Appendix Б applied (doc parses identically to declared twin) |
| T-5.5-3.1 | CGML-5.5-3 | X | `data` tag without `key` attribute → rejected |
| T-5.6-1.1 | CGML-5.6-1 | X | graph without `id` → rejected |
| T-5.6-1.2 | CGML-5.6-1 | X | `edgedefault="undirected"` → rejected or reported |
| T-5.8-1.1 | CGML-5.8-1 | X | edge missing `source` (or `target`, or `id`, or empty ones — 4 variants) → rejected |
| T-5.8-2.1 | CGML-5.8-2 | I | written edge ids follow `source-target#N` → informational |
| T-5.9-1.1 | CGML-5.9-1 | X | missing `id` on graph/node/edge (3 variants) → rejected |
| T-5.9-2.1 | CGML-5.9-2 | A | ids using `- _ # ! ~` and hierarchical `n0::n1` (`F-FLAT`) → accepted |
| T-5.9-2.2 | CGML-5.9-2 | X | id with space; with `"`; with `\`; with Cyrillic (4 variants) → rejected |
| T-5.9-3.1 | CGML-5.9-3 | A | 256-char id; ids `n1` vs `N1` coexist → accepted, distinct |
| T-5.9-3.2 | CGML-5.9-3 | X | empty id; 257-char id (2 variants) → rejected |
| T-6.1-1.2b | CGML-6.1-1 | X | `dStateMachine` with non-empty value → rejected |
| T-6.4-2.2 | CGML-6.4-2 | X | `dVertex` value `banana` → rejected |
| T-6.6-1.2b | CGML-6.6-1 | X | `dNote` value `casual` → rejected |
| T-6.8-1.1 | CGML-6.8-1 | A | transition `Trigger [Guard]/ behavior` → trigger/guard/behavior separated correctly |
| T-6.8-1.2 | CGML-6.8-1 | A | empty `dData` → no behavior, no error |
| T-6.8-1.3 | CGML-6.8-1 | A | trigger with guard and empty behavior list; `entry/` with empty body (2 fixtures) → accepted |
| T-6.8-2.1 | CGML-6.8-2 | A | two blocks split by blank line → two behavior entries |
| T-6.8-3.1 | CGML-6.8-3 | A | `entry/`, `exit/`, `do/` blocks → recognized as the three behavior kinds |
| T-6.8-3.2 | CGML-6.8-3 | A | multiple `entry/` + event + `exit/` blocks in one state (order preserved) → parsed |
| T-6.8-4.1 | CGML-6.8-4 | A | exotic event names (dots, arguments `EVENT(b)`, Unicode) → preserved verbatim, not validated |
| T-6.8-5.1 | CGML-6.8-5 | A | events with `propagate` / `block` / `defer` → parameters preserved |
| T-6.8-6.1 | CGML-6.8-6 | A | `[else]` guard → recognized |
| T-6.8-8.1 | CGML-6.8-8 | RT | guard `[Строка.Содержит(\[Пример\])]` → backslash-escaped brackets preserved |
| T-6.9-2.1 | CGML-6.9-2 | A | multi-line parameter value (`description` = three lines); blank-line separation → parsed to pairs |
| T-6.9-2.2 | CGML-6.9-2 | X | parameter name with non-Latin characters → rejected or reported |
| T-6.9-3.1 | CGML-6.9-3 | X | `standardVersion` missing; value `2.0` (2 variants) → rejected |
| T-6.9-4.1 | CGML-6.9-4-1 | A | `geometry` absent → `none` assumed; `short`; `full` (3 fixtures) |
| T-6.9-4.2 | CGML-6.9-4-1 | X | `geometry/ big` → rejected |
| T-6.9-4.3 | CGML-6.9-4-2 | A | text parameters (platform, name, author, contact, version, target) preserved |
| T-6.9-4.4 | CGML-6.9-4-3 | A | `createdAt` ISO 8601 UTC value preserved |
| T-6.9-4.5 | CGML-6.9-4-4 | A | paired fixtures: explicit `exitFirst` and absent parameter → default `actionFirst` |
| T-6.9-4.6 | CGML-6.9-4-5 | A | paired fixtures: explicit `propagate` and absent parameter → default `block` |
| T-6.9-4.7 | CGML-6.9-4-5 | X | `eventPropagation/ defer` → rejected (valid only per-event in `dData`, cf. CGML-6.8-5) |
| T-6.9-4.8 | CGML-6.9-4-6 | A | `markupLanguage/ markdown` → recorded as document default |
| T-6.9-5.1 | CGML-6.9-5 | A | custom parameter `myParam/ value` → preserved |
| T-7.2-2.1 | CGML-7.2-2 | A | negative and fractional coordinates (incl. high-precision values) → values in model within tolerance |
| T-9.2-1.1 | CGML-9.2-1 | A | `dColor` `#RRGGBB`, `#RRGGBBAA`, named `red` on node and edge → parsed |
| T-9.2-1.2 | CGML-9.2-1 | X | empty `dColor` value → rejected or reported |
| T-9.3-1.1 | CGML-9.3-1 | A | `dMarkup` = `markdown` on informal comment; absent → default `plain` |
| T-10.1-2.1 | CGML-10.1-2 | A | formal names `_x`, `Scan9`, `A_b_1` → accepted |
| T-10.1-2.2 | CGML-10.1-2 | X | formal name starting with digit; containing dash; Cyrillic; empty (4 variants) → rejected |
| T-B-1.1 | CGML-appendix-B-* | X | standard key redeclared with different `for`/`attr.name` → rejected |
| T-B-1.2 | CGML-appendix-B-* | A | document declaring only the subset of keys it uses → accepted |

### 3.4 Layer L4 — Document integrity

| Test | Req | Type | Fixture / action → expectation |
|---|---|---|---|
| T-5.5-4.1 | CGML-5.5-4 | X | node with two `dName` data tags → rejected |
| T-5.6-2.2 | CGML-5.6-2 | X | document with zero top-level graphs → rejected |
| T-5.9-4.1 | CGML-5.9-4 | X | same id on two nodes in different SMs; node id equal to region graph id (2 variants) → rejected |
| T-5.9-4.2 | CGML-5.9-4 | X | duplicate edge id → rejected |
| T-6.1-1.1 | CGML-6.1-1 | X | top-level graph without `dStateMachine` → rejected |
| T-6.1-2.1 | CGML-6.1-2 | X | SM without `dName`; with empty `dName`; two SMs with equal names (3 variants) → rejected |
| T-6.2-3.1 | CGML-6.2-3 | X | two sibling states named `A` → rejected |
| T-6.2-3.2 | CGML-6.2-3 | A | same name on different hierarchy levels → accepted |
| T-6.3-2.1 | CGML-6.3-2 | X | edge with nonexistent `source`; `target` in the other SM of `F-MULTI` (2 variants) → rejected |
| T-6.3-2.2 | CGML-6.3-2 | X | edge whose `source` or `target` is the SM graph id itself (2 variants) → rejected |
| T-6.3-4.1 | CGML-6.3-4 | X | two `[else]` transitions from one state → rejected or reported |
| T-6.3-5.1 | CGML-6.3-5 | X | edge label geometry while an endpoint node has none (short mode) → rejected or reported |
| T-6.4-4-1.1 | CGML-6.4-4-1 | X | two `initial` on the same level → rejected |
| T-6.4-4-1.2 | CGML-6.4-4-1 | A | `initial` at SM level and inside a region → accepted |
| T-6.4-4-2.1 | CGML-6.4-4-2 | X | choice with two `[else]` outgoing transitions → rejected or reported |
| T-6.7-2.1 | CGML-6.7-2 | X | comment link to nonexistent node → rejected |
| T-6.9-1.1 | CGML-6.9-1 | X | no `CGML_META` node; meta only in second SM (2 variants) → rejected |
| T-7.1-1.1 | CGML-7.1-1 | A | `F-MIN` (none), `F-GEO-S` (short), `F-GEO-F` (full) → mode detected correctly |
| T-7.2-1.2 | CGML-7.2-1-5 | X | edge `dGeometry` present in a `short`-mode document → rejected or reported |
| T-7.2-1.3 | CGML-7.2-1-* | X | wrong geometry object kind: point on a state; rect on an initial (2 variants) → rejected or reported |
| T-8.5-2.1 | CGML-8.5-2 | X | plain transition (no `dPivot`) targeting an edge id → rejected |
| T-10.1-3.1 | CGML-10.1-3 | X | duplicate SM formal names; duplicate sibling-state formal names (2 variants) → rejected |

### 3.5 Integration tests (implementations under test)

Positive parsing, writing, and round-trip behavior over the full fixtures; runs only on documents
that pass L1–L4.

| Test | Req | Type | Fixture / action → expectation |
|---|---|---|---|
| T-5.5-2.1i | CGML-5.5-2 | A | declared/undeclared key-block twins parse to identical models |
| T-5.6-2.1 | CGML-5.6-2 | A | `F-MULTI` → two SMs in model |
| T-6.1-3.1 | CGML-6.1-3 | A | SM `dGeometry` rect in `F-GEO-S` → parsed |
| T-6.1-5.1 | CGML-6.1-5 | A | `F-MULTI` names/content of both SMs correct |
| T-6.1-5.2 | CGML-6.1-5 | A | `F-EMPTY-SM` — SM with zero elements → accepted |
| T-6.1-5.3 | CGML-6.1-5 | RT | `F-EMPTY-SM` round-trip → still valid, meta preserved |
| T-6.2-1.1 | CGML-6.2-1 | A | plain node → simple state in model |
| T-6.2-2.1 | CGML-6.2-2 | A | state without `dName`; two unnamed siblings → both accepted as unnamed |
| T-6.2-4.1 | CGML-6.2-4 | A | state `dData` with entry/exit blocks → parsed per 6.8 |
| T-6.2-5.1 | CGML-6.2-5 | A | state rect geometry → parsed |
| T-6.3-1.1 | CGML-6.3-1 | A | edge without `dData` → triggerless transition |
| T-6.3-3.1 | CGML-6.3-3 | A | self-loop edge → accepted |
| T-6.4-2.1 | CGML-6.4-2 | A | one fixture per core value `initial`/`final`/`choice`/`terminate` → correct vertex kind |
| T-6.4-2.3 | CGML-6.4-2 | A | `dVertex` = `fork` → tolerated on read as unknown vertex |
| T-6.4-2.4 | CGML-6.4-2 | W | no written document ever contains `fork`/`join` |
| T-6.4-3.1 | CGML-6.4-3 | A | named pseudostate; point geometry on initial/final; rect on choice → parsed |
| T-6.5-3.1 | CGML-6.5-3 | I | written region ids use `parent:` convention → informational |
| T-6.5-4.2 | CGML-6.5-4 | A | child-state transitions at top level → correctly resolved to nested endpoints |
| T-6.6-1.1 | CGML-6.6-1 | A | informal and formal comments (`F-CMT`) → correct kinds |
| T-6.6-2.1 | CGML-6.6-2 | A | comment with body, title, rect geometry → parsed |
| T-6.6-3.1 | CGML-6.6-3 | I | formal comment body byte-identical after round-trip → informational (SHOULD) |
| T-6.7-1.1 | CGML-6.7-1 | A | comment link with `dPivot` = `dName` / `dData` → parsed as link, not transition |
| T-6.7-3.1 | CGML-6.7-3 | A | link with `dChunk` substring → parsed |
| T-6.8-2.2 | CGML-6.8-2 | RT | multi-block `dData` with multi-line behaviors → block structure preserved |
| T-6.9-1.2 | CGML-6.9-1 | A | meta on an otherwise empty SM (`F-EMPTY-SM`) → all parameters readable |
| T-7.2-1.1 | CGML-7.2-1-1…4,6 | A | `F-GEO-S`: rect on SM/state/choice/comment/region; point on initial/final; label point and rect → all parsed with correct object kinds |
| T-7.2-2.2 | CGML-7.2-2 | RT | coordinates preserved through round-trip within the §2.1 tolerance |
| T-7.2-3.1 | CGML-7.2-3 | A | element without `dGeometry` in short doc → flagged non-visualized; children of a geometry-less composite → hidden |
| T-8.1-1.1 | CGML-8.1-1 | A | submachine node with `file://` reference → parsed, reference preserved |
| T-8.1-1.2 | CGML-8.1-1 | A | internal SM reference → resolved within document |
| T-8.1-1.3 | CGML-8.1-1 | I | unresolvable external reference → tolerated on parse, reported |
| T-8.2-1.1 | CGML-8.2-1 | A | `shallowHistory` and `deepHistory` vertexes → correct kinds |
| T-8.2-2.1 | CGML-8.2-2 | A | history inside a region and at SM level → accepted |
| T-8.3-1.1 | CGML-8.3-1 | A | `entryPoint`/`exitPoint` vertexes → correct kinds |
| T-8.3-2.1 | CGML-8.3-2 | A | entry/exit points inside a state, at SM level, adjacent to a submachine state → accepted |
| T-8.4-1.1 | CGML-8.4-1 | A/RT | `dCollapsed` composite with region → parsed; flag survives round-trip |
| T-8.5-1.1 | CGML-8.5-1 | A | comment link (`dPivot` present) targeting an edge id → parsed as link-to-transition |
| T-9.1-1.1 | CGML-9.1-1 | A | `F-GEO-F`: edge polyline points, `dSourcePoint`, `dTargetPoint`, label rect → parsed |
| T-9.1-2.1 | CGML-9.1-2 | W | full-mode writer output contains complete geometry (L1–L4 check) |
| T-9.3-2.1 | CGML-9.3-2 | A | `markupLanguage` metadata default applied to comments without own `dMarkup` |
| T-10.1-1.1 | CGML-10.1-1 | A | `dFormalName` on a node and on an SM graph → parsed |
| T-10.2-1.1 | CGML-10.2-1 | RT | formal comment body (init data) preserved verbatim |
| T-10.3-1.1 | CGML-10.3-1 | A | `CGML_COMPONENT` comment with `id/ type/ name/` params → parsed to component description |

Plus the cross-cutting suites of §2.2 (`RT-ALL`, `VAL-OUT`, `TOL-EXT`, `GEO-AGNOSTIC`, `FIELD`).

## 4. Coverage summary

- Requirements in the testing spec: **101** (all covered; sub-groups covered via their parent or item tests).
- Test rows: **~130**, ≈ 165 concrete cases counting multi-variant rows.
- By layer: L1 = 10, L2 = 24, L3 = 47, L4 = 22, INT = 42 rows (+5 cross-cutting suites).
- By type: A ≈ 68, X ≈ 58 (every MUST with an [X] sense has at least one rejection test at exactly one layer), RT/W ≈ 22, I = 5.
- Requirements checked at two layers get split ids (`T-6.1-1.2a` structure / `T-6.1-1.2b` value).

## 5. Open items for the implementation phase

- Source of the L2 schema: adapt the official GraphML XSD and generate the CGML tag-tree
  constraints (XSD 1.0 cannot express key-dependent content — the split between L2 and L3 follows
  exactly this tool boundary).
- Exact canonical textual dump format behind the golden files.
- Per-implementation capability declarations: which profiles each implementation claims.
- Policy for "rejected **or reported**" rows: strict mode vs warning mode, decided per implementation.
- Whether `T-5.1-1.2` (non-UTF-8) and other tolerance cases should be profile-dependent.
- Coordinate tolerance value (§2.1) — confirm 0.01 against the implementations' float formatting.
