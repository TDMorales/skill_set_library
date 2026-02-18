# Abstract Factory – TypeScript Example

Minimal Abstract Factory example showing abstract product interfaces, concrete products grouped by variant, an abstract factory interface, and concrete factories that guarantee family coherence.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The client bypasses the factory and instantiates concrete products directly, mixing variants from different families.

~~~typescript
/**
 * What breaks
 * - Client depends on concrete product classes, not abstract interfaces
 * - No factory enforces family coherence — variants can be mixed
 * - Adding a new variant requires modifying client code (violates Open/Closed)
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/theme_ui.ts
// +++ b/theme_ui.ts
// @@
// - function buildUI(factory: ThemeFactory): void {
// -   const button = factory.createButton();
// -   const panel = factory.createPanel();
// + function buildUI(): void {
// +   const button = new LightButton();
// +   const panel = new DarkPanel();
//   // ❌ BUG: client depends on concrete classes; families are mixed.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
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
~~~

---

## ▶ EXPLICIT EXAMPLE (RUNTIME SELECTION + ADDING A NEW VARIANT)

The concrete factory is selected at the initialization seam. Adding a new variant (HighContrast) requires only new classes — no changes to existing factories or client code.

~~~typescript
function selectTheme(name: string): ThemeFactory {
  if (name === "light") return new LightThemeFactory();
  if (name === "dark") return new DarkThemeFactory();
  if (name === "high-contrast") return new HighContrastThemeFactory();
  throw new Error("unknown theme");
}

class HighContrastButton implements Button {
  render(): string {
    return "HighContrastButton";
  }
}

class HighContrastPanel implements Panel {
  render(): string {
    return "HighContrastPanel";
  }
}

class HighContrastThemeFactory implements ThemeFactory {
  createButton(): Button {
    return new HighContrastButton();
  }

  createPanel(): Panel {
    return new HighContrastPanel();
  }
}

const factory = selectTheme("high-contrast");
buildUI(factory);
~~~
