# skill_set_library

A curated, repo-scoped library of Codex skills.

This repo is designed so skills can be:
- **Used by an agent from within a target repository** (repo-scoped skills)
- **Shared/downloaded in bulk** (clone the repo)
- **Installed individually or in groups** using the Codex CLI `$skill-installer` (prompted to pull from this repository)

---

## Safety First

This repository enforces strict safety rules via **AGENTS.md**.

### Hard rule
Skills and agents **must never** read, write, modify, or delete anything in:
- the user home directory (`~`, `/home/*`, `/Users/*`)
- system directories (`/etc`, `/usr`, `/bin`, `/opt`, `/var`)
- anything outside the target repository root

If a user asks for unsafe access, the agent/skill must refuse and provide a repo-scoped alternative.

See: `AGENTS.md`

---

## Repo Layout

Skills live under:

- `skills/<skill-name>/SKILL.md`
- `skills/.experimental/<skill-name>/SKILL.md` (unstable/volatile skills)

Each skill folder is self-contained and may include:
- `scripts/` (optional)
- `assets/` (optional)
- `references/` (optional)
- `examples/` (optional)

---

## Skill Contract

Every `SKILL.md` MUST start with YAML front matter:

```yaml
---
name: my-skill
description: Single-line description of what the skill does.
---
```

#### Additional sections inside SKILL.md should clearly define:
- purpose
- inputs/outputs
- step-by-step procedure
- guardrails and validation

## Installing Skills into a Target Repo

Skills are intended to be installed into a target repo at:

```bash
    <target-repo>/.codex/skills/<skill-name>/SKILL.md
```

## Using Codex CLI $skill-installer

Use natural-language prompts to install from this repository, for example:
- Install one skill:
    - $skill-installer install <skill-name> from the skill_set_library repository
- Install multiple skills:
    - $skill-installer install <skill-a> and <skill-b> from the skill_set_library repository
- Install an experimental skill:
    - $skill-installer install <skill-name> from the .experimental folder in the skill_set_library repository

Notes:
- Exact phrasing can vary by Codex CLI version; the key is specifying the skill name(s) and that they come from this repository.
- Skills should end up in the target repo under .codex/skills/.

## Validating Skills

A validator script is included to enforce the contract and safety rules:
```bash
python tools/validate.py

## verbose mode
python tools/validate.py --verbose
```

The validator checks:
- required SKILL.md
- required YAML front matter (name, description)
- kebab-case naming
- folder name matches name
- unsafe path references and dangerous command patterns
- symlinks that point outside the repo

## Contributing

## Adding a New Skill

There are two supported ways to add a new skill to this repository: **manual creation** and **automated scaffolding**.  
Both approaches must result in a skill that complies with `AGENTS.md` and passes validation.

---

### Manual Process (Advanced / Explicit Control)

Use this approach if you want full control over the initial layout or are migrating an existing skill.

1. Create a new folder under `skills/`:
   - Stable skill:
     ```
     skills/<skill-name>/
     ```
   - Experimental skill:
     ```
     skills/.experimental/<skill-name>/
     ```

2. Add a `SKILL.md` file inside the folder.
   - It **must** start with valid YAML front matter:
     ```yaml
     ---
     name: <skill-name>
     description: One-line description of what the skill does.
     ---
     ```
   - The `name` value must:
     - be kebab-case
     - exactly match the folder name

3. Fully document the skill behavior in `SKILL.md`.
   - Clearly describe purpose, inputs, outputs, procedure, and guardrails
   - Explicitly reference and comply with `AGENTS.md`
   - Ensure all file access is **repo-scoped only**

4. (Optional) Add supporting folders as needed:
   - `scripts/`
   - `examples/`
   - `assets/`
   - `references/`

5. Run the validator from the repo root:

   ```bash
    python tools/validate.py
   ```

Fix any reported errors before considering the skill complete.

### Automated Process (Recommended)

For most cases, use the new-skill.sh helper script.
It scaffolds a new skill using the approved template and enforces naming and structure rules up front.

What the script does
- Validates the skill name (kebab-case)
- Creates the skill folder in the correct location
- Copies the canonical SKILL.md template
- Injects the skill name and description into front matter
- Optionally creates common subfolders
- Runs the validator automatically (unless disabled)

#### **Examples**
Create a stable skill:
```bash
./tools/new-skill.sh repo-health-check --description "Generate a repository health report for agents."
```

Create an experimental skill with folders:
```bash
./tools/new-skill.sh draft-pr-helper --experimental --with scripts,examples,assets
```

#### After running the script
	1.	Open the generated SKILL.md file.
	2.	Replace all placeholder text with concrete, deterministic instructions.
	3.	Verify all paths and actions are repository-scoped.
	4.	Re-run validation if needed:

        ```bash
            python tools/validate.py
        ```

#### Experimental skills

If the skill is still changing rapidly, place it under:
- skills/.experimental/<skill-name>/

Move to skills/<skill-name>/ once it’s stable.