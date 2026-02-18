# Change Preventers – TypeScript Examples

Before/after examples for each Change Preventer smell. Each section shows the smell, then the refactored version.

---

## CP-1: Divergent Change

### ❌ BROKEN (exhibits the smell)

A single class is modified for unrelated reasons — database changes AND notification changes AND report changes all touch `OrderService`.

~~~typescript
class OrderService {
  saveOrder(order: Order): void {
    const db = connectDb();
    db.execute("INSERT INTO orders ...", order.toDict());
  }

  notifyCustomer(order: Order): void {
    const body = `Order ${order.id} confirmed`;
    sendEmail(order.customer.email, "Confirmation", body);
  }

  generateMonthlyReport(): string {
    const rows = connectDb().execute("SELECT * FROM orders WHERE ...");
    return formatCsv(rows);
  }
}
~~~

### ✅ CORRECT (after Extract Class — one class per axis of change)

~~~typescript
class OrderRepository {
  save(order: Order): void {
    const db = connectDb();
    db.execute("INSERT INTO orders ...", order.toDict());
  }
}

class OrderNotifier {
  notifyCustomer(order: Order): void {
    const body = `Order ${order.id} confirmed`;
    sendEmail(order.customer.email, "Confirmation", body);
  }
}

class OrderReporter {
  generateMonthlyReport(): string {
    const rows = connectDb().execute("SELECT * FROM orders WHERE ...");
    return formatCsv(rows);
  }
}
~~~

---

## CP-2: Shotgun Surgery

### ❌ BROKEN (exhibits the smell)

Changing the logging format requires edits in every file that logs.

~~~typescript
// file: auth.ts
function login(user: string, password: string): void {
  console.log(`[INFO] ${new Date().toISOString()} auth.login called`);
  // ...
}

// file: orders.ts
function placeOrder(order: Order): void {
  console.log(`[INFO] ${new Date().toISOString()} orders.placeOrder called`);
  // ...
}

// file: payments.ts
function charge(card: string, amount: number): void {
  console.log(`[INFO] ${new Date().toISOString()} payments.charge called`);
  // ...
}
~~~

### ✅ CORRECT (after Move Method — consolidate into one module)

~~~typescript
// file: logger.ts
export function logCall(name: string): void {
  console.log(`[INFO] ${new Date().toISOString()} ${name} called`);
}

// file: auth.ts
import { logCall } from "./logger";

function login(user: string, password: string): void {
  logCall("auth.login");
  // ...
}

// file: orders.ts
import { logCall } from "./logger";

function placeOrder(order: Order): void {
  logCall("orders.placeOrder");
  // ...
}

// file: payments.ts
import { logCall } from "./logger";

function charge(card: string, amount: number): void {
  logCall("payments.charge");
  // ...
}
~~~

---

## CP-3: Parallel Inheritance Hierarchies

### ❌ BROKEN (exhibits the smell)

Every new `Shape` subclass requires a matching `ShapeSerializer` subclass.

~~~typescript
class Shape {}
class Circle extends Shape {}
class Rectangle extends Shape {}

class ShapeSerializer {}
class CircleSerializer extends ShapeSerializer {}
class RectangleSerializer extends ShapeSerializer {}
~~~

### ✅ CORRECT (after Move Method — collapse one hierarchy into the other)

~~~typescript
interface Shape {
  serialize(): Record<string, unknown>;
}

class Circle implements Shape {
  constructor(private radius: number) {}
  serialize(): Record<string, unknown> {
    return { type: "circle", radius: this.radius };
  }
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  serialize(): Record<string, unknown> {
    return { type: "rectangle", width: this.width, height: this.height };
  }
}
~~~

### ▶ EDGE CASE

Keeping separate hierarchies is justified when serialization logic is complex enough to warrant its own tests and the serialization format changes independently from shape behavior (e.g., supporting multiple wire formats).
