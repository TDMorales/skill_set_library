# SOURCES.md — Lean Markdown Reading: Reference Origins

## Purpose

This file documents the external projects, principles, and design decisions
that informed the Lean Markdown Reading skill. It exists to make the skill's
reasoning auditable — any agent or maintainer can trace why a particular
rule exists back to a concrete source.

---

## Source 1 — QMD Search (tobi/qmd)

**Repository:** https://github.com/tobi/qmd  
**Type:** Local hybrid search engine for markdown collections  
**Stars at time of reference:** ~6,500

### Principles borrowed

**Tiered retrieval pattern**
QMD Search operates in three tiers: fast keyword match (BM25) first,
semantic vector search second, LLM reranking last. The skill adapts this
as a reading tier hierarchy: map structure first, keyword-target sections
second, deep-read only what passes both gates. The core insight is that
you should never do expensive work before cheaper work has narrowed the
scope.

**Natural breakpoint chunking**
QMD Search chunks documents at natural markdown breakpoints — headings,
section breaks, paragraph boundaries — rather than at arbitrary token
counts. The skill's P2 (Natural Breakpoint Chunking) and the H1–H3
heading-as-chunk-boundary rule come directly from this. Arbitrary token
slicing breaks semantic units. Heading-based chunking preserves them.

**Relevance gating before retrieval**
QMD Search uses `--min-score` thresholds to filter results before
returning them to the caller. The skill's P3 (Relevance Gating) and P4
(Token Budget Awareness) translate this into a pre-read decision: the
agent establishes relevance before loading a chunk, not after. The
`--min-score` concept becomes the ~300 token budget rule — a chunk that
is large and only possibly relevant should be treated the same way a
low-score search result is treated: skip it unless a higher-confidence
signal emerges.

**Search mode discipline**
QMD Search explicitly warns against using `vsearch` (slow, cold-start
model load) when `search` (fast BM25) will do. This maps directly to the
skill's skip zone philosophy: do not use expensive reading when structural
navigation suffices. The temptation to read speculatively is the agent
equivalent of running `qmd query` on every search.

### What was not borrowed

QMD Search is a tool that requires installation, indexing, and a live
process. This skill deliberately requires none of that. The skill extracts
QMD Search's *behavioral principles* and applies them as agent reading
discipline, not as a dependency on the tool itself.

---

## Source 2 — QMD Syntax (ajithraghavan/qmd)

**Repository:** https://github.com/ajithraghavan/qmd  
**Type:** Token-efficient markdown syntax specification for LLM consumption  
**Version referenced:** v1.0

### Principles borrowed

**Token overhead is real and measurable**
The QMD Syntax project quantifies what the Lean Reading skill treats as
an axiom: markdown formatting characters themselves consume tokens, and
multi-character sequences waste more than single-character equivalents.
The project's benchmark of 20–30% token reduction from syntax compression
alone grounds the skill's motivation. If syntax overhead at the character
level is worth optimizing, structural overhead at the file level — loading
irrelevant sections — is worth optimizing far more aggressively.

**Token estimate reference (from QMD Syntax benchmarks)**
The QMD Syntax comparison (231 bytes traditional vs 217 bytes QMD for a
~25 line document) provides a real-world density anchor. At roughly
8–9 bytes per token for mixed prose and markup, this suggests:

| Content type             | Approx lines | Approx tokens |
| ------------------------ | ------------ | ------------- |
| Dense prose paragraphs   | 10 lines     | ~120 tokens   |
| Mixed prose + lists      | 20 lines     | ~200 tokens   |
| List/table heavy content | 35–40 lines  | ~300 tokens   |
| Code block heavy content | 25–30 lines  | ~300 tokens   |

This table is the grounding for SKILL.md's ~300 token budget threshold.
It is an estimate, not a precise measurement. Use it as a gut-check,
not a hard limit.

**Minimal ambiguity as a design goal**
QMD Syntax's principle that each marker should have one clear purpose
informed the skip zone list design. Skip zones are defined by structural
role (e.g. "barrel export table", "verification checklist") not by
content keywords, because role-based classification has minimal ambiguity.
An agent can identify a skip zone without reading its content.

**Single-character efficiency principle**
The core QMD Syntax insight — that token count is a function of how
information is encoded, not just how much information exists — informs
the skill's extraction philosophy. When an agent reads a 40-line section
and extracts 6 facts, the output is those 6 facts, not a reproduction of
the 40 lines. Compression happens at the extraction step, not just at
the selection step.

### What was not borrowed

The actual QMD Syntax markers (`!` for H1, `>` for H2, `*` for bold,
etc.) are not used or required by this skill. This skill operates on
standard markdown files. The syntax project is referenced for its
principles and benchmarks only, not as a format dependency.

---

## Source 3 — QMD Search Skill Definition (tobi/qmd/skills/qmd)

**Path:** https://github.com/tobi/qmd/tree/main/skills/qmd  
**Type:** Agent skill definition shipped with the QMD Search tool

### Principles borrowed

**Skill behavior defined separately from tool behavior**
The QMD project ships its own skill file that tells agents *how to use*
the tool — when to prefer `qmd search` over `qmd vsearch`, when to avoid
`qmd query`, how to interpret results. This separation of tool capability
from agent behavior discipline is the direct model for how this skill
is structured. SKILL.md defines how an agent should behave when reading
markdown; it does not define a tool.

**Default behavior specification**
The QMD skill explicitly sets defaults: prefer `qmd search`, only use
`vsearch` when keyword search fails, avoid `qmd query` for interactive
use. This pattern of explicit defaults with named escalation conditions
is reflected in the Lean Reading skill's tiered procedure: Step 1 (map)
is always run, Step 4 (flat file fallback) is only reached when Steps 1–2
cannot apply, re-reads are only allowed under the re-entry rule.

**Trigger phrase design**
The QMD skill defines specific natural language trigger phrases that
indicate when the skill should activate. The Lean Reading skill's
"When To Use" section follows this pattern: concrete conditions, not
vague guidelines.

---

## Source 4 — Project Context (skill_set_library AGENTS.md)

**Path:** AGENTS.md in the skill_set_library repository  
**Type:** Mandatory policy and skill contract for all skills in this library

### Constraints applied

The AGENTS.md defines the required structure for all skills in this
library: `SKILL.md` as the authoritative behavior definition, optional
`examples/`, `scripts/`, `assets/`, and `references/` directories.
This `SOURCES.md` file exists because AGENTS.md requires skills to be
auditable and self-contained.

The repository-scoped execution model and filesystem safety rules from
AGENTS.md are incorporated directly into SKILL.md's File Access
Constraints section. They are not restated here in full — see AGENTS.md
sections 2 and 3 for the authoritative rules.

---

## Versioning Note

These sources were reviewed at the time this skill was authored.
If the referenced repositories introduce breaking changes to their
core principles or if the AGENTS.md policy is updated, this file
and SKILL.md should be reviewed for consistency.

Maintainer: review this file any time a skip zone is added or removed,
or any time a procedure step in SKILL.md is changed, to confirm the
source rationale still holds.