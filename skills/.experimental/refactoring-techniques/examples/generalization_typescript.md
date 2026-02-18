# Dealing with Generalization – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## DG-1: Extract Superclass / Extract Interface

### ❌ BEFORE

Two classes share common behavior but have no shared abstraction.

~~~typescript
class Employee {
  constructor(public name: string, public annualCost: number) {}

  monthlyCost(): number {
    return this.annualCost / 12;
  }
}

class Department {
  constructor(public name: string, public staff: Employee[]) {}

  get annualCost(): number {
    return this.staff.reduce((sum, e) => sum + e.annualCost, 0);
  }

  monthlyCost(): number {
    return this.annualCost / 12;
  }
}
~~~

### ✅ AFTER (Extract Interface)

Mechanical steps:
1. Create an interface with the shared members.
2. Pull up common method signatures.
3. Have both classes implement the interface.

~~~typescript
interface CostCenter {
  readonly annualCost: number;
  monthlyCost(): number;
}

class Employee implements CostCenter {
  constructor(public name: string, public annualCost: number) {}

  monthlyCost(): number {
    return this.annualCost / 12;
  }
}

class Department implements CostCenter {
  constructor(public name: string, public staff: Employee[]) {}

  get annualCost(): number {
    return this.staff.reduce((sum, e) => sum + e.annualCost, 0);
  }

  monthlyCost(): number {
    return this.annualCost / 12;
  }
}
~~~

---

## DG-2: Collapse Hierarchy

### ❌ BEFORE

A subclass adds no meaningful behavior beyond the superclass.

~~~typescript
class Employee {
  constructor(public name: string, public salary: number) {}

  monthlyPay(): number {
    return this.salary / 12;
  }
}

class Salesperson extends Employee {}
~~~

### ✅ AFTER

Mechanical steps:
1. Move any unique members from the subclass into the superclass (none here).
2. Update all references from the subclass to the superclass.
3. Remove the subclass.

~~~typescript
class Employee {
  constructor(public name: string, public salary: number) {}

  monthlyPay(): number {
    return this.salary / 12;
  }
}

const emp = new Employee("Alice", 72000);
~~~

---

## DG-3: Replace Inheritance with Delegation

### ❌ BEFORE

`Stack` extends `Array` but only wants `push`/`pop`, not the full Array API.

~~~typescript
class Stack<T> extends Array<T> {
  peek(): T | undefined {
    return this[this.length - 1];
  }
}
~~~

### ✅ AFTER

Mechanical steps:
1. Create a field of the former superclass's type.
2. Create forwarding methods for the operations the subclass actually uses.
3. Remove the inheritance relationship.

~~~typescript
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  get isEmpty(): boolean {
    return this.items.length === 0;
  }
}
~~~

### ▶ EDGE CASE

If the subclass genuinely needs the full superclass API and IS-A semantics hold, inheritance is appropriate. Replace only when the subclass uses a small fraction of the superclass interface or when IS-A is misleading (a Stack is not an Array).
