# CyberiadaML-GraphML 1.0 — Testing Specification Review against the Markdown Standard

Review of `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` v1.5 §2 (101 requirement rows) against
`docs/PNST_1044-2025.md`, the first clean text of the standard. Date: 2026-08-25. Only
discrepancies are listed; matching rows are omitted. Each item is a proposed correction for
the next specification revision — nothing here has been applied yet.

## 1. Discrepancies

| # | Requirement | Specification claim | Standard text (md) | Proposed correction |
|---|---|---|---|---|
| 1 | CGML-5.5-1 | every `key` binds `attr.name` and `attr.type` (MUST) | appendix Б: the geometry keys `dGeometry`, `dSourcePoint`, `dTargetPoint`, `dLabelGeometry` have no `attr.type` | `attr.type` optional (absent for the four geometry keys) |
| 2 | (none) §5.5 3) | — | «при переопределении стандартных ключей изменение имени (`attr.name`) или типа (`attr.type`) … запрещено. Не рекомендуется переопределять стандартные ключи»; «приложения могут вводить собственные ключи» | add CGML-5.5-5 MUST (redeclaration keeps attr.name/attr.type) + SHOULD NOT redeclare; CGML-5.5-6 MAY custom keys. §2.8.2 "undeclared key violates 5.5" has no md basis — drop or mark GraphML-derived |
| 3 | CGML-5.8-2 | MAY `source-target#N` | §5.8.1 «**Рекомендуется** … шаблон `source-target#N` … `N` … (начинается с `0`)» | level SHOULD; N starts at 0 |
| 4 | (none) §5.6.1/5.7.1 | — | «Рекомендуется использовать префикс `G` или `g`» (graph), «префикс `n`» (node) | optional SHOULD rows |
| 5 | (none) §6.1.2 | — | «стандарт не позволяет описывать машины состояний, содержащие непосредственно в элементе машины состояний более одной области» | add CGML-6.1-6 MUST: no `dRegion` subgraph directly under the SM graph (appendix А: `graph*` only under `node*`) |
| 6 | CGML-6.2-3 / 6.6-2 | sibling uniqueness for states only | §6.2.1 «… не может содержать двух **элементов** с одинаковым именем»; §6.6.1 comments follow state naming; §6.4.1 pseudostates «аналогично» | one uniqueness set per level: named states, pseudostates and comments |
| 7 | CGML-6.3-4, 6.4-4-2 | MUST at most one `else` per source / per `choice` | §6.3/§6.4 carry no such rule («ограничено только требованиями стандарта ПРИМС»); §6.8.1 only admits the `else` keyword | mark both as derived from ПНСТ 984-2024; 6.3-4 duplicates 6.4-4-2 — merge |
| 8 | CGML-6.5-2 | `dRegion` marker, no level, no position | §6.5.1 «**может** быть указан как **первый** дочерний тег … В случае единственной области … может быть опущен»; §6.5.2 «более чем одной области … **должен** содержать в качестве первого дочернего тега ключ `dRegion`» | split: MAY omit for a single region; MUST present and first for ≥2 regions; MUST empty; MUST first child when present |
| 9 | CGML-6.5-3 | MAY id = parent id + `:` | §6.5.1 «**рекомендуется** … (`:`)» (also §8.1.1); examples (appendix В «Область», Г.2, Г.4) use `::` | level SHOULD; tests must not enforce a single colon |
| 10 | (none) §6.5.1 | — | «В случае отсутствия геометрии области при наличии геометрии составного состояния, геометрия области принимается равной геометрии составного состояния»; region `dName` allowed | add: region geometry defaults to the parent state's; region `dName` MAY |
| 11 | CGML-6.7-1 | `dPivot` names the aspect (open set) | §6.7.1 «одно из **трех** значений: `dName` … `dData` … пустое значение» | closed set {`dName`, `dData`, empty}; [X] rejects others |
| 12 | CGML-6.7-3 | MAY `dChunk` | §6.7.1 «Указывается **обязательно**, если … `dPivot` имеет значения `dName` или `dData`»; «не может быть пустой строкой» | MUST present and non-empty when dPivot ∈ {dName, dData} |
| 13 | CGML-6.7-2 | endpoints exist in the same SM graph | §6.7.2 source «**только** элемент типа комментарий»; target «любая вершина (в том числе и другой комментарий)»; «дуги связей в виде **петель** … не поддерживаются»; geometry only if both vertices have geometry | add: source MUST be a `dNote` node; target may be a comment; no self-loops; geometry condition as 6.3-5 |
| 14 | CGML-6.8-4 | event name may be absent in a transition label and a node block | §6.8.1 «описание событий начинается с имени события» — absence only implied by the §6.4 edge examples (`[else]`, `[… &gt; 0]/`) | keep the edge case (cite §6.4 examples); the nameless node block is ПНСТ 984-derived / not supported by 1044 |
| 15 | CGML-6.8-2 (md defect) | blocks separated by a blank line (MUST) | md's §10.1 example `entry/ scan_start();⏎exit/ scan_stop();` uses a single newline; appendix В «state-blocks-2» merges an internal event into the entry block | md example defect; fixtures must not copy these |
| 16 | CGML-6.9-1 | CGML_META in the first SM graph | §6.9.2 «обязан быть **единственным** в документе и размещаться на **верхнем уровне** первой машины состояний»; «не должен иметь предметов комментирования или быть предметом комментирования» | add: exactly one per document; top level of the first SM; no `dPivot` edges from/to it |
| 17 | CGML-6.9-2 | name/value syntax | §6.9.1 «пробелы и табуляции перед и после символа косой черты (`/`) игнорируются»; multi-line values; «Рекомендуется … camel case» | add whitespace-trimming MUST, multi-line MAY, camelCase SHOULD |
| 18 | CGML-6.9-3 | `standardVersion` = version of this standard | §6.9 «версия стандарта **ПРИМС (ПНСТ 984)** … `1.0`» | wording only |
| 19 | CGML-7.2-1-5 | "transition — no geometry" | Table 4 «Переход **или связь между комментарием и предметом комментирования** – Не описывается» | include comment links |
| 20 | CGML-7.2-1-6 | `dLabelGeometry` carrier, no level | §7.2.1 «**обязателен** для любой визуализируемой дуги … которая … содержит метку»; label coordinates relative to the **source node's** top-left corner | MUST when the edge is visualized and labelled; add the coordinate frame |
| 21 | CGML-7.2-2 | point = center, rect = top-left, real numbers | §7.2.1 y axis downwards; coordinates relative to the **parent** element's top-left corner (SM; composite state for regions; region); SM coordinates global | add the coordinate-frame rule (affects geometry round-trip tests) |
| 22 | (none) §7.2.2 | — | «ширина и высота … может задаваться **нестрого**» (short) vs §9.1.1 «точного соответствия размеров» (full) | add MAY row for short mode (contrast 9.1-2) |
| 23 | CGML-8.1-1 | external `file://` or internal reference; no position rule | §8.1.1 «**первый и обязательный** дочерний тег»; internal = SM `id`, external = URI; examples (§8.1, appendix В) reference by `dName` | add first-child MUST; record the md inconsistency (normative `id` vs examples `dName`) — test both |
| 24 | (none) §8.1.1/8.1.2, Table 5 | — | «не более одного подграфа»; subgraph only for entry/exit points; subgraph «не может содержать никаких ключей»; no `dData` on a submachine state | add rows 8.1-2 … 8.1-4 |
| 25 | CGML-8.2-2 | MUST history usable inside states and with SMs | §8.2.2 «ограничено только требованиями стандарта ПРИМС» | drop MUST or mark ПНСТ 984-derived |
| 26 | CGML-8.3-2 | placement | §8.3.2 «внутри родительского элемента или на его границе» | optional display row |
| 27 | CGML-8.4-1 (md defect) | collapsed node keeps its region subgraph; only composite states | §8.4.2 agrees, but the appendix В collapsed-state fragment has **no** `graph` child | md example defect; [X] test: `dCollapsed` on a node without a subgraph → invalid |
| 28 | CGML-8.5-1 | target may be an edge id | §8.5 «дуги, **представляющей переход**» | the target edge must be a transition, not a comment link |
| 29 | CGML-9.1-1 | coarse: edges "get" dGeometry/dSourcePoint/dTargetPoint | §9.1.2 «Для **всех** дуг … `dSourcePoint`»; «`dTargetPoint` … для всех дуг кроме связей … с … фрагментами»; §9.1.1 edge `dGeometry` only for polylines with ≥1 intermediate point, non-empty; coordinate frames relative to source/target nodes | split into MUST rows |
| 30 | CGML-9.2-1 | named colours "also allowed" | §9.2.1 «непустая строка с префиксом `#` и шести- или восьмизначным … кодом»; names «**рекомендуется** поддержка»; §9.2.2 not on SMs and regions | hex MUST; names SHOULD-support; [X] `dColor` on `graph` invalid |
| 31 | CGML-9.3-1 | MAY `dMarkup` on informal comments | §9.3.3 «применяется **только** в узлах неформальных комментариев»; non-empty; §9.3.4 overrides `markupLanguage` | [X] `dMarkup` elsewhere invalid; non-empty; precedence rule |
| 32 | CGML-10.1-3 | SM formal names unique in the document; state formal names unique among siblings | §10.1.2 cites 6.1.1/6.1.2 only (SM naming), not 6.2.1 | keep, mark the sibling rule as extrapolated (md cross-reference defect) |
| 33 | CGML-10.3-1 | marker = comment name `CGML_COMPONENT`; body `id/ type/ name/ …` | §10.3.1 «тело … должно **начинаться со строки** `CGML_COMPONENT`» (example without `dName`); appendix Г.3 uses `<data key="dName"> CGML_COMPONENT </data>` (with spaces) and a body starting at `id/`; `id`, `type` mandatory; §10.3.2 components defined in every SM | md self-inconsistent: decide one encoding (or accept both); `id`/`type` MUST, `name`/`description` MAY; add the per-SM row |
| 34 | §2.8.2 table | `dSubmachineState` = EXT-COMPLETENESS | appendix А lists `data<dSubmachineState>` unbracketed (core) while §8.1 is an extension | keep EXT-COMPLETENESS; note the md inconsistency |

## 2. Defects in the standard text itself

- Table 2 names the marker key `dMachineState`; the key is `dStateMachine` everywhere else.
- The §6.7 example closes `<node id="n1">` with `</edge>`.
- Appendix А: `[data<dFormalName]` lacks the closing `>`.
- Г.1 uses `dName` on the graph without declaring `dName for="graph"` (only `for="node"` is declared).
- Г.3 names its components `<data key="dName"> CGML_COMPONENT </data>` with surrounding spaces; §10.3.1 describes a different encoding (body starting with `CGML_COMPONENT`). Libraries trim the spaces differently, which the harness now reports as defects C-7 / PY-4 / CS-6.
- Items 15, 23 and 27 above: examples contradicting their own clause.

## 3. Earlier open findings — settled

- **CGML-10.1-2 formal-name character set**: §10.1.1 = `[A-Za-z_][A-Za-z0-9_]*`, non-empty; case sensitivity implied, cited as inferred.
- **§2.8.1 tag tree vs appendix А**: region subtree placement matches (`graph*` under `node*`, no edges inside regions, edges only under the SM graph); only the `[…]` extension markers were dropped.

## 4. Suggested handling

Revise the testing specification to v2.0 in one pass: adjust the levels (items 3, 8, 9, 12, 20, 30), add the missing rows (2, 5, 10, 16, 17, 21, 22, 24, 29, 31), mark the ПНСТ 984-derived rules (7, 14, 25), and update `cgmlval/requirements.py`, the rules and the catalog accordingly; fix the standard text defects of §2 in `docs/PNST_1044-2025.md` first, since several rows depend on which encoding the standard settles on (items 23, 33).
