# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants. Keep these minimal and adapt names to your domain.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of Abstract Factory rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Abstract Factory interfaces, concrete factories, abstract product interfaces, concrete products.
2. **Locate call sites**
   - Trace where factories are obtained and where products are created.
   - Check whether client code references concrete types directly.
3. **Map flows**
   - Selection seam → concrete factory → product family → client usage.
   - Verify that each factory produces a complete, coherent family.
4. **Check invariants**
   - Evaluate AF-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as "verified" (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant creation seams
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- pattern target:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `AF-F-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of AF-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what breaks or becomes harder to change
- **Minimal Fix:** concrete change (describe or patch snippet)
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified
  - `[ ]` not verified / missing
  - `[!]` violated (must link to finding IDs)

---

## Abstract Factory (Python)

```python
from abc import ABC, abstractmethod


class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Panel(ABC):
    @abstractmethod
    def render(self) -> str: ...


class LightButton(Button):
    def render(self) -> str:
        return "LightButton"


class LightPanel(Panel):
    def render(self) -> str:
        return "LightPanel"


class DarkButton(Button):
    def render(self) -> str:
        return "DarkButton"


class DarkPanel(Panel):
    def render(self) -> str:
        return "DarkPanel"


class ThemeFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_panel(self) -> Panel: ...


class LightThemeFactory(ThemeFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_panel(self) -> Panel:
        return LightPanel()


class DarkThemeFactory(ThemeFactory):
    def create_button(self) -> Button:
        return DarkButton()

    def create_panel(self) -> Panel:
        return DarkPanel()


def build_ui(factory: ThemeFactory) -> None:
    button = factory.create_button()
    panel = factory.create_panel()
    print(button.render(), panel.render())


build_ui(LightThemeFactory())
```

## Abstract Factory (TypeScript)

```ts
interface Button {
  render(): string;
}

interface Panel {
  render(): string;
}

class LightButton implements Button {
  render(): string {
    return "LightButton";
  }
}

class LightPanel implements Panel {
  render(): string {
    return "LightPanel";
  }
}

class DarkButton implements Button {
  render(): string {
    return "DarkButton";
  }
}

class DarkPanel implements Panel {
  render(): string {
    return "DarkPanel";
  }
}

interface ThemeFactory {
  createButton(): Button;
  createPanel(): Panel;
}

class LightThemeFactory implements ThemeFactory {
  createButton(): Button {
    return new LightButton();
  }

  createPanel(): Panel {
    return new LightPanel();
  }
}

class DarkThemeFactory implements ThemeFactory {
  createButton(): Button {
    return new DarkButton();
  }

  createPanel(): Panel {
    return new DarkPanel();
  }
}

function buildUI(factory: ThemeFactory): void {
  const button = factory.createButton();
  const panel = factory.createPanel();
  console.log(button.render(), panel.render());
}

buildUI(new LightThemeFactory());
```

---

## Runtime Variant Selection (initialization seam)

The concrete factory is selected once at startup; client code never touches concrete types.

```python
def select_theme(name: str) -> ThemeFactory:
    if name == "light":
        return LightThemeFactory()
    if name == "dark":
        return DarkThemeFactory()
    raise ValueError(f"unknown theme: {name}")


factory = select_theme("dark")
build_ui(factory)
```

```ts
function selectTheme(name: string): ThemeFactory {
  if (name === "light") return new LightThemeFactory();
  if (name === "dark") return new DarkThemeFactory();
  throw new Error("unknown theme");
}

const factory = selectTheme("dark");
buildUI(factory);
```
