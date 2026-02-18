# Bloaters – TypeScript Examples

Before/after examples for each Bloater smell. Each section shows the smell, then the refactored version.

---

## BL-1: Long Method

### ❌ BROKEN (exhibits the smell)

~~~typescript
function processOrder(order: Order): number {
  if (!order.items.length) throw new Error("empty order");
  if (!order.customer) throw new Error("no customer");
  let subtotal = 0;
  for (const item of order.items) {
    subtotal += item.price * item.quantity;
  }
  const tax = subtotal * 0.08;
  let total = subtotal + tax;
  if (order.customer.isPremium) {
    total *= 0.9;
  }
  let invoice = `Invoice for ${order.customer.name}\n`;
  for (const item of order.items) {
    invoice += `  ${item.name}: $${(item.price * item.quantity).toFixed(2)}\n`;
  }
  invoice += `Total: $${total.toFixed(2)}`;
  sendEmail(order.customer.email, "Order Confirmed", invoice);
  return total;
}
~~~

### ✅ CORRECT (after Extract Method)

~~~typescript
function processOrder(order: Order): number {
  validateOrder(order);
  const total = calculateTotal(order);
  const invoice = generateInvoice(order, total);
  sendConfirmation(order.customer, invoice);
  return total;
}

function validateOrder(order: Order): void {
  if (!order.items.length) throw new Error("empty order");
  if (!order.customer) throw new Error("no customer");
}

function calculateTotal(order: Order): number {
  const subtotal = order.items.reduce((s, i) => s + i.price * i.quantity, 0);
  const tax = subtotal * 0.08;
  let total = subtotal + tax;
  if (order.customer.isPremium) total *= 0.9;
  return total;
}

function generateInvoice(order: Order, total: number): string {
  const lines = [`Invoice for ${order.customer.name}`];
  for (const item of order.items) {
    lines.push(`  ${item.name}: $${(item.price * item.quantity).toFixed(2)}`);
  }
  lines.push(`Total: $${total.toFixed(2)}`);
  return lines.join("\n");
}

function sendConfirmation(customer: Customer, invoice: string): void {
  sendEmail(customer.email, "Order Confirmed", invoice);
}
~~~

### ▶ EDGE CASE

Sequential setup code (e.g., test fixtures or CLI argument parsing) may be acceptably long if each line is simple and extraction would obscure the flow.

---

## BL-2: Large Class

### ❌ BROKEN (exhibits the smell)

~~~typescript
class UserManager {
  createUser(name: string, email: string): void { /* ... */ }
  deleteUser(userId: string): void { /* ... */ }
  updateProfile(userId: string, data: object): void { /* ... */ }
  authenticate(email: string, password: string): boolean { /* ... */ }
  resetPassword(email: string): void { /* ... */ }
  sendWelcomeEmail(user: User): void { /* ... */ }
  sendPasswordResetEmail(user: User): void { /* ... */ }
  generateReport(userId: string): Report { /* ... */ }
  exportToCsv(userId: string): string { /* ... */ }
}
~~~

### ✅ CORRECT (after Extract Class)

~~~typescript
class UserRepository {
  create(name: string, email: string): void { /* ... */ }
  delete(userId: string): void { /* ... */ }
  updateProfile(userId: string, data: object): void { /* ... */ }
}

class AuthService {
  authenticate(email: string, password: string): boolean { /* ... */ }
  resetPassword(email: string): void { /* ... */ }
}

class UserNotifier {
  sendWelcomeEmail(user: User): void { /* ... */ }
  sendPasswordResetEmail(user: User): void { /* ... */ }
}

class UserReportExporter {
  generateReport(userId: string): Report { /* ... */ }
  exportToCsv(userId: string): string { /* ... */ }
}
~~~

---

## BL-3: Primitive Obsession

### ❌ BROKEN (exhibits the smell)

~~~typescript
function createInvoice(
  amount: number,
  currency: string,
  zipCode: string,
  phone: string
): void {
  if (!["USD", "EUR", "GBP"].includes(currency)) throw new Error("bad currency");
  if (!/^\d{5}$/.test(zipCode)) throw new Error("bad zip");
  // ...
}
~~~

### ✅ CORRECT (after Replace Data Value with Object)

~~~typescript
class Money {
  constructor(
    readonly amount: number,
    readonly currency: "USD" | "EUR" | "GBP"
  ) {}
}

class ZipCode {
  readonly value: string;
  constructor(raw: string) {
    if (!/^\d{5}$/.test(raw)) throw new Error(`invalid zip: ${raw}`);
    this.value = raw;
  }
}

function createInvoice(price: Money, zipCode: ZipCode, phone: string): void {
  // ...
}
~~~

### ▶ EDGE CASE

Not every string or number needs a wrapper. Reserve value objects for domain concepts with validation rules or formatting logic that would otherwise be duplicated.

---

## BL-4: Long Parameter List

### ❌ BROKEN (exhibits the smell)

~~~typescript
function scheduleMeeting(
  title: string,
  start: Date,
  end: Date,
  room: string,
  organizer: string,
  attendees: string[],
  recurrence: string | null,
  reminderMinutes: number
): void {
  // ...
}
~~~

### ✅ CORRECT (after Introduce Parameter Object)

~~~typescript
type MeetingRequest = {
  title: string;
  start: Date;
  end: Date;
  room: string;
  organizer: string;
  attendees: string[];
  recurrence?: string;
  reminderMinutes?: number;
};

function scheduleMeeting(request: MeetingRequest): void {
  // ...
}
~~~

---

## BL-5: Data Clumps

### ❌ BROKEN (exhibits the smell)

~~~typescript
function geocode(street: string, city: string, state: string, zip: string): LatLng { /* ... */ }
function validateAddress(street: string, city: string, state: string, zip: string): boolean { /* ... */ }
function formatLabel(street: string, city: string, state: string, zip: string): string { /* ... */ }
~~~

### ✅ CORRECT (after Extract Class)

~~~typescript
type Address = {
  street: string;
  city: string;
  state: string;
  zip: string;
};

function geocode(address: Address): LatLng { /* ... */ }
function validateAddress(address: Address): boolean { /* ... */ }
function formatLabel(address: Address): string { /* ... */ }
~~~
