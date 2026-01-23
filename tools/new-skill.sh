#!/usr/bin/env bash
# tools/new-skill.sh
#
# Scaffold a new skill folder for skill_set_library.
#
# What it does:
# - Validates kebab-case skill name
# - Creates a new skill directory in skills/ or skills/.experimental/
# - Copies a SKILL.md template and substitutes name/description
# - Optionally creates common subfolders
# - Runs the validator (tools/validate.py) if available
#
# Usage:
#   ./tools/new-skill.sh <skill-name> [--description "…"] [--experimental] [--with scripts,examples,assets,references] [--no-validate]
#
# Examples:
#   ./tools/new-skill.sh repo-health-check --description "Generate a repo health report."
#   ./tools/new-skill.sh draft-pr-helper --experimental --with scripts,examples
#
set -euo pipefail

# -----------------------------
# Helpers
# -----------------------------
err() { printf "ERROR: %s\n" "$*" >&2; }
info() { printf "%s\n" "$*"; }

is_kebab_case() {
  local s="$1"
  [[ "$s" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]
}

usage() {
  cat <<'EOF'
Create a new skill scaffold.

Usage:
  ./tools/new-skill.sh <skill-name> [options]

Options:
  --description "..."      One-line description for SKILL.md front matter.
  --experimental           Create under skills/.experimental/<skill-name>/ instead of skills/<skill-name>/.
  --with a,b,c             Create optional subfolders (comma-separated): scripts,examples,assets,references
                           Default: scripts,examples
  --template PATH          Path to SKILL.md template. Default: skills/_template/SKILL.md then skills/_schema/SKILL.template.md
  --no-validate            Do not run python tools/validate.py at the end.
  -h, --help               Show this help.

Examples:
  ./tools/new-skill.sh repo-health-check --description "Generate a repo health report."
  ./tools/new-skill.sh draft-pr-helper --experimental --with scripts,examples,assets
EOF
}

# Escape a string for safe insertion into YAML in a single line.
# We quote the value and escape backslashes and quotes.
yaml_quote() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf "\"%s\"" "$s"
}

# Portable in-place replacement:
# writes to a temp file then moves into place (avoids sed -i differences).
replace_in_file() {
  local file="$1"
  local search="$2"
  local replace="$3"

  local tmp
  tmp="$(mktemp)"
  # Use sed with a delimiter unlikely to appear
  sed "s|${search}|${replace}|g" "$file" > "$tmp"
  mv "$tmp" "$file"
}

# Find repo root (where skills/ lives), starting from this script location.
find_repo_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local cur="$script_dir"
  for _ in $(seq 1 10); do
    if [[ -d "$cur/skills" ]]; then
      echo "$cur"
      return 0
    fi
    cur="$(cd "$cur/.." && pwd)"
  done
  # fallback: current working dir
  if [[ -d "$(pwd)/skills" ]]; then
    pwd
    return 0
  fi
  return 1
}

# -----------------------------
# Args
# -----------------------------
if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

SKILL_NAME=""
DESCRIPTION="One-line description of what this skill does, written for an agent."
EXPERIMENTAL="false"
WITH_FOLDERS="scripts,examples"
TEMPLATE_PATH=""
RUN_VALIDATE="true"

# First positional is skill name unless it looks like an option
if [[ "${1:-}" == -* ]]; then
  err "First argument must be <skill-name>."
  usage
  exit 1
fi
SKILL_NAME="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description)
      shift
      if [[ $# -eq 0 ]]; then err "--description requires a value"; exit 1; fi
      DESCRIPTION="$1"
      shift
      ;;
    --experimental)
      EXPERIMENTAL="true"
      shift
      ;;
    --with)
      shift
      if [[ $# -eq 0 ]]; then err "--with requires a comma-separated list"; exit 1; fi
      WITH_FOLDERS="$1"
      shift
      ;;
    --template)
      shift
      if [[ $# -eq 0 ]]; then err "--template requires a path"; exit 1; fi
      TEMPLATE_PATH="$1"
      shift
      ;;
    --no-validate)
      RUN_VALIDATE="false"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "Unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

# -----------------------------
# Validation
# -----------------------------
if ! is_kebab_case "$SKILL_NAME"; then
  err "Skill name must be kebab-case (e.g., 'repo-health-check'). Got: '$SKILL_NAME'"
  exit 1
fi

REPO_ROOT="$(find_repo_root)" || {
  err "Could not find repo root (expected a skills/ directory). Run from inside the repo."
  exit 1
}

SKILLS_ROOT="$REPO_ROOT/skills"
DEST_DIR="$SKILLS_ROOT/$SKILL_NAME"
if [[ "$EXPERIMENTAL" == "true" ]]; then
  DEST_DIR="$SKILLS_ROOT/.experimental/$SKILL_NAME"
fi

if [[ -e "$DEST_DIR" ]]; then
  err "Destination already exists: $DEST_DIR"
  exit 1
fi

# Determine template path
if [[ -n "$TEMPLATE_PATH" ]]; then
  if [[ ! -f "$TEMPLATE_PATH" ]]; then
    err "Template not found: $TEMPLATE_PATH"
    exit 1
  fi
else
  # Preferred defaults (in order)
  if [[ -f "$SKILLS_ROOT/_template/SKILL.md" ]]; then
    TEMPLATE_PATH="$SKILLS_ROOT/_template/SKILL.md"
  elif [[ -f "$SKILLS_ROOT/_schema/SKILL.template.md" ]]; then
    TEMPLATE_PATH="$SKILLS_ROOT/_schema/SKILL.template.md"
  else
    err "No template found. Expected one of:"
    err "  - skills/_template/SKILL.md"
    err "  - skills/_schema/SKILL.template.md"
    err "Or pass --template PATH"
    exit 1
  fi
fi

# -----------------------------
# Scaffold
# -----------------------------
info "Repo root: $REPO_ROOT"
info "Creating skill: $SKILL_NAME"
info "Location: $DEST_DIR"
mkdir -p "$DEST_DIR"

# Copy template
cp "$TEMPLATE_PATH" "$DEST_DIR/SKILL.md"

# Substitute front matter fields (strict + safe)
# We replace the first occurrence of these exact template strings if present.
# (Your template should contain these placeholders.)
NAME_QUOTED="$(yaml_quote "$SKILL_NAME")"
DESC_QUOTED="$(yaml_quote "$DESCRIPTION")"

# Replace "name: my-skill" and "description: One-line ..."
# Keep replacements compatible whether template uses quoted or unquoted values.
replace_in_file "$DEST_DIR/SKILL.md" "^name: .*" "name: ${SKILL_NAME}"
replace_in_file "$DEST_DIR/SKILL.md" "^description: .*" "description: ${DESCRIPTION}"

# Create optional subfolders
IFS=',' read -r -a folders <<< "$WITH_FOLDERS"
for f in "${folders[@]}"; do
  f="$(echo "$f" | tr -d '[:space:]')"
  [[ -z "$f" ]] && continue
  case "$f" in
    scripts|examples|assets|references)
      mkdir -p "$DEST_DIR/$f"
      ;;
    *)
      err "Unknown folder in --with: '$f' (allowed: scripts,examples,assets,references)"
      exit 1
      ;;
  esac
done

# Add a tiny placeholder file to examples if created, to encourage good hygiene
if [[ -d "$DEST_DIR/examples" && ! -e "$DEST_DIR/examples/README.md" ]]; then
  cat > "$DEST_DIR/examples/README.md" <<'EOF'
# Examples

Add safe, repo-scoped examples of how this skill should be used.
Do not reference home/system paths. Follow AGENTS.md.
EOF
fi

info "Scaffold created."

# -----------------------------
# Validate
# -----------------------------
if [[ "$RUN_VALIDATE" == "true" ]]; then
  if [[ -f "$REPO_ROOT/tools/validate.py" ]]; then
    if command -v python >/dev/null 2>&1; then
      info "Running validator..."
      (cd "$REPO_ROOT" && python tools/validate.py)
      info "Validator passed."
    else
      err "Python not found; skipping validation. (Install Python or run: python tools/validate.py)"
    fi
  else
    err "Validator not found at tools/validate.py; skipping validation."
  fi
else
  info "Validation skipped (--no-validate)."
fi

info "Next steps:"
info "  1) Edit: $(realpath "$DEST_DIR/SKILL.md" 2>/dev/null || echo "$DEST_DIR/SKILL.md")"
info "  2) Keep all paths repo-scoped (see AGENTS.md)."
info "  3) Re-run: python tools/validate.py"