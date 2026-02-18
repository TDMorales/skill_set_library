# Dealing with Generalization – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## DG-1: Extract Superclass / Extract Interface

### ❌ BEFORE

Two classes share common behavior but have no shared abstraction.

~~~python
class Employee:
    def __init__(self, name: str, annual_cost: float):
        self.name = name
        self.annual_cost = annual_cost

    def monthly_cost(self) -> float:
        return self.annual_cost / 12


class Department:
    def __init__(self, name: str, staff: list):
        self.name = name
        self.staff = staff

    @property
    def annual_cost(self) -> float:
        return sum(e.annual_cost for e in self.staff)

    def monthly_cost(self) -> float:
        return self.annual_cost / 12
~~~

### ✅ AFTER (Extract Superclass)

Mechanical steps:
1. Create a superclass with the shared members.
2. Pull up common fields and methods.
3. Have both classes inherit from the superclass.

~~~python
from abc import ABC, abstractmethod


class CostCenter(ABC):
    @property
    @abstractmethod
    def annual_cost(self) -> float: ...

    def monthly_cost(self) -> float:
        return self.annual_cost / 12


class Employee(CostCenter):
    def __init__(self, name: str, cost: float):
        self.name = name
        self._annual_cost = cost

    @property
    def annual_cost(self) -> float:
        return self._annual_cost


class Department(CostCenter):
    def __init__(self, name: str, staff: list[Employee]):
        self.name = name
        self.staff = staff

    @property
    def annual_cost(self) -> float:
        return sum(e.annual_cost for e in self.staff)
~~~

---

## DG-2: Collapse Hierarchy

### ❌ BEFORE

A subclass adds no meaningful behavior beyond the superclass.

~~~python
class Employee:
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary

    def monthly_pay(self) -> float:
        return self.salary / 12


class Salesperson(Employee):
    pass
~~~

### ✅ AFTER

Mechanical steps:
1. Move any unique members from the subclass into the superclass (none here).
2. Update all references from the subclass to the superclass.
3. Remove the subclass.

~~~python
class Employee:
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary

    def monthly_pay(self) -> float:
        return self.salary / 12


emp = Employee("Alice", 72000)
~~~

---

## DG-3: Replace Inheritance with Delegation

### ❌ BEFORE

`Stack` inherits from `list` but only wants `push`/`pop`, not the full list API.

~~~python
class Stack(list):
    def push(self, item):
        self.append(item)
~~~

### ✅ AFTER

Mechanical steps:
1. Create a field of the former superclass's type.
2. Create forwarding methods for the operations the subclass actually uses.
3. Remove the inheritance relationship.

~~~python
class Stack:
    def __init__(self):
        self._items: list = []

    def push(self, item) -> None:
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0
~~~

### ▶ EDGE CASE

If the subclass genuinely needs the full superclass API and IS-A semantics hold, inheritance is appropriate. Replace only when the subclass uses a small fraction of the superclass interface or when IS-A is misleading (a Stack is not a List).
