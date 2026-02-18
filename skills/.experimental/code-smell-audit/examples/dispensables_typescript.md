# Dispensables – TypeScript Examples

Before/after examples for each Dispensable smell. Each section shows the smell, then the refactored version.

---

## DS-1: Comments

### ❌ BROKEN (exhibits the smell)

Narrating comments restate the code instead of explaining intent.

~~~typescript
// Get the user from the database
const user = db.getUser(userId);

// Check if the user is active
if (user.isActive) {
  // Calculate the discount
  const discount = user.loyaltyPoints * 0.01;
  // Apply the discount to the total
  total = total - discount;
}
~~~

### ✅ CORRECT (after Extract Method + Rename — code is self-documenting)

~~~typescript
const user = db.getUser(userId);
if (user.isActive) {
  total = applyLoyaltyDiscount(total, user.loyaltyPoints);
}

function applyLoyaltyDiscount(total: number, points: number): number {
  return total - points * 0.01;
}
~~~

### ▶ EDGE CASE

Comments that explain *why* (business rules, workarounds, non-obvious constraints) or document public API contracts are valuable and should not be flagged.

---

## DS-2: Duplicate Code

### ❌ BROKEN (exhibits the smell)

~~~typescript
function activateUser(user: User): void {
  user.status = "active";
  user.updatedAt = new Date();
  db.save(user);
  sendEmail(user.email, "Account Activated", "Your account is now active.");
}

function deactivateUser(user: User): void {
  user.status = "inactive";
  user.updatedAt = new Date();
  db.save(user);
  sendEmail(user.email, "Account Deactivated", "Your account has been deactivated.");
}
~~~

### ✅ CORRECT (after Extract Method)

~~~typescript
function changeUserStatus(user: User, status: string, subject: string, message: string): void {
  user.status = status;
  user.updatedAt = new Date();
  db.save(user);
  sendEmail(user.email, subject, message);
}

function activateUser(user: User): void {
  changeUserStatus(user, "active", "Account Activated", "Your account is now active.");
}

function deactivateUser(user: User): void {
  changeUserStatus(user, "inactive", "Account Deactivated", "Your account has been deactivated.");
}
~~~

---

## DS-3: Lazy Class

### ❌ BROKEN (exhibits the smell)

~~~typescript
class StringWrapper {
  constructor(private value: string) {}
  get(): string {
    return this.value;
  }
}
~~~

### ✅ CORRECT (after Inline Class — use the string directly)

~~~typescript
const name: string = "Alice";
~~~

### ▶ EDGE CASE

A thin class may be justified if it serves as a type-safe marker (e.g., branded types in TypeScript) or is expected to grow with domain logic soon.

---

## DS-4: Data Class

### ❌ BROKEN (exhibits the smell)

A class with only fields — behavior that operates on its data lives elsewhere.

~~~typescript
class Invoice {
  constructor(public items: Item[], public taxRate: number) {}
}

function calculateTotal(invoice: Invoice): number {
  const subtotal = invoice.items.reduce((s, i) => s + i.price, 0);
  return subtotal + subtotal * invoice.taxRate;
}
~~~

### ✅ CORRECT (after Move Method into the class)

~~~typescript
class Invoice {
  constructor(public items: Item[], public taxRate: number) {}

  total(): number {
    const subtotal = this.items.reduce((s, i) => s + i.price, 0);
    return subtotal + subtotal * this.taxRate;
  }
}
~~~

### ▶ EDGE CASE

Intentional DTOs, API request/response models, and configuration objects are legitimate data-only classes. Flag only when behavior that belongs with the data lives in a separate class.

---

## DS-5: Dead Code

### ❌ BROKEN (exhibits the smell)

~~~typescript
function process(data: string): string {
  const result = transform(data);
  // const oldResult = legacyTransform(data); // commented out months ago
  return result;
}

function legacyTransform(data: string): string {
  // No call sites remain anywhere in the codebase.
  return data;
}
~~~

### ✅ CORRECT (after deletion)

~~~typescript
function process(data: string): string {
  return transform(data);
}
~~~

---

## DS-6: Speculative Generality

### ❌ BROKEN (exhibits the smell)

~~~typescript
interface DataProcessor {
  process(data: string): string;
  validate(data: string): boolean;
  preHook(data: string): void;
  postHook(data: string): void;
}

class CsvProcessor implements DataProcessor {
  process(data: string): string { return parseCsv(data); }
  validate(data: string): boolean { return !!data; }
  preHook(_data: string): void { /* no-op */ }
  postHook(_data: string): void { /* no-op */ }
}
~~~

### ✅ CORRECT (after Collapse Hierarchy + Remove Parameter)

~~~typescript
class CsvProcessor {
  process(data: string): string {
    if (!data) throw new Error("empty data");
    return parseCsv(data);
  }
}
~~~
