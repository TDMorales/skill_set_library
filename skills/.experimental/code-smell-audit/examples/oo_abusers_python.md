# Object-Orientation Abusers – Python Examples

Before/after examples for each OO Abuser smell. Each section shows the smell, then the refactored version.

---

## OA-1: Switch Statements

### ❌ BROKEN (exhibits the smell)

~~~python
def calculate_area(shape: dict) -> float:
    if shape["type"] == "circle":
        return 3.14159 * shape["radius"] ** 2
    elif shape["type"] == "rectangle":
        return shape["width"] * shape["height"]
    elif shape["type"] == "triangle":
        return 0.5 * shape["base"] * shape["height"]
    else:
        raise ValueError(f"unknown shape: {shape['type']}")
~~~

### ✅ CORRECT (after Replace Conditional with Polymorphism)

~~~python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height
~~~

### ▶ EDGE CASE

A simple switch on 2–3 values that is unlikely to grow (e.g., parsing a CLI flag) may be clearer than a full class hierarchy. Apply polymorphism when the switch appears in multiple places or new cases are anticipated.

---

## OA-2: Temporary Field

### ❌ BROKEN (exhibits the smell)

~~~python
class ReportGenerator:
    def __init__(self):
        self._header = None
        self._data = None
        self._footer = None

    def generate_full(self, data):
        self._header = "FULL REPORT"
        self._data = data
        self._footer = "END"
        return self._render()

    def generate_summary(self, data):
        self._header = "SUMMARY"
        self._data = data
        # _footer is None here — only used in generate_full
        return self._render()

    def _render(self):
        parts = [self._header, str(self._data)]
        if self._footer:
            parts.append(self._footer)
        return "\n".join(parts)
~~~

### ✅ CORRECT (after Extract Class)

~~~python
class FullReport:
    def __init__(self, data):
        self.header = "FULL REPORT"
        self.data = data
        self.footer = "END"

    def render(self) -> str:
        return f"{self.header}\n{self.data}\n{self.footer}"


class SummaryReport:
    def __init__(self, data):
        self.header = "SUMMARY"
        self.data = data

    def render(self) -> str:
        return f"{self.header}\n{self.data}"
~~~

---

## OA-3: Refused Bequest

### ❌ BROKEN (exhibits the smell)

~~~python
class Animal:
    def walk(self) -> str:
        return "walking"

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "woof"


class Fish(Animal):
    def walk(self) -> str:
        raise NotImplementedError("fish can't walk")

    def speak(self) -> str:
        raise NotImplementedError("fish can't speak")
~~~

### ✅ CORRECT (after Extract Superclass / Replace Inheritance with Delegation)

~~~python
from abc import ABC, abstractmethod


class Animal(ABC):
    @abstractmethod
    def move(self) -> str: ...


class Dog(Animal):
    def move(self) -> str:
        return "walking"

    def speak(self) -> str:
        return "woof"


class Fish(Animal):
    def move(self) -> str:
        return "swimming"
~~~

---

## OA-4: Alternative Classes with Different Interfaces

### ❌ BROKEN (exhibits the smell)

~~~python
class PdfRenderer:
    def render_pdf(self, content: str) -> bytes:
        ...

class HtmlRenderer:
    def to_html(self, content: str) -> str:
        ...
~~~

### ✅ CORRECT (after Rename Method + Extract Superclass)

~~~python
from abc import ABC, abstractmethod


class Renderer(ABC):
    @abstractmethod
    def render(self, content: str) -> str | bytes: ...


class PdfRenderer(Renderer):
    def render(self, content: str) -> bytes:
        ...

class HtmlRenderer(Renderer):
    def render(self, content: str) -> str:
        ...
~~~
