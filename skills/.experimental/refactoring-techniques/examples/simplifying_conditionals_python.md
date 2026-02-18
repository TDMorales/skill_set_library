# Simplifying Conditional Expressions – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## SC-1: Replace Conditional with Polymorphism

### ❌ BEFORE

A switch/if-else chain dispatches on a type string.

~~~python
class Bird:
    def __init__(self, bird_type: str, voltage: float = 0, coconuts: int = 0):
        self.type = bird_type
        self.voltage = voltage
        self.coconuts = coconuts


def speed(bird: Bird) -> float:
    if bird.type == "european":
        return 35
    elif bird.type == "african":
        return 40 - 12 * bird.coconuts
    elif bird.type == "norwegian_blue":
        return 0 if bird.voltage < 10 else 24
    raise ValueError(f"unknown bird: {bird.type}")
~~~

### ✅ AFTER (Replace Conditional with Polymorphism)

Mechanical steps:
1. Create a subclass for each branch of the conditional.
2. Move each branch's logic into the corresponding subclass's override.
3. Remove the conditional from the base.
4. Update creation sites to instantiate the correct subclass.

~~~python
from abc import ABC, abstractmethod


class Bird(ABC):
    @abstractmethod
    def speed(self) -> float: ...


class European(Bird):
    def speed(self) -> float:
        return 35


class African(Bird):
    def __init__(self, coconuts: int):
        self.coconuts = coconuts

    def speed(self) -> float:
        return 40 - 12 * self.coconuts


class NorwegianBlue(Bird):
    def __init__(self, voltage: float):
        self.voltage = voltage

    def speed(self) -> float:
        return 0 if self.voltage < 10 else 24
~~~

### ▶ EDGE CASE

If the conditional appears in only one place and new branches are unlikely, a simple if-else may be clearer than a class hierarchy. Apply this technique when the switch repeats across multiple methods or new cases are anticipated.
