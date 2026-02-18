# Abstract Factory – Python Example

Minimal Abstract Factory example showing abstract product interfaces, concrete products grouped by variant, an abstract factory interface, and concrete factories that guarantee family coherence.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The client bypasses the factory and instantiates concrete products directly, mixing variants from different families.

~~~python
"""
What breaks
- Client depends on concrete product classes, not abstract interfaces
- No factory enforces family coherence — variants can be mixed
- Adding a new variant requires modifying client code (violates Open/Closed)
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/theme_ui.py
# +++ b/theme_ui.py
# @@
# - def build_ui(factory: ThemeFactory) -> None:
# -     button = factory.create_button()
# -     panel = factory.create_panel()
# + def build_ui() -> None:
# +     button = LightButton()
# +     panel = DarkPanel()
#   # ❌ BUG: client depends on concrete classes; families are mixed.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
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
~~~

---

## ▶ EXPLICIT EXAMPLE (RUNTIME SELECTION + ADDING A NEW VARIANT)

The concrete factory is selected at the initialization seam. Adding a new variant (HighContrast) requires only new classes — no changes to existing factories or client code.

~~~python
def select_theme(name: str) -> ThemeFactory:
    if name == "light":
        return LightThemeFactory()
    if name == "dark":
        return DarkThemeFactory()
    if name == "high-contrast":
        return HighContrastThemeFactory()
    raise ValueError(f"unknown theme: {name}")


class HighContrastButton(Button):
    def render(self) -> str:
        return "HighContrastButton"


class HighContrastPanel(Panel):
    def render(self) -> str:
        return "HighContrastPanel"


class HighContrastThemeFactory(ThemeFactory):
    def create_button(self) -> Button:
        return HighContrastButton()

    def create_panel(self) -> Panel:
        return HighContrastPanel()


factory = select_theme("high-contrast")
build_ui(factory)
~~~
