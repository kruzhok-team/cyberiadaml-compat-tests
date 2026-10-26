# CyberiadaML-GraphML Standard Compatibility — Testing Specification

**Standard under test:** ПНСТ 1044-2025 "Системы киберфизические. Национальная киберфизическая платформа. Часть 4. Программирование расширенных иерархических машин состояний. Формат документа описания диаграмм машин состояний" — the Cyberiada-GraphML (CGML) format for HSM (ПРИМС) diagrams serialization.

**Source text:** `docs/PNST_1044-2025.md` — the Markdown mirror of the standard maintained in this repository is the authoritative text for the testing system; the PDF is consulted for layout questions only. The requirement rows below cite its clause numbers.

**Related standards:**

- ПНСТ 984-2024 "Системы киберфизические. Национальная киберфизическая платформа. Часть 3. Программирование расширенных иерархических машин состояний" — the HSM (ПРИМС) diagram semantics;
- GraphML — http://graphml.graphdrawing.org/specification.html;
- XML 1.0 standard.

**Extension under test:** ПРИМС:КА — `docs/FA-extension.md` 0.3 (2026-10-26), the deterministic finite automaton extension of ПРИМС and CGML; its rows (§2.9) cite the clause numbers of that document.

**Document version:** 1.11 (2026-10-26)

## 1. Purpose

This document specifies **what must be checked** to establish that an implementation — any library or tool, in any programming language, present or future — is compatible with the CGML standard. It is implementation-independent: compatibility is defined solely against the standard document, never against a reference library.

For every requirement below, compatibility of an implementation means, as applicable:

- **[R] Read compatibility** — the implementation accepts a document satisfying the requirement and interprets it as the standard prescribes;
- **[W] Write compatibility** — every document the implementation produces satisfies the requirement;
- **[X] Rejection compatibility** — the implementation rejects (or reports) a document violating a mandatory requirement.

Requirement identifiers use the scheme `CGML-<clause>-<n>` (e.g. `CGML-5.4-1`). Levels follow the standard's wording: **MUST** (обязательно / не допускается), **SHOULD** (рекомендуется), **MAY** (допускается).

The test-suite implementation (corpus, validator, drivers, reports) will be specified separately.

## 2. Compatibility requirements by clause of CyberiadaML GraphML version 1.0 (ПНСТ 1044-2025)

This specification covers CyberiadaML GraphML standard version 1.0.

### 2.1 Conformance profiles

The standard itself separates a mandatory base from optional extensions; compatibility claims are made per profile:

| Profile | Clauses | Mandatory? |
|---|---|---|
| **CORE** | §5 document format, §6 elements, §7 base geometry, appendices А/Б/В | yes — every implementation |
| **EXT-COMPLETENESS** | §8: submachine states, history pseudostates, entry/exit points, collapsed composites, comment links to transitions | declared per implementation |
| **EXT-DISPLAY** | §9: full geometry, color marking, comment markup | declared per implementation |
| **EXT-PLATFORM** | §10: formal names, initialization comments, dynamic components | declared per implementation |
| **EXT-FA** | ПРИМС:КА (`docs/FA-extension.md` 0.3): deterministic finite automaton diagrams, selected by `type/ fa` in the document metadata (§2.9) | declared per implementation |

An implementation not claiming an extension profile must still not mis-parse core content of documents that contain extension keys (unknown-but-declared keys are GraphML data and must be tolerated on read).

### 2.2 §5 — Document format

The CyberiadaML GraphML standard extends the GraphML format specification. This section highlights the significant differences from the GraphML specification.

**5.1 Document** (`CGML-5.1-*`)

- `CGML-5.1-1` MUST: document is a text file, `UTF-8` encoding (other encodings only in platform-specific scenarios; not recommended). [R/W/X]
- `CGML-5.1-2` MUST: root tag `graphml` with `xmlns="http://graphml.graphdrawing.org/xmlns"`; XML declaration with version and encoding present. [R/W]
- `CGML-5.1-3` MAY: additional namespace attributes for format extensions. [R]

**5.2 Special characters** (`CGML-5.2-*`)

- `CGML-5.2-1` MUST: XML markup characters in content are escaped (`&lt; &gt; &amp; &quot; &apos;` per Table 1); implementations must unescape on read and escape on write. [R/W]

**5.3 XML text comments** (`CGML-5.3-*`)

- `CGML-5.3-1` MUST: XML comments (`<!-- -->`) are ignored during CGML processing (unless a specialized extension states otherwise); they must not break parsing anywhere in the document. [R] **Note:** XML comments are distinct from the HSM (ПРИМС) "Comment" element (6.6).

**5.4 Format version** (`CGML-5.4-*`)

- `CGML-5.4-1` MUST: a `data` tag with `key="gFormat"` is present as the **first child** of `graphml`. [R/W/X] **Note:** This is the additional requirement to the GraphML format (see `CGML-5.10-1`).
- `CGML-5.4-2` MUST: its value is the fixed string `Cyberiada-GraphML-1.0`; any other value is invalid for this version of the standard. [R/W/X]

**5.5 Data keys** (`CGML-5.5-*`)

- `CGML-5.5-1` MUST: `key` declarations appear after the format mark and before the graph structure; each declaration binds `id` to an element kind (`for=` `graphml`/`graph`/`node`/`edge`), an `attr.name`, and an  optional `attr.type` (absent for the four geometry keys). [R/W]
- `CGML-5.5-2` SHOULD: the declaration block is kept in the document; if absent, the default declarations of Appendix Б apply. [R/W]
- `CGML-5.5-3` MUST: a `data` tag always carries a `key` attribute; content is interpreted by its key. [R/W/X]
- `CGML-5.5-4` MUST: a given graph/node/edge carries **at most one** `data` of each key type (no duplicate keys within one tag). [R/W/X]
- `CGML-5.5-5` MUST: a standard `key` redeclaration keeps the original `attr.name` and `attr.type`. [R/W/X]
- `CGML-5.5-6` SHOULD: do not change the standard keys declarations. [R/W]
- `CGML-5.5-7` MAY: add custom keys to the list of declared `keys`. [R]

**5.6 Graph** (`CGML-5.6-*`)

- `CGML-5.6-1` MUST: `graph` has a unique `id`; `edgedefault="directed"` (state-machine graphs are always directed). [R/W/X]
- `CGML-5.6-2` MUST: one **or more** top-level graphs per document, each a separate state machine. [R/W]
- `CGML-5.6-3` MUST: child order inside `graph`: data keys → nodes → edges; subgraphs nest only inside nodes (regions / nested state machines). [R/W]
- `CGML-5.6-4` SHOULD: the `graph` name is started with `g` or `G` prefix. [W] 

**5.7 Node** (`CGML-5.7-*`)

- `CGML-5.7-1` MUST: `node` has a unique `id`. [R/W/X]
- `CGML-5.7-2` MUST: `node` appears only inside `graph`. [R/W/X]
- `CGML-5.7-3` MAY: node contains data keys and, for composite/submachine states, nested `graph` tags. [R]
- `CGML-5.7-4` MUST: the node kind is given by a marker key placed **first** among the node's data keys — `dNote` (comment), `dVertex` (pseudostate or final state), `dSubmachineState` (submachine state); a `node` carries **at most one** marker key; a node without a marker key is a simple or composite state. [R/W/X]

**5.8 Edge** (`CGML-5.8-*`)

- `CGML-5.8-1` MUST: `edge` has non-empty `id`, `source`, `target` attributes. [R/W/X]
- `CGML-5.8-2` SHOULD: edge id follows the `source-target` template, or `source-target#N` template when several edges connect the same pair of nodes; `N` starts at 0. [W]
- `CGML-5.8-3` MUST: all edge tags of a state-machine graph are placed **as a single block at the end** of that graph (after all nodes). [R/W]

**5.9 Identifiers** (`CGML-5.9-*`)

- `CGML-5.9-1` MUST: every `graph`, `node`, `edge` carries `id`. [R/W/X]
- `CGML-5.9-2` MUST: id charset — ASCII 33 (`!`) through 126 (`~`), **excluding** `"` (34), `'` (39), `` ` `` (96) and `\` (92); hyphen, underscore, `#` explicitly allowed. [R/W/X]
- `CGML-5.9-3` MUST: ids are case-sensitive; non-empty; length ≤ 256 characters. [R/W/X]
- `CGML-5.9-4` MUST: ids are unique across the **whole document**, including all nested nodes and all state machines. [R/W/X]

**5.10 Differences from GraphML** (`CGML-5.10-*`)

- `CGML-5.10-1` MUST: a CGML document is not a valid GraphML document in exactly two respects, which implementations must tolerate: (1) the `data` tag with `key` attribute equal to `gFormat` tag precedes the `key` declarations (see `CGML-5.4-1`); (2) a key `id` is declared once per element kind (`for`), so the same `id` may appear in several `key` tags. Generic GraphML tools may reject CGML documents on these points. [R/W]

### 2.3 §6 — Document elements

Element ↔ encoding map (Table 2): state machine = top-level `graph` + `dStateMachine`; region = nested `graph` + `dRegion`; simple/composite state = `node` (default); final state & pseudostates = `node` + `dVertex`; comment = `node` + `dNote`; transition = `edge`; comment link = `edge` + `dPivot` (its target is a node or, under 8.5, the edge id of a transition).

**6.1 State machine** (`CGML-6.1-*`)

- `CGML-6.1-1` MUST: `dStateMachine` is the mandatory **first** child key of the top-level graph; its value is **empty** (pure type marker). [R/W/X]
- `CGML-6.1-2` MUST: `dName` present; non-empty string; **no two state machines in a document share a name**. The machine's name is also the name of its single region (6.1.2). [R/W/X]
- `CGML-6.1-3` MAY: `dGeometry` (rectangle, §7). [R/W]
- `CGML-6.1-4` MUST: children ordered keys → nodes → edges. [R/W/X]
- `CGML-6.1-5` MAY: several independent state machines at top level (multi-SM documents). [R/W]
- `CGML-6.1-6` MUST: no `graph` (region) tag directly under a state-machine graph — subgraphs nest only inside nodes. [R/W/X]

**6.2 Simple state** (`CGML-6.2-*`)

- `CGML-6.2-1` MUST: Default node type: a `node` without `dVertex`/`dNote`/`dSubmachineState` is a state. [R]
- `CGML-6.2-2` MAY: `dName` — the state name; optional; empty value ≡ unnamed state; multiple unnamed siblings allowed. [R/W/X]
- `CGML-6.2-3` MUST: sibling states and pseudostates on the same hierarchy level — a state machine or a region, each region being a separate name space (6.5.2) — must have unique names; comments are exempt (6.6.1). [R/W/X]
- `CGML-6.2-4` MAY: `dData` — behaviour/internal transitions text (per 6.8). [R/W]
- `CGML-6.2-5` MAY: `dGeometry` (rectangle). [R/W]

**6.3 Transition** (`CGML-6.3-*`)

- `CGML-6.3-1` MAY: `dData` — event/guard/behaviour text (6.8); absent when the transition carries none. [R/W]
- `CGML-6.3-2` MUST: `source` and `target` nodes exist and belong to the **same state-machine graph**. [R/W/X] 
- `CGML-6.3-3` MAY: self-loops (source = target). [R]
- `CGML-6.3-4` MUST: transitions outgoing from the same `source` node must have **at most one** **else** trigger (derived from the ПНСТ 984-2024 standard). [R/W/X]
- `CGML-6.3-5` MUST: transition geometry only permitted when both endpoint nodes have geometry. [R/W]

**6.4 Pseudostates and final state** (`CGML-6.4-*`)

- `CGML-6.4-1` MUST: `dVertex` is the mandatory **first** child key of the vertex node. [R/W/X]
- `CGML-6.4-2` MUST: value from Table 3 — CORE: `initial`, `final`, `choice`, `terminate`; EXT-COMPLETENESS: `shallowHistory`, `deepHistory`, `entryPoint`, `exitPoint`; **reserved** for future usage (must not be emitted, tolerated on read as unknown vertex): `fork`, `join`. [R/W/X]
- `CGML-6.4-3` MAY: `dName` (see `CGML-6.2-3`), geometry (point for most pseudostates/final; rectangle for `choice`, per §7/Appendix В). [R/W]
- `CGML-6.4-4-*` Usage counts constrained only by the ПНСТ 984-2024 standard semantics (e.g. one initial pseudostate per region):
  - `CGML-6.4-4-1` MUST: The only initial pseudostate is allowed on the same hierarchy level of the state machine; [R/W]
  - `CGML-6.4-4-2` SHOULD: a document representing a correct ПРИМС diagram contains at least one `initial` pseudostate in every state machine (in any of its regions, 6.4.2); §1 admits intermediate documents that need not conform, so the validator reports the absence as INFO. [R/X]

**6.5 Composite state and region** (`CGML-6.5-*`)

Composite states admit all simple-state requirements (see 6.2).

- `CGML-6.5-1` MUST: nested elements of a composite state live in one or more region subgraphs (`graph` inside the `node`); the region subgraph is mandatory for holding children. [R/W]
- `CGML-6.5-2` MUST: region marker: `dRegion` key on the nested graph (empty value). Must be the first child tag when present. [R/W]
- `CGML-6.5-3` SHOULD: region/subgraph id = parent node id + separator (`:`/`::`). Test must not enforce a single/double colon. [W]
- `CGML-6.5-4` MAY: the `dRegion` marker may be omitted when a composite state has a single region subgraph. [R/W]
- `CGML-6.5-5` MUST: with two or more region subgraphs in a composite state each of them carries the `dRegion` marker as its first data key. [R/W/X]
- `CGML-6.5-6` MAY: `dName` - region title (see `CGML-6.2-3`). [W]
- `CGML-6.5-7` MUST: if region geometry is omitted the regions' geometry is considered as equal to the parent composite state node's. [R]
- `CGML-6.5-8` MUST: transitions of child elements are placed at the end of the **top-level** state-machine graph, not inside region subgraphs. [R/W/X]

**6.6 Comment** (`CGML-6.6-*`)

- `CGML-6.6-1` MUST: `dNote` — mandatory **first** child key of a comment node; value `informal` (human-readable) or `formal` (machine-readable). [R/W/X]
- `CGML-6.6-2` MAY: `dData` — comment body text; `dName` — comment title (named like states, but comment names need not be unique, 6.6.1); `dGeometry` (rectangle). [R/W]
- `CGML-6.6-3` SHOULD: it is recommended to preserve a formal comments body verbatim. [R]
- `CGML-6.6-4` MAY: a comment without subjects (no outgoing links) relates to the state machine that contains it (6.6.2). [R]

**6.7 Comment-subject links** (`CGML-6.7-*`)

- `CGML-6.7-1` MUST: link = `edge` whose source is a comment node, with the mandatory **first** key `dPivot` naming the commented aspect from the closed set {`dName`, `dData`, empty}; any other value is rejected. [R/W/X]
- `CGML-6.7-2` MUST: `source` and `target` exist and belong to the **same state-machine graph**. The target may be **any node** of that graph: a state (simple or composite), a pseudostate or final state, **another comment**. A graph is never a target — neither the state machine (6.7.2, an explicit narrowing of ПНСТ 984-2024 7.8.5) nor a region. [R/W/X] **Extension hook:** under EXT-COMPLETENESS (8.5) `target` may name the edge id of a transition of the same graph.
- `CGML-6.7-3` MUST: `dChunk` — the commented fragment, a non-empty substring of the subject's aspect named by `dPivot`: `dName` → the subject's name; `dData` → the subject's body text — a state's behaviour blocks, a comment's body or (8.5) the transition label including event names, guards and actions (6.7.1). Present and non-empty whenever `dPivot` is `dName` or `dData`; absent with an empty `dPivot`. A subject without the named aspect — `dName` on a transition or an unnamed vertex, `dData` on a vertex — admits no such link. [R/W/X]
- `CGML-6.7-4` MUST: the link's `source` is a comment node (`dNote` present, informal or formal); `source` ≠ `target` (no self-loops: a comment cannot comment itself, 6.7.2). [R/W/X]
- `CGML-6.7-5` MAY: a comment carries any number of links, also several to one subject; a subject may be linked from several comments (6.7.2). Links are edges of the top-level state-machine graph like transitions (`CGML-6.5-8`), in any order among them. [R/W]
- `CGML-6.7-6` MUST: a link carries geometry (9.1) only when the comment and the subject are drawn — the geometry condition of `CGML-6.3-5` applies to links (6.7.2); in the base geometry format a link carries no geometry (`CGML-7.2-1-5`). [R/W]

**6.8 Events, guards, behaviour** (`CGML-6.8-*`)

- `CGML-6.8-1` MUST: `dData` value is text in the HSM diagram standard (ПНСТ 984-2024) label syntax `Event [Guard]/ Behaviour`: the `/` separates the event description — the event name (may be empty: a completion transition on an edge, ПНСТ 984-2024 3.31, or a completion block in a node) and an optional guard in square brackets — from the behaviour, and may be omitted only when no behaviour follows (§6.8.1). In a **node** every block is an internal-behaviour block (`entry/`, `exit/`, `do/`, see 6.8-3) or an internal event; its header is the block's first line, so behaviour lines require the `/` on it. In an **edge** the label may additionally span several lines (event name and guard on separate lines, as in the standard's own §6.8 edge example). The value may be an **empty string**, meaning no behaviour is defined. [R/W/X]
- `CGML-6.8-2` MUST: multiple behaviour/event blocks inside one `dData` are separated by a blank line (double newline); the number of blocks is unlimited. Whitespace inside `dData` is significant to block separation; implementations must preserve block structure round-trip. [R/W]
- `CGML-6.8-3` MUST: internal-behaviour blocks begin with one of the keywords `entry/`, `exit/`, or `do/` (entry, exit, do behaviour respectively). [R/W]
  - `CGML-6.8-3-1` MUST: a state carries at most one `entry/`, one `exit/` and one `do/` block (6.8.1). [R/W/X]
- `CGML-6.8-4` MUST: an event description starts with the event name (may be empty). [R/W]
  - `CGML-6.8-4-1` MUST: the event name is not a reserved word: `entry`, `exit`, `do`, `propagate`, `block`, `defer`, `else` (6.8.1). [R/W/X]
  - `CGML-6.8-4-2` MAY: the reserved event names `ANY` and `UNKNOWN` (ПНСТ 984-2024 7.4.6.7) are permitted event names. [R/W]
  - `CGML-6.8-4-3` MUST: a transition carries a single event — the format's explicit limitation of ПНСТ 984-2024 7.6.7.2 (6.8.1). [R/W]
  - `CGML-6.8-4-4` MAY: event names are global to the document (6.8.1). [R]
- `CGML-6.8-5` MAY: an event description may carry event-handling parameters from ПНСТ 984-2024: the keywords `propagate` and `block` placed directly before the `/` separator (after the guard when present), or `defer` placed directly after it (§6.8.1). [R/W] **Note:** per-event keywords, distinct from the document-level `eventPropagation` metadata parameter (6.9), which allows only `block`/`propagate`.
  - `CGML-6.8-5-1` MUST: `defer` appears only in a node `dData` (an internal transition) and is the whole behaviour of the block — nothing follows it (6.8.1). [R/W/X]
  - `CGML-6.8-5-2` MUST: `propagate` and `block` are allowed only when the event name is non-empty (6.8.2). [R/W/X]
- `CGML-6.8-6` MAY: a guard block may contain the keyword `else` (see the at-most-one-else constraints in `CGML-6.3-4`). [R/W]
- `CGML-6.8-7` MUST: XML special characters inside `dData` (`<`, `>`, `&`) are escaped per 5.2, as everywhere in the document. [R/W/X]
- `CGML-6.8-8` MUST: square brackets used **inside a guard's logical expression** are escaped with a backslash — `\[`, `\]` (e.g. `[String.Contains(\[Example\])]`). [R/W]

**6.9 Document metadata** (`CGML-6.9-*`)

- `CGML-6.9-1` MUST: a correct CGML document contains, on the top-level **in the first state-machine graph**, a formal-comment node named `CGML_META` (`dNote` = `formal`, `dName` = `CGML_META`) holding document metadata; exactly one per document; there are no `dPivot` edges from/to it. [R/W/X]
- `CGML-6.9-2` MUST: `dData` = list of `name/ value` parameters; parameters separated by an **empty line**; parameter name is Latin letters only; name and value separated by `/`; whitespaces and tabs in the name and value are trimmed. [R/W/X]
  - `CGML-6.9-2-1` MAY: multi-lined values are allowed. [R/W]
  - `CGML-6.9-2-2` SHOULD: the camelCase is recommended for the parameter name. [W]
- `CGML-6.9-3` MUST: mandatory parameter `standardVersion` equals to the version of the ПНСТ 984-2024 standard - `1.0`. [R/W/X]
- `CGML-6.9-4-*` MAY: Standard parameters (recommended, uniquely interpreted): [R]
  - `CGML-6.9-4-1` `geometry` — `none` (default when absent) | `short` | `full` — governs §7/§9.1 interpretation;
  - `CGML-6.9-4-2` `platform`, `platformVersion`, `platformLanguage`, `target`, `name`, `author`, `contact`, `description`, `version` — a text string;
  - `CGML-6.9-4-3` `createdAt` — ISO 8601, UTC;
  - `CGML-6.9-4-4` `transitionOrder` — `actionFirst` (default when absent) | `exitFirst`;
  - `CGML-6.9-4-5` `eventPropagation` — `block` (default when absent) | `propagate`;
  - `CGML-6.9-4-6` `markupLanguage` — default markup of informal comments, a text string (see 9.3).
- `CGML-6.9-5` MAY: any number of additional parameters. [R]
- `CGML-6.9-6` MUST: the metadata applies to every state machine of the document; machines needing different parameters are described in different documents (6.9.2). [R]

### 2.4 §7 — Geometry (base format)

**7.1 Geometry types** (`CGML-7.1-*`)

- `CGML-7.1-1` MUST: a document has exactly one geometry mode, declared by the `geometry` metadata parameter: `none` (default), `short` (base format, 7.2), `full` (extended, 9.1). [R/W/X]
  - `none`: document carries topology only; visualizers reconstruct layout;
  - `short`: semantics per 7.2; under `short`, missing element geometry is reconstructed on display;
  - `full`: semantics per 9.1. 

**7.2 Base geometry format** (`CGML-7.2-*`)

- `CGML-7.2-1-*` MUST: Geometry carriers (Table 4) [R/W]:
  - `CGML-7.2-1-1` state machine — `dGeometry` rect on its graph;
  - `CGML-7.2-1-2` simple/composite state, choice, comment, submachine state — `dGeometry` rect on the node;
  - `CGML-7.2-1-3` other pseudostates and final state — `dGeometry` point on the node;
  - `CGML-7.2-1-4` region — `dGeometry` rect on the region subgraph;
  - `CGML-7.2-1-5` transition — **no geometry in base format** including comment links;
  - `CGML-7.2-1-6` transition label — `dLabelGeometry` point or rect on the edge; must present when the edge is viauzualized and labelled; label coordinates relative to the **source node's** top-left corner;
- `CGML-7.2-2` MUST: the coordinate axes are: x left-to-right, y axis downwards; coordinates relative to the **parent** element's top-left corner (SM; composite state for regions; region); SM coordinates are global document coordinates, and when the SM carries no geometry its top-level children are given in the same global coordinates; `point` carries `x`,`y` = element **center**; `rect` carries `x`,`y` = **top-left corner** + `width`,`height`. Coordinates are real numbers; SVG-like syntax `<point x= y=/>`, `<rect x= y= width= height=/>` nested inside the `data` tag. [R/W/X]
- `CGML-7.2-3` MAY: `width` and `height` of the rectangular elements may be set loosely and reconstructed on load in the base (short) geometry format. [R]
- `CGML-7.2-4` MUST: absence of `dGeometry` on an element = element is not visualized; a non-visualized composite state hides all its children. [R]

### 2.5 §8 — EXT-COMPLETENESS extensions

**8.1 Submachine state** (`CGML-8.1-*`)

- `CGML-8.1-1` MUST: node with the marker key `dSubmachineState` as its **first** data key (see `CGML-5.7-4`); value = reference to a state machine — external (`file://…`, a URI) or within the document (the referenced SM `id`). Resolution of internal references (the SM id) and tolerance of unresolvable external references must be tested. [R/W/X]
  - `CGML-8.1-1-1` MUST: the reference does not name the state machine that contains the submachine state (8.1.1). [R/W/X]
- `CGML-8.1-2` MUST: a submachine state has a nested `graph` only to hold its entry/exit points (8.3) — a single subgraph containing nothing but such `node` tags; that subgraph carries **no data keys at all** (not even `dRegion`). [R/W/X]
- `CGML-8.1-3` MUST: a submachine state carries no `dData` — no internal behaviour or internal transitions (8.1.2). [R/W/X]
- `CGML-8.1-4` MUST: for an internal reference, every entry/exit point inside the submachine subgraph is named after an entry/exit point of the referenced state machine (8.1). [R/W/X]

**8.2 History pseudostates** (`CGML-8.2-*`)

- `CGML-8.2-1` MUST: `dVertex` = `shallowHistory` | `deepHistory`; otherwise the 6.4 vertex rules apply (dVertex first+mandatory; optional dName, point geometry). [R/W]
- `CGML-8.2-2` MUST: usable inside states and with state machines (derived from the ПНСТ 984-2024 standard). [R/W]

**8.3 Entry/exit points** (`CGML-8.3-*`)

- `CGML-8.3-1` MUST: `dVertex` = `entryPoint` | `exitPoint`; otherwise the 6.4 vertex rules apply (dVertex first+mandatory; optional dName, point geometry). [R/W]
- `CGML-8.3-2` MUST: usable inside states/SMs and with submachine states. [R/W]
- `CGML-8.3-3` MUST: be placed inside the parent element / on the parent element's border if geometry is set. [R/W]
- `CGML-8.3-4` MUST: an entry/exit point carries a non-empty `dName` (8.3.1). [R/W/X]
- `CGML-8.3-5` MUST: in a composite state with several regions the state's entry/exit points are placed in the first region (8.3.2). [R/W/X]

**8.4 Collapsed composite state** (`CGML-8.4-*`)

- `CGML-8.4-1` MAY: `dCollapsed` key on a composite-state node (empty value) marks a hidden decomposition block; visualizers must render collapsed. [R/W]
- `CGML-8.4-2` MUST: Nodes with `dCollapsed` key still contains its region subgraph, without the subgraph the document is invalid. [W/X]

**8.5 Comment link to a transition** (`CGML-8.5-*`)

- `CGML-8.5-1` MAY: an edge's `target` may name an **edge id** (the commented transition) instead of a node id; only valid for comment-subject links (`dPivot` present). The transition belongs to the same state-machine graph (`CGML-6.7-2`). [R/W]
- `CGML-8.5-2` MUST: the `target` edge is a transition, not a comment link. [R/W/X]
- `CGML-8.5-3` MUST: non-link edges (no `dPivot`) targeting an edge id remain invalid. [X]
- `CGML-8.5-4` MUST: `dChunk` of a link to a transition is a fragment of the transition's label (`dData`): an event name, a guard or an action; `dPivot` = `dName` is not admissible for a transition, which has no name (`CGML-6.7-3`). [R/W/X]

### 2.6 §9 — EXT-DISPLAY extensions

**9.1 Full geometry** (`CGML-9.1-*`)

Inherits base format (2.4).

- `CGML-9.1-1` MUST: additionally (Table 6) transitions get geometry:
  - `CGML-9.1-1-1` MUST: non-empty `dGeometry` on polyline edges with 1+ intermediate point; coordinates relative to the left-top point of the source element; a comment link may carry a polyline the same way. [R/W]
  - `CGML-9.1-1-2` MUST: `dSourcePoint` keys for all edge endpoint attachment; coordinates relative to the left-top point of the source element; [R/W]
  - `CGML-9.1-1-3` `dTargetPoint` keys for all edge endpoint attachment:
    - `CGML-9.1-1-3-1` MUST: if transition edges - coordinates relative to the left-top point of the target element; [R/W]
    - `CGML-9.1-1-3-2` MUST: if comment link to an element edges - coordinates relative to the left-top point of the target element; [R/W]
    - `CGML-9.1-1-3-3` MUST: if comment link to a transition edges - coordinates relative to the left-top point of the source element of the transition; [R/W]
    - `CGML-9.1-1-3-4` MUST: if comment link to a subject aspect's (`dChunk`) - **no target point** allowed; [R/W/X]

The frame of a target point (the target node, or the source node of the commented transition) is a rendering semantic: the conformance channels preserve the recorded coordinates unchanged, so the frame interpretation of `CGML-9.1-1-3-1…3` is established by an implementation's own geometry tests, not by the fixtures.

- `CGML-9.1-1-4` MAY: label geometry may be a rect. [R/W]
- `CGML-9.1-1-5` MUST: if label geometry described as a rect it must have valid `width` and `height`. [R/W]
- `CGML-9.1-2` MUST: the recorded geometry is sufficient for unambiguous rendering — no geometry reconstruction allowed; for the links (9.1.2): `dSourcePoint` on every link, `dTargetPoint` on every link to a node or a transition, none on a fragment link. A full-mode document missing a link end is **reported** by the validator — the implementations reconstruct the ends rather than refuse the document. [W]

**9.2 Color marking** (`CGML-9.2-*`)

- `CGML-9.2-1` MAY: `dColor` key on `node` or `edge` selects the element's colour. [R/W]
- `CGML-9.2-2` MUST: the value is a non-empty string `#RRGGBB` (RGB) or `#RRGGBBAA` (RGBA, alpha byte last) with hexadecimal digits; this form must be supported by every implementation claiming EXT-DISPLAY. [R/W/X]
- `CGML-9.2-3` SHOULD: a colour name from the CSS/HTML named-colour list (e.g. `red`, `green`) is an accepted alternative value; its support is recommended. Any other value is invalid. [R/W]
- `CGML-9.2-4` MUST: may not use on `graph` (SMs and regions). [R/W]

**9.3 Comment markup** (`CGML-9.3-*`)

- `CGML-9.3-1` MAY: `dMarkup` on a comment node (`dNote` = `informal` or `formal`) selects the markup language of its `dData`; value is a non-empty string; `plain` (default when absent) and `markdown` are standard values, editors may add their own. [R/W]
- `CGML-9.3-2` MUST: `dMarkup` on any node other than a comment, or with an empty value, is invalid. [R/W/X]
- `CGML-9.3-3` MAY: document-wide default of the informal comments is set via `markupLanguage` metadata (6.9); a formal comment has no default. [R/W]
- `CGML-9.3-4` MUST: `dMarkup` key overrides the document-wide `markupLanguage` for the comment. [R/W/X]

### 2.7 §10 — EXT-PLATFORM extensions

**10.1 Formal names** (`CGML-10.1-*`)

- `CGML-10.1-1` MAY: `dFormalName` on nodes/graphs — machine-readable identifier used by translators equivalently to `dName`. [R/W]
- `CGML-10.1-2` MUST: a formal name is case-sensitive; non-empty; starts with latin letters (`a`-`z`, `A`-`Z`) or underscore, continues with latin letters, underscore or digits. [R/W/X]
- `CGML-10.1-3` MUST: for state machine formal names - no two state machines in a document
  share a formal name; for the rest elements formal names - siblings on the same hierarchy
  level must have unique formal names (the same as `CGML-6.2-3`). [R/W/X]

**10.2 Formal comments for initialization** (`CGML-10.2-*`)

- `CGML-10.2-1` MAY: Formal comments (6.6) are allowed to carry translator/interpreter initialization; content not regulated by the standard — compatibility requires preserving the body verbatim. [R/W]

**10.3 Dynamic components** (`CGML-10.3-*`)

- `CGML-10.3-1` MUST: a dynamic component is a formal comment whose `dName` is the string `CGML_COMPONENT`, one space, and the component identifier — unique among the components of its state machine and satisfying the formal-name rules of `CGML-10.1-2` (e.g. `CGML_COMPONENT LED1`); the same identifier may be defined in several state machines (`CGML-10.3-2`), each definition being a node with its own document-wide unique `id` (`CGML-5.9-4`); its `dData` body is a parameter list in the document metadata syntax (`name/ value`, blank-line separated, whitespace around `/` trimmed) with the mandatory parameter `type` (component type, e.g. `LED`); further platform-defined parameters (`name`, `description`, …) are optional. [R/W/X]
- `CGML-10.3-2` MUST: when a platform supports dynamic components and a diagram uses them, every state machine of the document that uses a component defines it (a `CGML_COMPONENT` comment in that state machine). [R/W]

### 2.8 Additional machine-checkable artefacts (Appendices A & B) 

**2.8.1 Document tag tree** (`CGML-appendix-A-*`)

`CGML-appendix-A-1` MUST: the tag tree of appendix А defines the admissible **nesting** of tags: a tag placed under a parent the tree does not allow is invalid. The tree does not define presence or order — those follow from the clause rows (`CGML-5.4-1`, `CGML-5.5-1`, `CGML-5.6-3`, `CGML-5.7-4`, `CGML-5.8-3`, `CGML-6.1-1`, `CGML-6.1-4`, `CGML-6.4-1`, `CGML-6.6-1`, `CGML-6.7-1`) and the per-element key lists (`CGML-8.1-2`, `CGML-9.2-4`, `CGML-9.3-2`); the `node*` of a subgraph has the same structure as a top-level node, including its own `graph*` (unbounded depth). The syntax `data<KEY>` means a `data` tag with the key `KEY`; `*` means repeating (0+ times). [R/W/X]

- `graphml`
  - `data<gFormat>`
  - `key*`
  - `graph`
    - `data<dStateMachine>`
    - `data<dName>`
    - `data<dGeometry>`
      - `rect`
    - `data<dFormalName>`
    - `node*`
      - `data<dNote>`
      - `data<dSubmachineState>`
      - `data<dVertex>`
      - `data<dName>`
      - `data<dGeometry>`
        - `point`
        - `rect`
      - `data<dData>`
      - `data<dFormalName>`
      - `data<dCollapsed>`
      - `data<dColor>`
      - `data<dMarkup>`
      - `graph*`
        - `data<dRegion>`
        - `data<dName>`
        - `data<dGeometry>`
          - `rect`
        - `data<dFormalName>`
        - `node*`
    - `edge*`
      - `data<dPivot>`
      - `data<dChunk>`
      - `data<dData>`
      - `data<dLabelGeometry>`
        - `point`
        - `rect`
      - `data<dGeometry>`
        - `point*`
      - `data<dSourcePoint>`
        - `point`
      - `data<dTargetPoint>`
        - `point`
      - `data<dColor>`
  - `graph*`

**2.8.2 Standard key declarations** (`CGML-appendix-B-*`)

`CGML-appendix-B-1` MUST: a `key` declaration of a standard key binds the `id` to the element kinds, `attr.name` and `attr.type` given in appendix Б (Table below); a declaration with a different `for`, `attr.name` or `attr.type` for a standard `id`, and a `data` tag whose key is not declared (explicitly or by the appendix Б defaults), are invalid. [R/W/X]

| Key | for | attr.name | attr.type | Profile |
|---|---|---|---|---|
| `gFormat` | `graphml` | `format` | string | CORE |
| `dName` | `graph`, `node` | `name` | string | CORE |
| `dStateMachine` | `graph` | `stateMachine` | string | CORE |
| `dRegion` | `graph` | `region` | string | CORE |
| `dSubmachineState` | `node` | `submachineState` | string | EXT-COMPLETENESS |
| `dGeometry` | `graph`, `node`, `edge` | `geometry` | - | CORE (edge: EXT-DISPLAY) |
| `dSourcePoint`, `dTargetPoint` | `edge` | `sourcePoint`, `targetPoint` | - | EXT-DISPLAY |
| `dLabelGeometry` | `edge` | `labelGeometry` | - | CORE |
| `dNote` | `node` | `note` | string | CORE |
| `dVertex` | `node` | `vertex` | string | CORE |
| `dData` | `node`, `edge` | `data` | string | CORE |
| `dPivot`, `dChunk` | `edge` | `pivot`, `chunk` | string | CORE |
| `dCollapsed` | `node` | `collapsed` | string | EXT-COMPLETENESS |
| `dMarkup` | `node` | `markup` | string | EXT-DISPLAY |
| `dColor` | `node`, `edge` | `color` | string | EXT-DISPLAY |
| `dFormalName` | `graph`, `node` | `formalName` | string | EXT-PLATFORM |

### 2.9 ПРИМС:КА — EXT-FA extension (`docs/FA-extension.md` 0.3)

A deterministic finite automaton (FA) diagram is a CGML document restricted to a subset of
the ПРИМС elements and labelled by the metadata parameter `type/ fa`. The rows below apply
only to such documents; a document without `type/ fa` is never judged by them. Clause
numbers are those of `docs/FA-extension.md`. Terms: a *symbol* is an event name (an input
symbol) or an action line (an output symbol); the *top level* of the state machine is the
set of its direct children.

**FA 5 The document** (`CGML-FA-5-*`)

- `CGML-FA-5-1` MUST: an FA document carries the parameter `type` with the value `fa` in `CGML_META` (6.9 grammar: `type/ fa`); the value selects the FA rule set of this section and is preserved on write. [R/W/X]
- `CGML-FA-5-2` MUST: an FA document contains exactly one state machine. [R/W/X]
- `CGML-FA-5-3` MUST: the parameter `eventPropagation` is absent or has the value `block`. [R/W/X]

**FA 3 The element set** (`CGML-FA-3-*`)

- `CGML-FA-3-1` MUST: the elements of an FA diagram are simple and composite states, the `initial` pseudostate, the `final` state, transitions, comments and comment links; every other vertex kind (`choice`, `terminate`, the histories, entry and exit points), submachine states and the collapsed decomposition block (`dCollapsed`) are not admissible. [R/W/X]

**FA 3.1 States** (`CGML-FA-3.1-*`)

- `CGML-FA-3.1-1` MUST: the behaviour text of a state holds at most one block, an `entry/` block whose behaviour is exactly one line — the output symbol of the state; `exit/`, `do/` and event blocks (internal transitions) are not admissible. [R/W/X]
- `CGML-FA-3.1.1-1` MUST: a composite state has exactly one region and no `entry/` block. [R/W/X]
- `CGML-FA-3.1.1-2` MUST: a composite state that is the target of a transition contains an `initial` pseudostate in its region. [R/W/X]
- `CGML-FA-3.1.1-3` MUST: determinism — a state has at most one own outgoing transition per event name, `EOF` included; a transition of a nested state shadows the transition of its parent by the same event. [R/W/X]

**FA 3.2 Initial pseudostate** (`CGML-FA-3.2-*`)

- `CGML-FA-3.2-1` MUST: the top level of the state machine holds exactly one `initial` pseudostate (a narrowing of `CGML-6.4-4-2` to an error). [R/W/X]
- `CGML-FA-3.2-2` MUST: the transition from an `initial` pseudostate has no event, no guard and no action (an empty `dData`). [R/W/X]

**FA 3.3 Final states** (`CGML-FA-3.3-*`)

- `CGML-FA-3.3-1` MUST: `final` states are placed at the top level of the state machine only. [R/W/X]
- `CGML-FA-3.3-2` MUST: every transition into a `final` state carries the event `EOF`, and every transition with the event `EOF` targets a `final` state. [R/W/X]

**FA 3.4 Transitions** (`CGML-FA-3.4-*`)

- `CGML-FA-3.4-1` MUST: a transition from a state carries exactly one event block with a non-empty event name — an input symbol or `EOF`; a guard and the parameters `propagate`, `block`, `defer` are not admissible. [R/W/X]
- `CGML-FA-3.4-2` MUST: the behaviour of a transition is absent or exactly one line — the output symbol. [R/W/X]
- `CGML-FA-3.4-3` MUST: a symbol — an event name other than `EOF`, an action line, an `entry/` line, a member of a declared alphabet — is none of the reserved words `do`, `else`, `entry`, `exit`, `propagate`, `block`, `defer` and none of the reserved event names `ANY`, `UNKNOWN`, `EOF`. [R/W/X]

**FA 4 Alphabets** (`CGML-FA-4-*`)

- `CGML-FA-4-1` MUST: the input alphabet is declared by at most one formal comment named `FA_INPUT` or `FA_INPUT_RE`, the output alphabet by at most one named `FA_OUTPUT` or `FA_OUTPUT_RE`; such comments are placed at the top level of the state machine. [R/W/X]
- `CGML-FA-4-2` MUST: the body of an alphabet comment is one symbol per line, no line empty; in a `_RE` comment every line is a restricted regular expression over the constructs `.` (any single printable non-space character), `[a-z]` (a range), `{n}` and `{n,m}` (repetition counts, no spaces), `?`, `(a|b)` (a group with alternatives) and the escapes `\.` `\[` `\]` `\-` `\{` `\}` `\,` `\?` `\(` `\)` `\|` `\\`; the constructs `*`, `+`, `^`, `$` are not admissible (the set stays finite); an expression matches a whole symbol; the reserved strings of `CGML-FA-3.4-3` are excluded from the set. [R/W/X]
- `CGML-FA-4-3` MUST: when the input alphabet is declared, every event name other than `EOF` is a member of it; when the output alphabet is declared, every action line and every `entry/` line is a member of it. [R/W/X]
- `CGML-FA-4-4` MAY: an alphabet comment may have no geometry; its body is preserved verbatim (`CGML-10.2-1`). [R/W]

**FA 2.4 Execution** (`CGML-FA-2.4-*`)

- `CGML-FA-2.4-1` MAY: an executor runs an FA document with one active state, selects the transition by the event of the active state or, failing that, of its nearest ancestor, rejects the tape on a symbol with no transition, and issues `EOF` once after the last symbol; outside the scope of the document validator. [X]

## 3. Compatibility statement

An implementation is **CORE-compatible** when it satisfies every MUST of §2.2–§2.4 in each conformance sense ([R]/[W]/[X]) applicable to its capabilities (read-only tools are exempt from [W]; write-only generators from [R]). Extension-profile compatibility is claimed and tested per profile (§2.5–§2.7, §2.9). SHOULD-level deviations do not break compatibility but must be reported. Verdicts per requirement: `pass` / `fail` / `not-applicable` / `not-supported` (unclaimed profile).
