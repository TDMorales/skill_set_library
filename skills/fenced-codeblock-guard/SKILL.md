---
name: fenced-codeblock-guard
description: Prevent broken Markdown by ensuring all fenced code blocks are correctly opened/closed and safely nested.
---

## Purpose

When producing Markdown that contains fenced code blocks, formatting can break if a closing fence is missing (e.g., forgetting the closing backticks after a command like `python tools/validate.py`). This skill enforces a strict output policy so responses remain copy/paste-safe and do not “leak” formatting into later text.

This skill is intended to run inside a repository context and only affects the agent’s *response formatting* (not filesystem actions).

---

## Safety & Policy Compliance

This skill must comply with `AGENTS.md`.

- This skill MUST NOT access, read, write, modify, or delete any files.
- This skill MUST NOT reference or operate on home/system paths (tilde paths or OS home folders) or system directories (OS-level system folders).
- This skill only constrains how the agent formats its Markdown output.

---

## When to Use

Use this skill when:
- The user asks to “return in a code block so I can copy it”
- The response includes any fenced blocks (``` or ~~~)
- The response includes multiple code blocks, nested examples, or markdown that is likely to be copied verbatim
- The agent is writing files-as-text (README.md, scripts, configs, YAML, JSON, etc.)

---

## Inputs

- Draft response content (the text the agent is about to output)
- Optional user constraints:
  - “Put the entire response in a single code block”
  - “Use language tags (```md, ```bash, etc.)”
  - “Provide multiple files” (requires careful fence handling)

---

## Outputs

- A finalized response where:
  - Every fenced code block is correctly opened and closed
  - Nested fencing does not break formatting
  - Copy/paste behavior is reliable

---

## Procedure

### 1) Decide the fencing strategy

**If the user asks for “the whole thing in one code block”:**
- Wrap the entire content in one outer fence.
- DO NOT include inner triple-backtick fences inside that block.
  - If you must show “inner code fences” as examples, use one of:
    - Switch inner examples to `~~~` fences inside the outer fence, OR
    - Represent backticks by spacing them out (e.g., `\`\`\``) or using indentation.

**If the user does not require a single outer fence:**
- Use separate fenced blocks per file/snippet.
- Prefer consistent language tags (md/bash/yaml/json/etc.) only when helpful.

### 2) Generate the response content

- Write the content normally according to the user request.
- If multiple artifacts are present, label them clearly outside fences (e.g., “README.md”, “tools/new-skill.sh”).

### 3) Validate fences before sending (MANDATORY)

Perform these checks on the final text:

- Count opening vs. closing fences for each fence type:
  - Triple backticks: ``` 
  - Triple tildes: ~~~
- For each fence type, the total count must be even and properly paired.
- Ensure each closing fence matches the opening fence type (``` closes ```, ~~~ closes ~~~).
- Ensure there is no accidental nesting conflict:
  - If using an outer ``` fence, do not include inner ``` fences.
  - If nesting is unavoidable, outer must be ``` and inner must be ~~~ (or vice versa), consistently.

### 4) Fail-safe if validation is uncertain

If validation cannot be guaranteed:
- Prefer one single outer fenced block and avoid any inner fenced blocks entirely.
- Or output as plain text with no fences and instruct the user how to re-wrap safely.

---

## Guardrails & Validation

- NEVER leave a fenced block unclosed.
- NEVER include ``` inside an outer ``` fenced block.
- If you output a “whole file”, wrap it in exactly one fence and ensure the closing fence is present.
- If a response is long, still prioritize correct closure over extra prose.

---

## Refusal Conditions

Refuse or reformat if:
- The user requests conflicting constraints that would inevitably create broken nesting (e.g., “Put the whole response in one ``` block and also include multiple ``` blocks inside it”).
- In such cases, explain the constraint and provide a safe alternative strategy:
  - “Single outer block with escaped inner fences” or “outer fence uses ~~~”.

---

## Examples

See `skills/fenced-codeblock-guard/examples/README.md` for copy/paste-safe examples.
