# Moving Features between Objects – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## MF-1: Move Method

### ❌ BEFORE

`overdraftCharge` uses `Account`'s data but should live on `AccountType`.

~~~typescript
class AccountType {
  constructor(public isPremium: boolean) {}
}

class Account {
  constructor(public type: AccountType, public daysOverdrawn: number) {}

  overdraftCharge(): number {
    if (this.type.isPremium) {
      return this.daysOverdrawn > 7 ? 10 + (this.daysOverdrawn - 7) * 0.85 : 10;
    }
    return this.daysOverdrawn * 1.75;
  }
}
~~~

### ✅ AFTER

~~~typescript
class AccountType {
  constructor(public isPremium: boolean) {}

  overdraftCharge(daysOverdrawn: number): number {
    if (this.isPremium) {
      return daysOverdrawn > 7 ? 10 + (daysOverdrawn - 7) * 0.85 : 10;
    }
    return daysOverdrawn * 1.75;
  }
}

class Account {
  constructor(public type: AccountType, public daysOverdrawn: number) {}

  overdraftCharge(): number {
    return this.type.overdraftCharge(this.daysOverdrawn);
  }
}
~~~

---

## MF-2: Move Field

### ❌ BEFORE

`interestRate` belongs with `AccountType`, not `Account`.

~~~typescript
class Account {
  constructor(public interestRate: number, public type: AccountType) {}
}
~~~

### ✅ AFTER

~~~typescript
class AccountType {
  constructor(public isPremium: boolean, public interestRate: number) {}
}

class Account {
  constructor(public type: AccountType) {}

  get interestRate(): number {
    return this.type.interestRate;
  }
}
~~~

---

## MF-3: Extract Class

### ❌ BEFORE

~~~typescript
class Person {
  constructor(
    public name: string,
    public areaCode: string,
    public number: string
  ) {}

  phone(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
~~~

### ✅ AFTER

~~~typescript
class PhoneNumber {
  constructor(public areaCode: string, public number: string) {}

  toString(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}

class Person {
  constructor(public name: string, public phone: PhoneNumber) {}
}
~~~

---

## MF-4: Inline Class

### ❌ BEFORE

`PhoneNumber` does too little to justify its existence.

~~~typescript
class PhoneNumber {
  constructor(public number: string) {}
}

class Person {
  constructor(public name: string, private phone: PhoneNumber) {}

  get phoneNumber(): string {
    return this.phone.number;
  }
}
~~~

### ✅ AFTER

~~~typescript
class Person {
  constructor(public name: string, public phoneNumber: string) {}
}
~~~

---

## MF-5: Hide Delegate

### ❌ BEFORE

Client navigates through `person` to reach `department`.

~~~typescript
const manager = person.department.manager;
~~~

### ✅ AFTER

~~~typescript
class Person {
  get manager(): string {
    return this.department.manager;
  }
}

const manager = person.manager;
~~~

---

## MF-6: Remove Middle Man

### ❌ BEFORE

`Person` just delegates to `Department` for everything.

~~~typescript
class Person {
  constructor(private _department: Department) {}
  get manager() { return this._department.manager; }
  get budget() { return this._department.budget; }
  get headcount() { return this._department.headcount; }
}
~~~

### ✅ AFTER

~~~typescript
class Person {
  constructor(public department: Department) {}
}

const manager = person.department.manager;
~~~

---

## MF-7: Introduce Foreign Method / Local Extension

### ❌ BEFORE

Date arithmetic is scattered because the library lacks `nextBusinessDay`.

~~~typescript
let nextDay = new Date(start);
nextDay.setDate(nextDay.getDate() + 1);
while (nextDay.getDay() === 0 || nextDay.getDay() === 6) {
  nextDay.setDate(nextDay.getDate() + 1);
}
~~~

### ✅ AFTER (Foreign Method)

~~~typescript
function nextBusinessDay(start: Date): Date {
  const next = new Date(start);
  next.setDate(next.getDate() + 1);
  while (next.getDay() === 0 || next.getDay() === 6) {
    next.setDate(next.getDate() + 1);
  }
  return next;
}

const result = nextBusinessDay(start);
~~~

### ▶ EDGE CASE (Local Extension — when multiple methods are needed)

~~~typescript
class BusinessDate {
  constructor(private date: Date) {}

  nextBusinessDay(): BusinessDate {
    const next = new Date(this.date);
    next.setDate(next.getDate() + 1);
    while (next.getDay() === 0 || next.getDay() === 6) {
      next.setDate(next.getDate() + 1);
    }
    return new BusinessDate(next);
  }

  businessDaysUntil(end: Date): number {
    let count = 0;
    const current = new Date(this.date);
    while (current < end) {
      if (current.getDay() !== 0 && current.getDay() !== 6) count++;
      current.setDate(current.getDate() + 1);
    }
    return count;
  }
}
~~~
