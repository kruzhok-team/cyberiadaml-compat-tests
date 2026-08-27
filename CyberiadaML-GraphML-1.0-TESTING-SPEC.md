# CyberiadaML-GraphML Standard Compatibility — Testing Specification

**Standard under test:** ПНСТ 1044-2025 "Системы киберфизические. Национальная киберфизическая платформа. Часть 4. Программирование расширенных иерархических машин состояний. Формат документа описания диаграмм машин состояний" — the Cyberiada-GraphML (CGML) format for HSM (ПРИМС) diagrams serialization.

**Related standards:**

- ПНСТ 984-2024 "Системы киберфизические. Национальная киберфизическая платформа. Часть 3. Программирование расширенных иерархических машин состояний" — the HSM (ПРИМС) diagram semantics;
- GraphML — http://graphml.graphdrawing.org/specification.html;
- XML 1.0 standard.

**Document version:** 1.5 (2026-08-25)

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

- `CGML-5.4-1` MUST: a `data` tag with `key="gFormat"` is present as the **first child** of `graphml`. [R/W/X] **Note:** This is the additional requirement to the GraphML format. 
- `CGML-5.4-2` MUST: its value is the fixed string `Cyberiada-GraphML-1.0`; any other value is invalid for this version of the standard. [R/W/X]

**5.5 Data keys** (`CGML-5.5-*`)

- `CGML-5.5-1` MUST: `key` declarations appear after the format mark and before the graph structure; each declaration binds `id` to an element kind (`for=` `graphml`/`graph`/`node`/`edge`), an `attr.name`, and an  optional `attr.type` (absent for the four geometry keys). [R/W]
- `CGML-5.5-2` SHOULD: the declaration block is kept in the document; if absent, the default declarations of Appendix Б apply. [R/W]
- `CGML-5.5-3` MUST: a `data` tag always carries a `key` attribute; content is interpreted by its key. [R/W/X]
- `CGML-5.5-4` MUST: a given graph/node/edge carries **at most one** `data` of each key type (no duplicate keys within one tag). [R/W/X]
- `CGML-5.5-5` MUST: a standard `key` redeclaration keeps the original `attr.name` and `attr.type`. [R/W/X]
- `CGML-5.5.6` SHOULD: do not change the standard keys declarations. [R/W]
- `CGML-5.5-7` MAY: add custom keys to the list of declared `keys`. [R]

**5.6 Graph** (`CGML-5.6-*`)

- `CGML-5.6-1` MUST: `graph` has a unique `id`; `edgedefault="directed"` (state-machine graphs are always directed). [R/W/X]
- `CGML-5.6-2` MUST: one **or more** top-level graphs per document, each a separate state machine. [R/W]
- `CGML-5.6-3` MUST: child order inside `graph`: data keys → nodes → edges; subgraphs nest only inside nodes (regions / nested state machines). [R/W]
- `CGML-5-6-4` SHOULD: the `graph` name is started with `g` or `G` prefix. [W] 

**5.7 Node** (`CGML-5.7-*`)

- `CGML-5.7-1` MUST: `node` has a unique `id`. [R/W/X]
- `CGML-5.7.2` MUST: `node` appears only inside `graph`. [R/W/X]
- `CGML-5.7-3` MAY: node contains data keys and, for composite/submachine states, nested `graph` tags. [R]

**5.8 Edge** (`CGML-5.8-*`)

- `CGML-5.8-1` MUST: `edge` has non-empty `id`, `source`, `target` attributes. [R/W/X]
- `CGML-5.8-2` SHOULD: edge id follows the `source-target#N` template. `N` starts at 0. [W]
- `CGML-5.8-3` MUST: all edge tags of a state-machine graph are placed **as a single block at the end** of that graph (after all nodes). [R/W]

**5.9 Identifiers** (`CGML-5.9-*`)

- `CGML-5.9-1` MUST: every `graph`, `node`, `edge` carries `id`. [R/W/X]
- `CGML-5.9-2` MUST: id charset — ASCII 33 (`!`) through 126 (`~`), **excluding** `"` (34), `'` (39), `` ` `` (96) and `\` (92); hyphen, underscore, `#` explicitly allowed. [R/W/X]
- `CGML-5.9-3` MUST: ids are case-sensitive; non-empty; length ≤ 256 characters. [R/W/X]
- `CGML-5.9-4` MUST: ids are unique across the **whole document**, including all nested nodes and all state machines. [R/W/X]

### 2.3 §6 — Document elements

Element ↔ encoding map (Table 2): state machine = top-level `graph` + `dStateMachine`; region = nested `graph` + `dRegion`; simple/composite state = `node` (default); final state & pseudostates = `node` + `dVertex`; comment = `node` + `dNote`; transition = `edge`; comment link = `edge` + `dPivot`.

**6.1 State machine** (`CGML-6.1-*`)

- `CGML-6.1-1` MUST: `dStateMachine` is the mandatory **first** child key of the top-level graph; its value is **empty** (pure type marker). [R/W/X]
- `CGML-6.1-2` MUST: `dName` present; non-empty string; **no two state machines in a document share a name**. [R/W/X]
- `CGML-6.1-3` MAY: `dGeometry` (rectangle, §7). [R/W]
- `CGML-6.1-4` MUST: children ordered keys → nodes → edges. [R/W/X]
- `CGML-6.1-5` MAY: several independent state machines at top level (multi-SM documents). [R/W]
- `CGML-6.1-6` MUST: no `dRegion` subgraph directly under the SM graph (see appendix А: `graph*` only under `node*`)

**6.2 Simple state** (`CGML-6.2-*`)

- `CGML-6.2-1` Default node type: a `node` without `dVertex`/`dNote`/`dSubmachineState` is a state. [R]
- `CGML-6.2-2` MAY: `dName` — the state name; optional; empty value ≡ unnamed state; multiple unnamed siblings allowed. [R/W/X]
- `CGML-6.2-3` MUST: sibling elements (states, pseudostates, and comments) on the same hierarchy level must have unique names. [R/W/X]
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

**6.5 Composite state and region** (`CGML-6.5-*`)

Composite states admit all simple-state requirements (see 6.2).

- `CGML-6.5-1` MUST: nested elements of a composite state live in one or more region subgraphs (`graph` inside the `node`); the region subgraph is mandatory for holding children. [R/W]
- `CGML-6.5-2` MUST: region marker: `dRegion` key on the nested graph (empty value). Must be the first child tag when present. [R/W]
- `CGML-6.5-3` SHOULD: region/subgraph id = parent node id + separator (`:`/`::`). Test must not enforce a single/double colon. [W]
- `CGML-6.5-4` MAY: region tag may be omitted for a single region within a composite state. [R]
- `CGML-6.5-5` MUST: region tag must present for 2+ regions withi a composite state. [R/W/X]
- `CGML-6.5-6` MAY: `dName` - region title (see `CGML-6.2-3`). [W]
- `CGML-6.5-7` MUST: if region geometry is omitted the regions' geometry is considered as equal to the parent composite state node's. [R]
- `CGML-6.5-8` MUST: transitions of child elements are placed at the end of the **top-level** state-machine graph, not inside region subgraphs. [R/W/X]

**6.6 Comment** (`CGML-6.6-*`)
- `CGML-6.6-1` MUST: `dNote` — mandatory **first** child key of a comment node; value `informal` (human-readable) or `formal` (machine-readable). [R/W/X]
- `CGML-6.6-2` MAY: `dData` — comment body text; `dName` — comment title (see `CGML-6.2-3`); `dGeometry` (rectangle). [R/W]
- `CGML-6.6-3` SHOULD: it is recommended to preserve a formal comments body verbatim. [R]

**6.7 Comment-subject links** (`CGML-6.7-*`)
- `CGML-6.7-1` MUST: link = `edge` from comment node to subject node with mandatory first key `dPivot` naming the commented aspect from the closed set: {`dName`, `dData`, empty}, reject others. [R/W/X]
- `CGML-6.7-2` MUST: `source` and `target` nodes exist and belong to the **same state-machine graph**. [R/W/X] **Extension hook:** under EXT-COMPLETENESS (8.5) `target` may reference an edge id (comment link to a transition).
- `CGML-6.7-3` MUST: `dChunk` — substring of the subject's aspect being commented. Must present and be non-empty when `dPivot` is `dName` or `dData`. [R/W]
- `CGML-6.7-4` MUST: `source` must be a `dNote` node; no self-loops allowed; see geometry condition as in `CGML-6.3-5`. 

**6.8 Events, guards, behaviour** (`CGML-6.8-*`)

- `CGML-6.8-1` MUST: `dData` value is text in the HSM diagram standard (ПНСТ 984-2024) label syntax `Event [Guard]/ Behaviour`: the `/` separates the event description — the event name (may be empty: a completion transition on an edge, ПНСТ 984-2024 3.31, or a completion block in a node) and an optional guard in square brackets — from the behaviour, and may be omitted only when no behaviour follows (§6.8.1). In a **node** every block is an internal-behaviour block (`entry/`, `exit/`, `do/`, see 6.8-3) or an internal event; its header is the block's first line, so behaviour lines require the `/` on it. In an **edge** the label may additionally span several lines (event name and guard on separate lines, as in the standard's own §6.8 edge example). The value may be an **empty string**, meaning no behaviour is defined. [R/W/X]
- `CGML-6.8-2` MUST: multiple behaviour/event blocks inside one `dData` are separated by a blank line (double newline); the number of blocks is unlimited. Whitespace inside `dData` is significant to block separation; implementations must preserve block structure round-trip. [R/W]
- `CGML-6.8-3` MUST: internal-behaviour blocks begin with one of the keywords `entry/`, `exit/`, or `do/` (entry, exit, do behaviour respectively). [R/W]
- `CGML-6.8-4` MUST: an event description starts with the event name (may be empty). [R/W]
- `CGML-6.8-5` MAY: an event description may carry event-handling parameters from ПНСТ 984-2024: the keywords `propagate` and `block` placed directly before the `/` separator (after the guard when present), or `defer` placed directly after it (§6.8.1). [R/W] **Note:** per-event keywords, distinct from the document-level `eventPropagation` metadata parameter (6.9), which allows only `block`/`propagate`.
- `CGML-6.8-6` MAY: a guard block may contain the keyword `else` (see the at-most-one-else constraints in `CGML-6.3-4` and `CGML-6.4-4-2`). [R/W]
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
  - `CGML-6.9-4-4` `transitionOrder` — `actionFirst` (default) | `exitFirst`;
  - `CGML-6.9-4-5` `eventPropagation` — `block` (default) | `propagate`;
  - `CGML-6.9-4-6` `markupLanguage` — default markup of informal comments, a text string (see 9.3).
- `CGML-6.9-5`: MAY: any number of additional parameters. [R]

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
- `CGML-7.2-2` MUST: the coordinate axes are: x left-to-right, y axis downwards; coordinates relative to the **parent** element's top-left corner (SM; composite state for regions; region); SM coordinates global; `point` carries `x`,`y` = element **center**; `rect` carries `x`,`y` = **top-left corner** + `width`,`height`. Coordinates are real numbers; SVG-like syntax `<point x= y=/>`, `<rect x= y= width= height=/>` nested inside the `data` tag. [R/W/X]
- `CGML-7.2-3` MAY: `width` and `height` of the rectangular elements may be set loosely and reconstructed on load in the base (short) geometry format. [R]
- `CGML-7.2-4` MUST: absence of `dGeometry` on an element = element is not visualized; a non-visualized composite state hides all its children. [R]

### 2.5 §8 — EXT-COMPLETENESS extensions

**8.1 Submachine state** (`CGML-8.1-*`)

- `CGML-8.1-1` MUST: node with key `dSubmachineState`; value = reference to a state machine — external (`file://…`) or within the document (the referenced SM `id`). Resolution of internal references (the SM id) and tolerance of unresolvable external references must be tested. [R/W]
- `CGML-8.1-2` MUST: if a submachine state has entry/exit points then a single subgraph must be used for the entry/exit points specification; the subgraph may have no `dData` keys. [R/W]

**8.2 History pseudostates** (`CGML-8.2-*`)

- `CGML-8.2-1` MUST: `dVertex` = `shallowHistory` | `deepHistory`; otherwise the 6.4 vertex rules apply (dVertex first+mandatory; optional dName, point geometry). [R/W]
- `CGML-8.2-2` MUST: usable inside states and with state machines (derived from the ПНСТ 984-2024 standard). [R/W]

**8.3 Entry/exit points** (`CGML-8.3-*`)

- `CGML-8.3-1` MUST: `dVertex` = `entryPoint` | `exitPoint`; otherwise the 6.4 vertex rules apply (dVertex first+mandatory; optional dName, point geometry). [R/W]
- `CGML-8.3-2` MUST: usable inside states/SMs and with submachine states. [R/W]
- `CGML-8.3-3` MUST: be placed inside the parent element / on the parent element's border if geometry is set. [R/W]

**8.4 Collapsed composite state** (`CGML-8.4-*`)

- `CGML-8.4-1` MAY: `dCollapsed` key on a composite-state node (empty value) marks a hidden decomposition block; visualizers must render collapsed. [R/W]
- `CGML-8.4-2` MUST: Nodes with `dCollapsed` key still contains its region subgraph, without the subgraph the document is invalid. [W/X]

**8.5 Comment link to a transition** (`CGML-8.5-*`)

- `CGML-8.5-1` MAY: An edge's `target` may name an **edge id** (the commented transition) instead of a node id; only valid for comment-subject links (`dPivot` present).The
- `CGML-8.5-2` MUST: The `target` edge must be a transition, not a comment link. [R/W/X]
- `CGML-8.5-3` MUST: Non-comment link edges targeting edges remain invalid. [X]

### 2.6 §9 — EXT-DISPLAY extensions

**9.1 Full geometry** (`CGML-9.1-*`)

Inherits base format (2.4).

- `CGML-9.1-1` MUST: additionally (Table 6) transitions get geometry:
  - `CGML-9.1-1-1` MUST: non-empty `dGeometry` on polyline edges with 1+ intermediate point; coordinates relative to the left-top point of the source element.
  - `CGML-9.1-1-2` MUST: `dSourcePoint` keys for all edge endpoint attachment; coordinates relative to the left-top point of the source element;
  - `CGML-9.1-1-3` `dTargetPoint` keys for all edge endpoint attachment:
    - `CGML-9.1-1-3-1` MUST: if transition edges - coordinates relative to the left-top point of the target element; [R/W]
	- `CGML-9.1-1-3-2` MUST: if comment link to an element edges - coordinates relative to the left-top point of the target element; [R/W]
	- `CGML-9.1-1-3-3` MUST: if comment link to a transision edges- coordinates relative to the left-top point of the source element of the transition; [R/W]
    - `CGML-9.1-1-3-4` MUST: if comment link to a subject aspect's (`dChunk`) - **no target point** allowed; [R/W/X]
- `CGML-9.1-1-4` MAY: label geometry may be a rect. [R/W]
- `CGML-9.1-1-5` MUST: if label geometry described as a rect it must have valid `width` and `height`. [R/W]
- `CGML-9.1-2` MUST: the recorded geometry is sufficient for unambiguous rendering — no geometry reconstruction allowed. [W]

**9.2 Color marking** (`CGML-9.2-*`)

- `CGML-9.2-1` MAY: `dColor` key on `node` or `edge`; value = non-empty CSS/SVG color string. [R/W]
- `CGML-9.2-2` MUST: explicit hex forms `#RRGGBB` or `#RRGGBBAA` must be supported. [R/W]
- `CGML-9.2-3` SHOULD: named colors (e.g. `red`) also allowed. [R/W]
- `CGML-9.2-4` MUST: may not use on `graph` (SMs and regions). [R/W]

**9.3 Comment markup** (`CGML-9.3-*`)

- `CGML-9.3-1` MAY: `dMarkup` on informal comment nodes selects the markup language of `dData`; default `plain`; `markdown` supported per 9.3.1. [R/W]
- `CGML-9.3-2` MUST: `dMarkup` key outside the informal comment nodes is invalid. [X] 
- `CGML-9.3-3` MAY: document-wide default is set via `markupLanguage` metadata (6.9). [R/W]
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

- `CGML-10.3-1` MUST: Formal comment with name `CGML_COMPONENT` and structured body (`id/ …`, `type/ …`, `name/ …`, parameter lines in the 6.9 metadata syntax) describes a diagram component. [R/W]

### 2.8 Additional machine-checkable artefacts (Appendices A & B) 

**2.8.1 Document tag tree** (`CGML-appendix-A-*`)

`CGML-appendix-A-1` MUST: The complete hierarchy of admissible tags; any tag placement outside the tree is invalid. Basis for XML structural validation. The syntax `data<KEY>` means `data` tag with the key `KEY`; `*` means repeating (0+ times). Here is the hierarchical structure: [R/W/X]

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

Here is the complete key inventory with element bindings. It is not recommended to
redefine the standard keys, and using an undeclared key without declaration is not allowed (see
5.5). Reproduced for reference:

| Key | for | attr.name | Profile |
|---|---|---|---|
| `gFormat` | `graphml` | `format` | CORE |
| `dName` | `graph`, `node` | `name` | CORE |
| `dStateMachine` | `graph` | `stateMachine` | CORE |
| `dRegion` | `graph` | `region` | CORE |
| `dSubmachineState` | `node` | `submachineState` | EXT-COMPLETENESS |
| `dGeometry` | `graph`, `node`, `edge` | `geometry` | CORE (edge: EXT-DISPLAY) |
| `dSourcePoint`, `dTargetPoint` | `edge` | `sourcePoint`, `targetPoint` | EXT-DISPLAY |
| `dLabelGeometry` | `edge` | `labelGeometry` | CORE |
| `dNote` | `node` | `note` | CORE |
| `dVertex` | `node` | `vertex` | CORE |
| `dData` | `node`, `edge` | `data` | CORE |
| `dPivot`, `dChunk` | `edge` | `pivot`, `chunk` | CORE |
| `dCollapsed` | `node` | `collapsed` | EXT-COMPLETENESS |
| `dMarkup` | `node` | `markup` | EXT-DISPLAY |
| `dColor` | `node`, `edge` | `color` | EXT-DISPLAY |
| `dFormalName` | `graph`, `node` | `formalName` | EXT-PLATFORM |

## 3. Compatibility statement

An implementation is **CORE-compatible** when it satisfies every MUST of §2.2–§2.4 in each conformance sense ([R]/[W]/[X]) applicable to its capabilities (read-only tools are exempt from [W]; write-only generators from [R]). Extension-profile compatibility is claimed and tested per profile (§2.5–§2.7). SHOULD-level deviations do not break compatibility but must be reported. Verdicts per requirement: `pass` / `fail` / `not-applicable` / `not-supported` (unclaimed profile).

