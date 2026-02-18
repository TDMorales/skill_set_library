# Organizing Data – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## OD-1: Replace Data Value with Object

### ❌ BEFORE

A raw string carries domain meaning with validation scattered at call sites.

~~~python
def create_order(customer_name: str, phone: str):
    if not phone or len(phone) < 10:
        raise ValueError("bad phone")
    ...
~~~

### ✅ AFTER

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 10:
            raise ValueError(f"invalid phone: {self.value}")


def create_order(customer_name: str, phone: PhoneNumber):
    ...
~~~

---

## OD-2: Encapsulate Field / Collection

### ❌ BEFORE

Fields and collections are directly exposed; external code mutates them freely.

~~~python
class Course:
    def __init__(self):
        self.students: list[str] = []


course = Course()
course.students.append("Alice")
course.students.remove("Bob")
~~~

### ✅ AFTER

~~~python
class Course:
    def __init__(self):
        self._students: list[str] = []

    @property
    def students(self) -> tuple[str, ...]:
        return tuple(self._students)

    def enroll(self, name: str) -> None:
        if name not in self._students:
            self._students.append(name)

    def drop(self, name: str) -> None:
        self._students.remove(name)


course = Course()
course.enroll("Alice")
~~~

---

## OD-3: Replace Type Code with Subclasses / State-Strategy

### ❌ BEFORE

A type code drives conditional logic.

~~~python
class Employee:
    def __init__(self, name: str, emp_type: str):
        self.name = name
        self.type = emp_type

    def bonus(self) -> float:
        if self.type == "engineer":
            return 5000
        elif self.type == "manager":
            return 10000
        elif self.type == "sales":
            return 7000
        raise ValueError(f"unknown type: {self.type}")
~~~

### ✅ AFTER (Subclasses)

~~~python
from abc import ABC, abstractmethod


class Employee(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def bonus(self) -> float: ...


class Engineer(Employee):
    def bonus(self) -> float:
        return 5000


class Manager(Employee):
    def bonus(self) -> float:
        return 10000


class Sales(Employee):
    def bonus(self) -> float:
        return 7000
~~~

### ▶ EDGE CASE (State-Strategy — when type can change at runtime)

~~~python
from abc import ABC, abstractmethod


class EmployeeType(ABC):
    @abstractmethod
    def bonus(self) -> float: ...


class EngineerType(EmployeeType):
    def bonus(self) -> float:
        return 5000


class ManagerType(EmployeeType):
    def bonus(self) -> float:
        return 10000


class Employee:
    def __init__(self, name: str, emp_type: EmployeeType):
        self.name = name
        self.type = emp_type

    def bonus(self) -> float:
        return self.type.bonus()
~~~
