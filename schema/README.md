# CyberiadaML-GraphML 1.0 — RELAX NG schema

A RELAX NG schema of the CGML document structure, transcribed from ПНСТ 1044-2025
(`../docs/PNST_1044-2025.md`), and the measurement of how much of the standard a schema can
carry.

**Document version:** 1.0 (2026-08-27)

The validator specification closed the L2 layer with a note:

> XSD 1.0 cannot express the key-dependent content of the CGML tag tree (`data` content depends
> on its `key` attribute) [...] A schema export may be generated from the same tables later.

RELAX NG removes that obstacle: it has no Unique Particle Attribution rule, so a content model
may branch on sibling `data` elements distinguished only by their `key` attribute value. This
directory is the result. It is a **reference artefact** — `cgmlval` does not read it, keeps its
own L2 walker, and stays pure-stdlib Python.

## Files

| File | Contents |
|---|---|
| `cgml-1.0.rnc` | the base profile — the constraints `cgmlval` rejects a document for |
| `cgml-1.0-strict.rnc` | `include`s the base and adds the rest of the standard |
| `examples/S-*.graphml` | documents demonstrating what the strict profile adds |
| `examples/L1-*.graphml` | documents demonstrating what no profile can reach |

Only the compact syntax is kept in the repository. It is the readable form and the one a reader
of the standard can check line by line; `jing` validates against it directly, and `trang`
converts it to the XML syntax for engines that need it.

## The two profiles

```
   ПНСТ 1044-2025            cgml-1.0.rnc              cgml-1.0-strict.rnc
   appendix А  tag tree  --> base profile        -->   include + override
   appendix Б  keys          48 ERROR-level            + 16 advisory constraints
   appendix В  geometry      constraints               + what cgmlval never checks
   clauses 5-10 values
                                 |                            |
                                 v                            v
                      base rejects D  =>            strict rejects D  =>
                      cgmlval errors on D           cgmlval --strict fails on D,
                                                    or D breaks a requirement
                                                    cgmlval does not check (below)
```

The base profile is deliberately **weaker** than the standard: a constraint `cgmlval` only
reports as a deviation is held out of it, so that the base profile is a sound pre-filter —
anything it rejects is a real error, never a matter of taste. The strict profile is the standard
as written, and is stricter than `cgmlval` in the places listed under *Requirements the schema
checks and cgmlval does not*.

## Running it

The schema is not exercised by `cgmlval`, and the repository ships no engine. With a RELAX NG
processor available:

    jing -c schema/cgml-1.0.rnc document.graphml
    jing -c schema/cgml-1.0-strict.rnc document.graphml

`tests/test_schema.py` runs the corpus through both profiles and skips when no processor is
found. The numbers below were measured with `jing` 20220510 and `trang` 20220510 on OpenJDK 21.

## Coverage

Measured against the 83 registered `cgmlval` rules and the 73 validator-scoped requirements:

| Layer | Rules | base | strict | partial | XML parser | out of reach |
|---|---|---|---|---|---|---|
| L1 bytes and XML | 7 | – | – | – | 5 | 2 |
| L2 tag tree | 22 | 21 | 1 | – | – | **0** |
| L3 values | 35 | 11 | 5 | – | – | 19 |
| L4 integrity | 19 | 3 | 2 | 1 | – | 13 |
| **total** | **83** | **35** | **8** | **1** | **5** | **34** |

**49 of 83 rules (59 %)**, and of the 73 validator-scoped requirements **39 fully, 2 partly**.
The schema covers the whole of L2 — every rule of the layer it was meant to replace.

The *XML parser* column is L1 and needs the distinction spelled out, because it is easy to
mis-count. Five L1 rules are not implemented by `cgmlval` either: `xml-well-formed` and
`xml-not-empty` are the parse itself, and `char-escaping`, `data-escaping` and `xml-comments`
are registered with the notes *"detected by the well-formedness parse"* and *"the parser drops
XML comments"*. A schema always runs behind a parser, so `jing -c` rejects an unescaped `<` or an
empty file at exactly the same point and for the same reason. Counting the grammar alone against
a whole tool would have compared the two unfairly.

The remaining two L1 rules are genuinely beyond any schema, and for one reason: they are
properties of the **byte stream**, which the parser consumes and the XML infoset does not
preserve.

- `doc-encoding` (CGML-5.1-1) — a correctly-declared KOI8-R document is valid XML, and the
  infoset exposes no encoding for a schema to match — `examples/L1-encoding.graphml` is a
  correctly declared KOI8-R document that both profiles accept and `cgmlval` reports.
- `xml-declaration` (CGML-5.1-2) — `<?xml version="1.0" encoding="UTF-8"?>` is not an infoset
  item a pattern can require; `examples/L1-no-declaration.graphml` has none and passes both
  profiles. This is why CGML-5.1-2 counts as *partial*: the schema does pin the
  other half of the requirement, the root element and its namespace.

Both need the file read as bytes before parsing, which is exactly what `cgmlval`'s L1 does and
what the test catalog assigns to "any standard XML parser".

Over the document corpus: **32 of 32** valid documents accepted by both profiles, **16 of 23**
invalid documents rejected by the base profile, and **0** documents rejected by the base profile
without `cgmlval` also reporting an error.

### The seven invalid documents the schema does not catch

| Document | Requirement | Why it is out of reach |
|---|---|---|
| `X-5.5-4-duplicate-data` | CGML-5.5-4 | at-most-one of each `data` key needs an `interleave` the spec forbids (below) |
| `X-5.9-4-duplicate-id` | CGML-5.9-4 | identity constraint |
| `X-6.3-2-dangling-target` | CGML-6.3-2 | reference resolution |
| `X-6.7-2-dangling-link` | CGML-6.7-2 | reference resolution |
| `X-6.8-1-node-no-slash` | CGML-6.8-1 | `dData` behaviour grammar — text content |
| `X-6.9-1-no-meta` | CGML-6.9-1 | existence of a named formal comment + text content |
| `X-6.9-4-5-bad-propagation` | CGML-6.9-4-5 | `CGML_META` parameter grammar — text content |

Every miss falls into one of two classes: an **identity or reference constraint**, or a **grammar
over element text**. Nothing structural is missing.

## What the schema reaches that XSD 1.0 cannot

Three constructs carry most of the coverage, and none of them is expressible in XSD 1.0:

- **A three-way branch on the leading `data` key.** A node is a vertex, a comment or a state
  according to its first `data` child, and a node of one kind may not carry the marker of
  another. All three alternatives begin with the same element name and differ only in an
  attribute value — the Unique Particle Attribution rule forbids this in XSD. It gives
  `vertex-first-key`, `note-first-key` and `pivot-first-key` at once.
- **Per-key `data` content.** `dGeometry` holds a `rect` on a graph, a `point` or a `rect` on a
  node and a polyline on an edge — the same element name with content chosen by an attribute
  value. This was the reason the validator specification rejected XSD.
- **Counting competing siblings.** `CGML-6.4-4-1` — at most one initial pseudostate on a
  hierarchy level — is the regular expression `plain*, (initial, plain*)?` over `node` children.
  XSD would need two types for `node` in one content model. This is an **L4 integrity rule the
  schema decides structurally**, which is not where one expects a schema to reach.

Appendix В adds a fourth in the strict profile: the geometry kind is fixed per element, and
since a node's `dVertex` value and its `dGeometry` content sit in the *same* element, the pairing
is enforceable — a `choice` with `point` geometry is rejected with *expected element "rect"*.

## Requirements the schema checks and cgmlval does not

Reading the standard directly, rather than the testing specification's transcription of it,
turned up three requirements that no `cgmlval` rule implements. Each has a demonstration document
that `cgmlval` accepts with **no finding at all** and the strict profile rejects:

| Requirement | Demonstration | What is wrong with it |
|---|---|---|
| appendix Б with §5.5(3) | `examples/S-attr-type.graphml` | `dName` redeclared with `attr.type="int"`; §5.5(3) forbids changing the declared type, and `cgmlval` compares only `attr.name` and `for` |
| CGML-6.5-5 | `examples/S-two-regions.graphml` | a composite state with two regions where one omits `dRegion`; §6.5.2 requires the marker on each when there is more than one |
| CGML-6.5-2 | (same construction) | `dRegion` not the first child tag of a region subgraph |

`examples/S-reserved-vertex.graphml`, `examples/S-choice-point.graphml` and
`examples/S-markup-formal.graphml` show the other direction — constraints `cgmlval` does report,
as a deviation rather than an error, so the strict profile mirrors `cgmlval --strict`.

## Findings against the repository

Transcribing from the standard rather than from `CyberiadaML-GraphML-1.0-TESTING-SPEC.md` §2.8
put the schema in a position to test what the testing specification review had already noted, and
to add to it.

**Already recorded, now encoded and demonstrated.**
`CyberiadaML-GraphML-1.0-TESTING-SPEC-REVIEW.md` §3 records that §2.8.1 dropped the appendix А
`[…]` extension markers, and its item 2 proposes a `CGML-5.5-5` for the §5.5(3) rule that a
redeclaration must keep `attr.name` and `attr.type`. The schema carries the profile markings as a
comment on every production, and `examples/S-attr-type.graphml` turns the second from a proposal
into a document that `cgmlval` accepts in silence. Item 8 of the same review asked for
`CGML-6.5-2` to be split; the split now exists in the specification as `CGML-6.5-2`/`CGML-6.5-5`,
and `examples/S-two-regions.graphml` shows it is still unimplemented.

**New: `cgmlval/requirements.py` disagrees with the testing specification about §6.5.**
The specification (since `b58f79f`) defines `CGML-6.5-1`…`CGML-6.5-8`. The requirement table
stops at `CGML-6.5-4` and, more than being incomplete, it is *wrong*: its `CGML-6.5-4` entry is
bound to the `region-no-edges` rule, which implements what the specification now calls
`CGML-6.5-8`, while the specification's `CGML-6.5-4` is a MAY about omitting `dRegion` for a
single region. The registry coverage audit cannot see this — the table it audits against is the
stale part. `CGML-6.5-5`, `-6` and `-7` are absent entirely.

**New: two standard fixtures no longer mirror the standard.**
`tests/test_standard_examples.py::test_standard_fixture_mirrors_the_text` fails for Г.1 and Г.3
against the current text, independently of this change:

- Г.3 — §10.3 moved the component identifier from the `dData` parameter `id/` into `dName`
  (`CGML_COMPONENT LED1`) and left `type` as the only mandatory parameter. This settles review
  item 33 ("md self-inconsistent: decide one encoding") and invalidates its premise;
  `TESTING-SPEC.md:292` and `TEST-CATALOG.md:276` still describe the old body, and the three
  `defects.json` entries recorded from the old spacing and the resulting name collision need
  re-evaluation, since Г.3 now names its two components distinctly.
- Г.1 — the standard now declares `dName for="graph"`, which resolves a defect listed in review
  §2 and leaves the fixture behind.

Both are a resync of the standard fixtures and the specification rows, not schema work.

## Limits of the schema

- **No identity constraints.** RELAX NG has none by design, which puts `unique-ids`,
  `state-names`, `formal-name-unique` and endpoint resolution out of reach. The DTD-compatibility
  `xsd:ID` datatype does not help: CGML identifiers such as `n0::n1` and `init-n0#1` are not XML
  NCNames, and §5.9 admits characters `ID` forbids.
- **No grammar over text content.** The §6.8 behaviour blocks and the §6.9 metadata parameters
  are line-oriented grammars inside `dData`. A datatype pattern could approximate them, but not
  report *which* parameter is wrong, which is the point of the check.
- **`interleave` cannot express "at most one of each `data` key".** The obvious encoding —
  `dName? & dGeometry? & dData?` — is rejected: RELAX NG §7.4 forbids an `interleave` whose
  operands carry overlapping element name classes, and all of these are `data`. `CGML-5.5-4`
  therefore stays an integrity check. The restriction is about *name classes*, not elements in
  general: `cgml.nodes & cgml.edge*` in the base profile is legal, because `node` and `edge` are
  disjoint.

## Notes for maintainers

- **Repeat the namespace in a file that overrides.** Patterns written in `cgml-1.0-strict.rnc`,
  including those inside the `include { … }` block, are compiled in *that* file's namespace
  scope. Without its own `default namespace` declaration every `element data` there means `data`
  in no namespace and silently matches nothing — the schema stays valid and rejects everything.
- **A definition inside `include { … }` must override an existing one.** New helper patterns
  belong at the top level of the overriding file.
- `libxml2` (and so `lxml` and `xmllint --relaxng`) is not the reference implementation and does
  not enforce the §7 restrictions; the numbers above were produced with `jing`.

## Should the schema be generated from cgmlval?

Not as things stand. `cgmlval/tagtree.py` does not carry the appendix А profile markings, the
appendix Б `attr.type` column or the appendix В geometry mapping, so generating from it would
reproduce exactly the gaps this schema was able to find. The two artefacts are more useful as
independent readings of the same standard, cross-checked by the corpus, than as one derived from
the other. Revisit if the L2 tables ever become a complete transcription of the appendices.
