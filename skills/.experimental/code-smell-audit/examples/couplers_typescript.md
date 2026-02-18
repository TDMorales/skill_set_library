# Couplers – TypeScript Examples

Before/after examples for each Coupler smell. Each section shows the smell, then the refactored version.

---

## CL-1: Feature Envy

### ❌ BROKEN (exhibits the smell)

`formatAddress` reaches into `customer` for every field — it belongs on `Customer` or an `Address` class.

~~~typescript
function formatAddress(customer: Customer): string {
  return `${customer.street}\n${customer.city}, ${customer.state} ${customer.zipCode}\n${customer.country}`;
}
~~~

### ✅ CORRECT (after Move Method)

~~~typescript
class Customer {
  constructor(
    public street: string,
    public city: string,
    public state: string,
    public zipCode: string,
    public country: string
  ) {}

  formatAddress(): string {
    return `${this.street}\n${this.city}, ${this.state} ${this.zipCode}\n${this.country}`;
  }
}
~~~

### ▶ EDGE CASE

Utility functions that format/transform data from a single object are not always Feature Envy — if the formatting concern is deliberately separated (e.g., a view layer formatting a model), keeping it external is valid.

---

## CL-2: Inappropriate Intimacy

### ❌ BROKEN (exhibits the smell)

`Order` reaches into `Inventory`'s internal map, and `Inventory` reads `Order`'s private items.

~~~typescript
class Order {
  _items: Item[] = [];

  checkStock(inventory: Inventory): void {
    for (const item of this._items) {
      if ((inventory._stock.get(item.sku) ?? 0) < item.qty) {
        throw new Error(`${item.sku} out of stock`);
      }
    }
  }
}

class Inventory {
  _stock = new Map<string, number>();

  reserveFor(order: Order): void {
    for (const item of order._items) {
      this._stock.set(item.sku, (this._stock.get(item.sku) ?? 0) - item.qty);
    }
  }
}
~~~

### ✅ CORRECT (after Hide Delegate + clean interfaces)

~~~typescript
class Order {
  private _items: Item[] = [];

  get items(): ReadonlyArray<Item> {
    return this._items;
  }
}

class Inventory {
  private stock = new Map<string, number>();

  hasStock(sku: string, qty: number): boolean {
    return (this.stock.get(sku) ?? 0) >= qty;
  }

  reserve(sku: string, qty: number): void {
    if (!this.hasStock(sku, qty)) throw new Error(`${sku} out of stock`);
    this.stock.set(sku, (this.stock.get(sku) ?? 0) - qty);
  }
}

function fulfill(order: Order, inventory: Inventory): void {
  for (const item of order.items) {
    inventory.reserve(item.sku, item.qty);
  }
}
~~~

---

## CL-3: Message Chains

### ❌ BROKEN (exhibits the smell)

~~~typescript
const city = order.customer.address.city;
~~~

### ✅ CORRECT (after Hide Delegate)

~~~typescript
class Order {
  get shippingCity(): string {
    return this.customer.address.city;
  }
}

const city = order.shippingCity;
~~~

### ▶ EDGE CASE

Short chains (one or two dots) accessing well-known, stable structures (e.g., `req.user.id`) are idiomatic in many frameworks. Flag only chains of 3+ or chains into unstable internals.

---

## CL-4: Middle Man

### ❌ BROKEN (exhibits the smell)

`TeamLead` delegates everything to `Developer` with no added logic.

~~~typescript
class Developer {
  writeCode(): string { return "code written"; }
  fixBug(bugId: number): string { return `bug ${bugId} fixed`; }
}

class TeamLead {
  constructor(private dev: Developer) {}
  writeCode(): string { return this.dev.writeCode(); }
  fixBug(bugId: number): string { return this.dev.fixBug(bugId); }
}
~~~

### ✅ CORRECT (after Remove Middle Man — use Developer directly)

~~~typescript
class Developer {
  writeCode(): string { return "code written"; }
  fixBug(bugId: number): string { return `bug ${bugId} fixed`; }
}

const dev = new Developer();
dev.writeCode();
~~~

### ▶ EDGE CASE

A delegating class is justified when it adds access control, logging, caching, or API-stability guarantees. Flag only when delegation is pure pass-through with no added value.

---

## CL-5: Incomplete Library Class

### ❌ BROKEN (exhibits the smell)

The date library lacks a `businessDaysBetween` method, so the logic is scattered across call sites.

~~~typescript
function daysUntilDeadline(start: Date, end: Date): number {
  let count = 0;
  const current = new Date(start);
  while (current < end) {
    if (current.getDay() !== 0 && current.getDay() !== 6) count++;
    current.setDate(current.getDate() + 1);
  }
  return count;
}
~~~

### ✅ CORRECT (after Introduce Local Extension — wrapper or helper module)

~~~typescript
class BusinessCalendar {
  static businessDaysBetween(start: Date, end: Date): number {
    let count = 0;
    const current = new Date(start);
    while (current < end) {
      if (current.getDay() !== 0 && current.getDay() !== 6) count++;
      current.setDate(current.getDate() + 1);
    }
    return count;
  }
}

const days = BusinessCalendar.businessDaysBetween(start, end);
~~~
