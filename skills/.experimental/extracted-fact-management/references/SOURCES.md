# SOURCES.md — Extracted Fact Management: Reference Origins

## Purpose

Documents the external projects, research, and implementations that
informed the Extracted Fact Management skill. Every major design
decision in SKILL.md traces back to at least one source here.

---

## Source 1 — LangGraph `interrupt` and Persistence Layer
**URL:** https://blog.langchain.com/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt/  
**Type:** Official LangChain blog post announcing the `interrupt` primitive  
**Relevance:** Tier 1 — primary reference

### Principles borrowed

**Persistence as a first-class citizen**
LangGraph checkpoints every step of graph execution by reading from
and writing to a persistent state store. This is the direct model for
the skill's checkpoint schema and Phase 3 freeze protocol. The insight
that an interrupted thread "doesn't take up any resources beyond storage
space, and can be resumed many months later on a different machine" is
the behavioral principle behind F-3 (checkpoint after every step) and
the Phase 4 resumption procedure.

**The scratchpad framing**
LangGraph describes its persistence layer as "a scratchpad for
human/agent collaboration." This framing is the origin of the fact
ledger concept — not a transcript, not a summary, but a structured
working surface that both the agent and the human can inspect and edit.

**Four HITL interaction patterns**
LangGraph identifies four canonical human-in-the-loop patterns:
Approve/Reject, Review & Edit State, Review Tool Calls, and Multi-turn
conversation. These map directly onto the skill's four interruption
classes: GATE, CLARIFY, GATE (tool variant), and SOFT/CLARIFY/REDIRECT
respectively. The skill's classification table is a behavioral
translation of these four patterns into natural language signals an
agent can recognize without a framework.

**Resumption reruns the interrupted node, not previous nodes**
LangGraph's `interrupt` reruns any work done in the current node before
the interrupt point, but no previous nodes. This is the technical basis
for the skill's rule that resumption always starts from the last
completed checkpoint — not from mid-step — because mid-step state is
not guaranteed to be clean.

### What was not borrowed
LangGraph's `interrupt` is a Python primitive requiring a specific
graph execution framework. This skill extracts its behavioral principles
as agent discipline, not as a framework dependency. No LangGraph
installation or graph structure is required.

---

## Source 2 — OpenAI Agents SDK: Human-in-the-Loop
**URL:** https://openai.github.io/openai-agents-python/human_in_the_loop/  
**Type:** Official OpenAI Agents SDK documentation  
**Relevance:** Tier 1 — primary reference

### Principles borrowed

**RunState serialization as the pause/resume mechanism**
The OpenAI SDK surfaces interruptions through a serializable `RunState`
object. Any pending approvals are stored in the run state so the agent
can be paused, the state handed off, and execution resumed — potentially
on a different machine or in a future session. This is the direct model
for the skill's checkpoint schema field `ledger_snapshot`: a full
serializable capture of all fact statuses at the moment of pause.

**Interruptions are run-wide, not node-local**
The SDK makes clear that approval interruptions surface at the outer
run level regardless of how deeply nested the tool call is. The skill's
F-4 invariant (freeze the ledger before any interruption response)
reflects this: the freeze happens at the task level, not at whatever
sub-step triggered the interruption.

**Versioning pending tasks**
The SDK documentation on long-running approvals introduces the concept
of versioning: a pending task can become outdated if the underlying
state changes before the human responds. The skill's UNVERIFIED
freshness marker and the staleness rules for session gaps directly
implement this concept behaviorally — a fact extracted in session A
may be UNVERIFIED by the time the human resumes in session B.

**Typed approval decisions**
The SDK distinguishes between approval decisions scoped to a specific
call ID versus decisions that apply always. This maps onto the skill's
interruption class distinction: a GATE interruption is scoped to the
specific next action (approve this step), while a REDIRECT is a
global change that affects all remaining steps.

### What was not borrowed
The SDK's `needs_approval` decorator and `RunContextWrapper` are
implementation-specific. The skill adapts the behavioral contract
(pause, surface, wait, resume or rollback) without requiring the SDK.

---

## Source 3 — Deep Dive: State Management in AI Agents
**URL:** https://leucir-marin.medium.com/deep-dive-state-management-in-ai-agents-lessons-from-a-real-world-system-0dab053ab4b8  
**Type:** Technical deep-dive on LangGraph state architecture from a
production Five Whys analysis agent  
**Relevance:** Tier 1 — primary reference for ledger structure

### Principles borrowed

**Validate at boundaries, not internally**
The article establishes that validation overhead on every field access
is prohibitive in AI agent systems. The skill applies this as: fact
units are validated when they enter the ledger (at extraction) and
when they are consumed by a step (at use) — not on every ledger read.
This keeps the ledger lean and the per-step execution fast.

**Keep it serializable**
The article's recommendation to use simple data types, avoid complex
objects, and design for `json.dumps()` compatibility is the basis for
the fact unit schema design. Every field in the schema is a string,
number, or simple list — nothing that requires special serialization.

**Design for debugging**
The article argues that AI agents are complex and unpredictable, so
state structures must be readable by a human at any point without
special tooling. The skill's ledger state output contract (the agent
can produce current ledger state at any time in plain language) is a
direct implementation of this principle.

**Optimize for cost: focused context views**
The article reports 30–50% LLM cost reduction from proper state
management through focused context creation and minimizing state size.
The skill's token efficiency rules — fact content is one sentence not
a paragraph, checkpoint snapshots record IDs and statuses not full
content, CONSUMED facts are archived not re-loaded on resumption —
all derive from this principle.

**Start with structure, add flexibility gradually**
The article's recommendation to define core fields first and add
optional fields only as needed informs the fact unit schema design:
the required fields (id, source, content, status) are always present;
`consumed_by`, `freshness`, and `notes` are populated as needed.

### What was not borrowed
The TypedDict implementation and LangGraph-specific node architecture
are Python-framework-specific. The skill extracts the structural
philosophy as behavioral discipline for any agent, regardless of
implementation framework.

---

## Source 4 — Zapier: Human-in-the-Loop in AI Workflows
**URL:** https://zapier.com/blog/human-in-the-loop/  
**Type:** Practitioner guide to HITL patterns in production automation  
**Relevance:** Tier 2 — taxonomy reference

### Principles borrowed

**Three-class interruption taxonomy**
Zapier's practical guide distinguishes between approval gates (pause
before risky action), clarification loops (agent needs more info), and
correction flows (human redirects). This three-way split is the
foundation for the skill's four-class system: SOFT and CLARIFY emerge
from the clarification loop category, GATE from the approval gate
category, and REDIRECT from the correction flow category. SOFT was
added as a distinct class because a pure question (no new information,
no direction change) requires a different protocol than a clarification
that carries new facts.

**Highest-impact class wins**
Zapier's observation that a single message can contain multiple
interruption signals informed the skill's conflict resolution rule:
when signals from multiple classes appear in one message, apply
REDIRECT > GATE > CLARIFY > SOFT. The higher the potential impact on
the task state, the higher the class priority.

### What was not borrowed
Zapier's specific workflow primitives and automation platform
implementation are not referenced. Only the behavioral taxonomy
is borrowed.

---

## Source 5 — Lumenalta: 8 Tactics to Reduce Context Drift
**URL:** https://lumenalta.com/insights/8-tactics-to-reduce-context-drift-with-parallel-ai-agents  
**Type:** Practitioner guide to context drift in parallel agent systems  
**Relevance:** Tier 2 — staleness and fact invalidation reference

### Principles borrowed

**Central shared task spec as single source of truth**
Lumenalta's first tactic is a single living document that every agent
thread pulls from, preventing drift from scattered requirements.
The skill's ledger initialization procedure (one ledger, one task
header, all source files declared upfront) implements this as agent
behavior: there is always one canonical ledger, never parallel copies.

**Agents treat all text as equally reliable**
The article's observation that agents treat outdated docs with the
same confidence as current ones is the behavioral problem the
UNVERIFIED freshness marker solves. Marking facts as UNVERIFIED
after a session gap forces the agent to re-verify before using them,
rather than silently trusting stale extractions.

**Context drift is a systems issue, not a personal failure**
The article frames drift as an architectural concern, not a prompting
failure. This framing justifies building the ledger as a structural
constraint — not a recommendation the agent can choose to ignore —
with hard invariants (F-1 through F-8) that enforce correct behavior
regardless of conversational pressure.

### What was not borrowed
The parallel agent coordination tactics and multi-thread branch
management strategies are not directly applicable to single-agent
sequential implementation tasks.

---

## Source 6 — OpenAI Community: Preventing Doc Drift in Agentic Coding
**URL:** https://community.openai.com/t/show-preventing-doc-drift-in-agentic-coding-workflows/1375031  
**Type:** Community discussion thread on VeriContext, a hash-based doc
verification tool  
**Relevance:** Tier 2 — fact freshness and staleness detection reference

### Principles borrowed

**Docs drift while agents still treat them as ground truth**
The thread's core observation — that documentation drifts while agents
continue to follow stale instructions as if they were current — is
the problem the skill's staleness rules address. The five concrete
staleness triggers (explicit correction, file change mention, session
gap on mutable files, contradicting output, redirect making it
irrelevant) are a behavioral translation of this problem: rather than
hash-verifying every file on every step, the skill uses human signals
and structural contradictions to detect when re-verification is needed.

**Fail-closed on verification**
VeriContext uses strict hash matching with no fuzzy fallback — if the
hash doesn't match, the verification fails. The skill applies this
principle to fact consumption: F-6 (STALE facts are never used) is
fail-closed. An agent that encounters a STALE fact must replace it
before proceeding, not make a judgment call about whether it's
"probably still valid."

**Short random codes for tracking findings across a conversation**
The thread contributor who adds random codes to each finding to
track them across long conversations is the direct inspiration for
the fact unit ID schema (step-number-sequence format like `2-3`).
The ID gives both the agent and the human a stable reference to
a specific fact that survives across interruptions and resumptions.

### What was not borrowed
VeriContext's SHA-256 hashing implementation and pre-commit hook
integration are tool-level solutions. The skill extracts the
fail-closed verification principle and stable fact identification
pattern as behavioral rules.

---

## Source 7 — Agent-Deck (asheshgoplani)
**URL:** https://github.com/asheshgoplani/agent-deck  
**Type:** Terminal session manager for AI coding agents (Go + Bubble Tea)  
**Relevance:** Tier 2 — real-world problem validation

### Principles borrowed

**Session state as a first-class object**
Agent-Deck treats each agent session as a named, addressable unit of
work that persists independently and can be switched between. The
insight that agents lose context when you switch tasks validates the
skill's core problem statement — context loss during interruption is
real and costly enough that people build dedicated tooling to address
it. The skill addresses this at the behavioral level: the ledger is
the session state that prevents context loss without requiring a
dedicated session manager.

### What was not borrowed
The Go implementation, terminal UI, and multi-session management
features are tool-specific. The skill is framework-agnostic and
addresses the underlying problem behaviorally.

---

## Source 8 — Lean Markdown Reading Skill (this repository)
**Path:** `../lean-markdown-reading/SKILL.md`  
**Type:** Companion skill in this library  
**Relevance:** Direct dependency

### Integration points documented

The Extracted Fact Management skill depends on Lean Markdown Reading
for all fact extraction. The dependency is explicitly one-directional:
Lean Reading produces facts; this skill manages them. Lean Reading
does not need to know this skill exists.

Three integration points are formalized in SKILL.md:

1. Lean Reading extracts → this skill records immediately (F-1)
2. This skill triggers re-reads for UNVERIFIED facts, using Lean
   Reading's re-entry rule (declared gap required before re-read)
3. Unused facts at closure feed calibration signals back to Lean
   Reading (over-reading indicator)

---

## Versioning Note

These sources were reviewed at the time this skill was authored.
The LangGraph and OpenAI Agents SDK documentation in particular
evolves frequently. If the `interrupt` API or `RunState` interface
changes significantly, review SKILL.md Phase 3 and Phase 4 for
alignment with updated patterns.

Maintainer: review this file any time an interruption class is added
or removed, or any time the checkpoint or fact unit schema changes,