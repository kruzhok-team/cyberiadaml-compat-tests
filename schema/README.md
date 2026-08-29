# CyberiadaML-GraphML 1.0 — RELAX NG schema

A RELAX NG schema of the CGML document structure, transcribed from ПНСТ 1044-2025
(`../docs/PNST_1044-2025.md`), and the measurement of how much of the standard a schema can
carry.

**Document version:** 1.1 (2026-08-30) — follows the testing specification 1.6.

## Files

| File | Contents |
|---|---|
| `cgml-1.0.rnc` | the base profile — the constraints `cgmlval` rejects a document for |
| `cgml-1.0-strict.rnc` | `include`s the base and adds the rest of the standard |
| `examples/S-*.graphml` | documents demonstrating what the strict profile adds |
| `examples/L1-*.graphml` | documents demonstrating what no profile can reach |

## The two profiles

```
   ПНСТ 1044-2025            cgml-1.0.rnc              cgml-1.0-strict.rnc
   appendix А  tag tree  --> base profile        -->   include + override
   appendix Б  keys          the ERROR-level           + the WARNING-level
   appendix В  geometry      constraints               constraints
   clauses 5-10 values                                 + what cgmlval never checks
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

## What the schema carries

Measured on the repository corpus with `jing` 20241231 (OpenJDK 25); `cgmlval` registers
96 rules (66 ERROR, 11 WARNING, 19 INFO).

| Corpus | Documents | Base profile | Strict profile |
|---|---|---|---|
| positive fixtures (`fixtures/core`, `ext`, `field`, `geometry`, `standard`, `tests/examples`) | 32 | 32 accepted | 32 accepted |
| appendix Г documents of the standard | 4 | 4 accepted | 4 accepted |
| negative fixtures (`fixtures/negative`) | 43 | 29 rejected | 29 rejected |
| `examples/S-*` (strict only) | 4 | 4 accepted | 4 rejected |
| `examples/L1-*` (below the schema) | 2 | 2 accepted | 2 accepted |

The 14 negatives neither profile rejects are the identity, reference and text-grammar cases
listed as `UNREACHABLE` in `tests/test_schema.py`: duplicate ids and data keys, dangling
endpoints, self-loops, links targeting links, a second `CGML_META`, and the `dData` /
`CGML_META` / `CGML_COMPONENT` grammars.

### Requirements the schema checks and cgmlval does not

| Example | Requirement | What the strict profile adds |
|---|---|---|
| `S-region-marker-order` | CGML-6.5-2 | `dRegion` is the first key of a single region as well (cgmlval orders it only for two and more) |
| `S-custom-key-for` | CGML-5.5-7, GraphML | a custom `key` names a GraphML element kind in `for` and carries `attr.name` |
| `S-choice-point` | CGML-7.2-1-2 | a choice with point geometry is rejected, not reported |
| `S-reserved-vertex` | CGML-6.4-2 | the reserved `fork` / `join` vertexes are rejected, not tolerated |

## Running it

The schema is not exercised by `cgmlval`, and the repository ships no engine. With a RELAX NG
processor available:

    jing -c schema/cgml-1.0.rnc document.graphml
    jing -c schema/cgml-1.0-strict.rnc document.graphml

`tests/test_schema.py` runs the corpus through both profiles and skips when no processor is
found (`jing` on the path, or `CGML_JING_JAR` with `java`).

## Limits of the schema

- **No identity constraints.** RELAX NG has none by design, which puts `unique-ids`,
  `state-names`, `formal-name-unique` and endpoint resolution out of reach. The DTD-compatibility
  `xsd:ID` datatype does not help: CGML identifiers such as `n0::n1` and `init-n0#1` are not XML
  NCNames, and §5.9 admits characters `ID` forbids.
- **No grammar over text content.** The §6.8 behaviour blocks, the §6.9 metadata parameters and
  the §10.3 component bodies are line-oriented grammars inside `dData`. A datatype pattern could
  approximate them, but not report *which* parameter is wrong, which is the point of the check.
- **`interleave` cannot express "at most one of each `data` key".** The obvious encoding —
  `dName? & dGeometry? & dData?` — is rejected: RELAX NG §7.4 forbids an `interleave` whose
  operands carry overlapping element name classes, and all of these are `data`. `CGML-5.5-4`
  therefore stays an integrity check. The restriction is about *name classes*, not elements in
  general: `cgml.nodes & cgml.edge*` in the base profile is legal, because `node` and `edge` are
  disjoint. Sequences with a fixed leading key (the marker branches of a node, `dPivot` /
  `dChunk` on a link, `dCollapsed` before the regions) are expressible and are used.
- **Colour names are case-insensitive in CSS.** RELAX NG values are not, so `dColor` admits any
  alphabetic word; the name list itself is checked by `cgmlval`.

## Notes for maintainers

- **Repeat the namespace in a file that overrides.** Patterns written in `cgml-1.0-strict.rnc`,
  including those inside the `include { … }` block, are compiled in *that* file's namespace
  scope. Without its own `default namespace` declaration every `element data` there means `data`
  in no namespace and silently matches nothing — the schema stays valid and rejects everything.
- **A definition inside `include { … }` must override an existing one.** New helper patterns
  belong at the top level of the overriding file.
- **A base addition needs its cgmlval ERROR rule first.** The soundness invariant is tested
  (`test_the_base_profile_never_rejects_what_cgmlval_accepts`); a constraint cgmlval only reports
  goes to the strict profile.
- `libxml2` (and so `lxml` and `xmllint --relaxng`) is not the reference implementation and does
  not enforce the §7 restrictions; the numbers above were produced with `jing`.
