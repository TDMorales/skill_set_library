# Organizing Data – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## OD-1: Replace Data Value with Object

### ❌ BEFORE

A raw string carries domain meaning with validation scattered at call sites.

~~~typescript
function createOrder(customerName: string, phone: string): void {
  if (!phone || phone.length < 10) throw new Error("bad phone");
  // ...
}
~~~

### ✅ AFTER

~~~typescript
class PhoneNumber {
  readonly value: string;
  constructor(raw: string) {
    if (!raw || raw.length < 10) throw new Error(`invalid phone: ${raw}`);
    this.value = raw;
  }
}

function createOrder(customerName: string, phone: PhoneNumber): void {
  // ...
}
~~~

---

## OD-2: Encapsulate Field / Collection

### ❌ BEFORE

Fields and collections are directly exposed; external code mutates them freely.

~~~typescript
class Course {
  students: string[] = [];
}

const course = new Course();
course.students.push("Alice");
course.students.splice(0, 1);
~~~

### ✅ AFTER

~~~typescript
class Course {
  private _students: string[] = [];

  get students(): ReadonlyArray<string> {
    return [...this._students];
  }

  enroll(name: string): void {
    if (!this._students.includes(name)) {
      this._students.push(name);
    }
  }

  drop(name: string): void {
    const idx = this._students.indexOf(name);
    if (idx >= 0) this._students.splice(idx, 1);
  }
}

const course = new Course();
course.enroll("Alice");
~~~

---

## OD-3: Replace Type Code with Subclasses / State-Strategy

### ❌ BEFORE

A type code drives conditional logic.

~~~typescript
class Employee {
  constructor(public name: string, public type: string) {}

  bonus(): number {
    switch (this.type) {
      case "engineer": return 5000;
      case "manager": return 10000;
      case "sales": return 7000;
      default: throw new Error(`unknown type: ${this.type}`);
    }
  }
}
~~~

### ✅ AFTER (Subclasses)

~~~typescript
abstract class Employee {
  constructor(public name: string) {}
  abstract bonus(): number;
}

class Engineer extends Employee {
  bonus(): number { return 5000; }
}

class Manager extends Employee {
  bonus(): number { return 10000; }
}

class Sales extends Employee {
  bonus(): number { return 7000; }
}
~~~

### ▶ EDGE CASE (State-Strategy — when type can change at runtime)

~~~typescript
interface EmployeeType {
  bonus(): number;
}

class EngineerType implements EmployeeType {
  bonus(): number { return 5000; }
}

class ManagerType implements EmployeeType {
  bonus(): number { return 10000; }
}

class Employee {
  constructor(public name: string, public type: EmployeeType) {}

  bonus(): number {
    return this.type.bonus();
  }
}
~~~
