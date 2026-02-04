#!/usr/bin/env python3
"""
tools/validate.py

Validator for skill_set_library skills against AGENTS.md "contract" + repo policies.

What it checks:
- Skill folder structure: skills/<skill>/SKILL.md exists (also supports skills/.experimental/<skill>/SKILL.md)
- YAML front matter in SKILL.md includes required fields: name, description
- Folder name matches front matter `name`
- Skill name + folder name are kebab-case
- No unsafe filesystem references in SKILL.md or any files under the skill directory:
  - home dirs (~, $HOME, /home/*, /Users/*)
  - system dirs (/etc, /bin, /usr, /opt, /var)
  - path traversal beyond repo (../)
  - dangerous commands (rm -rf, sudo, etc.) - heuristic scanning
- No symlinks in the skill directory that point outside the repo root

How to run:
  python tools/validate.py
  python tools/validate.py --verbose
  python tools/validate.py --repo-root /path/to/skill_set_library

Exit codes:
  0 = all good
  1 = validation errors found
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# -----------------------------
# Repo policy / contract rules
# -----------------------------

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Heuristic "unsafe" patterns. This is intentionally strict.
UNSAFE_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # Home directory references
    # Avoid matching markdown code fences like "~~~"
    ("home-tilde", re.compile(r"(^|[^\w])(?<!~)~([/\\]|$)")),
    ("home-env", re.compile(r"\$(HOME|USERPROFILE)\b")),
    ("home-path-linux", re.compile(r"(^|[^\w])/(home|root)/")),
    ("home-path-macos", re.compile(r"(^|[^\w])/Users/")),

    # System directories
    ("system-etc", re.compile(r"(^|[^\w])/etc/")),
    ("system-bin", re.compile(r"(^|[^\w])/bin/")),
    ("system-usr", re.compile(r"(^|[^\w])/usr/")),
    ("system-opt", re.compile(r"(^|[^\w])/opt/")),
    ("system-var", re.compile(r"(^|[^\w])/var/")),

    # Path traversal
    ("path-traversal", re.compile(r"(^|[^\w])\.\./")),

    # Sensitive file hints (common)
    ("ssh-keys", re.compile(r"\.ssh/")),
    ("dotenv", re.compile(r"(^|[^\w])\.env(\b|$)")),
]

# Command heuristics (not perfect, but catches obvious violations)
DANGEROUS_COMMANDS: List[Tuple[str, re.Pattern]] = [
    ("rm-rf", re.compile(r"(^|\s)rm\s+-rf(\s|$)")),
    ("rm-force", re.compile(r"(^|\s)rm\s+-f(\s|$)")),
    ("sudo", re.compile(r"(^|\s)sudo(\s|$)")),
    ("chmod-777", re.compile(r"(^|\s)chmod\s+777(\s|$)")),
    ("chown-root", re.compile(r"(^|\s)chown\s+root(\s|$)")),
]


# Files we skip scanning to avoid noise / binary problems.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".pdf",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".woff", ".woff2", ".ttf", ".otf",
}
SKIP_SKILLS = {"_template"}

# Max file size (bytes) to scan as text
MAX_SCAN_BYTES = 800_000  # 800KB

# Required markers for example files under examples/
EXAMPLE_REQUIRED_MARKERS = [
    "## ❌ BROKEN EXAMPLE (DO NOT COPY)",
    "What breaks",
    "BROKEN DIFF (DO NOT COPY)",
    "--- a/",
    "+++ b/",
]


@dataclass
class Issue:
    level: str  # "ERROR" or "WARN"
    where: str
    message: str


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def find_repo_root(start: Path) -> Path:
    # Prefer explicit repo root: if there's a skills/ directory, treat as root.
    # Otherwise walk upward until found.
    cur = start.resolve()
    for _ in range(10):
        if (cur / "skills").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


def list_skill_dirs(repo_root: Path) -> List[Path]:
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        return []

    skill_dirs: List[Path] = []

    # Stable skills: skills/<skill>/
    for p in skills_root.iterdir():
        if p.name in SKIP_SKILLS:
            continue
        if not p.is_dir():
            continue
        if p.name.startswith("."):
            continue
        if p.name == ".experimental":
            continue
        skill_dirs.append(p)

    # Experimental skills: skills/.experimental/<skill>/
    exp_root = skills_root / ".experimental"
    if exp_root.is_dir():
        for p in exp_root.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                skill_dirs.append(p)

    return sorted(skill_dirs, key=lambda x: str(x).lower())


def read_text_safely(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            return None
        data = path.read_bytes()
        # Quick binary sniff: null byte => treat as binary
        if b"\x00" in data:
            return None
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def parse_front_matter(text: str) -> Tuple[Dict[str, str], int]:
    """
    Lightweight front matter parser that allows nested YAML.
    Expects:
      ---
      <any yaml>
      ---
    Returns (dict with at least name/description if found, end_index) or ({}, -1).
    """
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, -1

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return {}, -1

    block = "\n".join(lines[1:end_idx])
    fm: Dict[str, str] = {}
    for key in ("name", "description"):
        m = re.search(rf"^{key}\s*:\s*(.+?)\s*$", block, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val

    return fm, end_idx


def path_within(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def scan_text_for_unsafe(content: str) -> List[str]:
    hits: List[str] = []
    for label, pat in UNSAFE_PATTERNS:
        if pat.search(content):
            hits.append(label)
    for label, pat in DANGEROUS_COMMANDS:
        if pat.search(content):
            hits.append(f"dangerous-cmd:{label}")
    return sorted(set(hits))


def should_skip_file(path: Path) -> bool:
    if path.suffix.lower() in SKIP_EXTS:
        return True
    return False


def missing_example_markers(content: str) -> List[str]:
    missing: List[str] = []
    for marker in EXAMPLE_REQUIRED_MARKERS:
        if marker not in content:
            missing.append(marker)
    return missing


def validate_skill_dir(repo_root: Path, skill_dir: Path, verbose: bool) -> List[Issue]:
    issues: List[Issue] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        issues.append(Issue("ERROR", str(skill_dir), "Missing required SKILL.md"))
        return issues

    # Folder naming policy (kebab-case)
    if not KEBAB_CASE_RE.match(skill_dir.name):
        issues.append(Issue(
            "ERROR",
            str(skill_dir),
            f"Skill folder name must be kebab-case (got '{skill_dir.name}')"
        ))

    # Parse front matter
    text = read_text_safely(skill_md)
    if text is None:
        issues.append(Issue("ERROR", str(skill_md), "SKILL.md unreadable or too large/binary"))
        return issues

    fm, end_idx = parse_front_matter(text)
    if end_idx == -1:
        issues.append(Issue(
            "ERROR",
            str(skill_md),
            "SKILL.md must start with YAML front matter delimited by '---' lines"
        ))
        return issues

    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()

    if not name:
        issues.append(Issue("ERROR", str(skill_md), "Front matter missing required field: name"))
    if not desc:
        issues.append(Issue("ERROR", str(skill_md), "Front matter missing required field: description"))

    if name and not KEBAB_CASE_RE.match(name):
        issues.append(Issue(
            "ERROR",
            str(skill_md),
            f"Front matter 'name' must be kebab-case (got '{name}')"
        ))

    if name and name != skill_dir.name:
        issues.append(Issue(
            "ERROR",
            str(skill_md),
            f"Front matter name '{name}' must match folder name '{skill_dir.name}'"
        ))

    # Safety scan SKILL.md
    hits = scan_text_for_unsafe(text)
    if hits:
        issues.append(Issue(
            "ERROR",
            str(skill_md),
            f"Unsafe patterns detected in SKILL.md: {', '.join(hits)}"
        ))

    # Scan files under skill dir
    for root, dirs, files in os.walk(skill_dir):
        root_path = Path(root)

        # Skip noisy dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for fn in files:
            p = root_path / fn
            if p.name.startswith("."):
                continue
            if should_skip_file(p):
                continue

            # Symlink checks
            if p.is_symlink():
                try:
                    resolved = p.resolve()
                except Exception:
                    issues.append(Issue("ERROR", str(p), "Symlink could not be resolved"))
                    continue

                if not path_within(repo_root, resolved):
                    issues.append(Issue(
                        "ERROR",
                        str(p),
                        f"Symlink points outside repo root: {resolved}"
                    ))
                continue

            # Text safety scan
            content = read_text_safely(p)
            if content is None:
                # Not necessarily an error—could be binary or too large
                if verbose:
                    issues.append(Issue("WARN", str(p), "Skipped scanning (binary/too large/unreadable)"))
                continue

            file_hits = scan_text_for_unsafe(content)
            if file_hits:
                issues.append(Issue(
                    "ERROR",
                    str(p),
                    f"Unsafe patterns detected: {', '.join(file_hits)}"
                ))

            # Enforce broken example outline for examples/*.md (excluding README.md)
            if p.suffix.lower() == ".md" and "examples" in p.parts and p.name.lower() != "readme.md":
                missing = missing_example_markers(content)
                if missing:
                    issues.append(Issue(
                        "ERROR",
                        str(p),
                        "Examples must include the broken example outline markers: "
                        + ", ".join(missing)
                    ))

    # Disallow symlink directories that escape repo
    for p in skill_dir.rglob("*"):
        if p.is_dir() and p.is_symlink():
            try:
                resolved = p.resolve()
            except Exception:
                issues.append(Issue("ERROR", str(p), "Symlink dir could not be resolved"))
                continue
            if not path_within(repo_root, resolved):
                issues.append(Issue(
                    "ERROR",
                    str(p),
                    f"Symlink directory points outside repo root: {resolved}"
                ))

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate skills against AGENTS.md contract.")
    ap.add_argument("--repo-root", type=str, default=None, help="Path to repo root (defaults to auto-detect).")
    ap.add_argument("--verbose", action="store_true", help="Print extra info (e.g., skipped files).")
    args = ap.parse_args()

    start = Path.cwd()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root(start)
    skills_root = repo_root / "skills"

    if not skills_root.is_dir():
        eprint(f"ERROR: Could not find skills/ directory at repo root: {repo_root}")
        return 1

    skill_dirs = list_skill_dirs(repo_root)
    if not skill_dirs:
        eprint(f"WARN: No skills found under {skills_root}")
        return 0

    all_issues: List[Issue] = []
    for sd in skill_dirs:
        issues = validate_skill_dir(repo_root, sd, args.verbose)
        all_issues.extend(issues)

    # Print report
    errors = [i for i in all_issues if i.level == "ERROR"]
    warns = [i for i in all_issues if i.level == "WARN"]

    if errors or warns:
        print("Skill Validation Report")
        print("=" * 80)

    for i in errors + warns:
        print(f"[{i.level}] {i.where}\n  - {i.message}")

    if errors:
        print("\nResult: FAILED")
        print(f"Errors: {len(errors)}  Warnings: {len(warns)}")
        return 1

    print("Result: OK")
    if warns:
        print(f"Warnings: {len(warns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
