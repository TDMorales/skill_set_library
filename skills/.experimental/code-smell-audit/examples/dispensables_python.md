# Dispensables – Python Examples

Before/after examples for each Dispensable smell. Each section shows the smell, then the refactored version.

---

## DS-1: Comments

### ❌ BROKEN (exhibits the smell)

Narrating comments restate the code instead of explaining intent.

~~~python
# Get the user from the database
user = db.get_user(user_id)

# Check if the user is active
if user.is_active:
    # Calculate the discount
    discount = user.loyalty_points * 0.01
    # Apply the discount to the total
    total = total - discount
~~~

### ✅ CORRECT (after Extract Method + Rename — code is self-documenting)

~~~python
user = db.get_user(user_id)
if user.is_active:
    total = apply_loyalty_discount(total, user.loyalty_points)


def apply_loyalty_discount(total: float, points: int) -> float:
    return total - points * 0.01
~~~

### ▶ EDGE CASE

Comments that explain *why* (business rules, workarounds, non-obvious constraints) or document public API contracts are valuable and should not be flagged.

---

## DS-2: Duplicate Code

### ❌ BROKEN (exhibits the smell)

~~~python
def activate_user(user):
    user.status = "active"
    user.updated_at = datetime.now()
    db.save(user)
    send_email(user.email, "Account Activated", "Your account is now active.")


def deactivate_user(user):
    user.status = "inactive"
    user.updated_at = datetime.now()
    db.save(user)
    send_email(user.email, "Account Deactivated", "Your account has been deactivated.")
~~~

### ✅ CORRECT (after Extract Method)

~~~python
def change_user_status(user, new_status: str, subject: str, message: str):
    user.status = new_status
    user.updated_at = datetime.now()
    db.save(user)
    send_email(user.email, subject, message)


def activate_user(user):
    change_user_status(user, "active", "Account Activated", "Your account is now active.")


def deactivate_user(user):
    change_user_status(user, "inactive", "Account Deactivated", "Your account has been deactivated.")
~~~

---

## DS-3: Lazy Class

### ❌ BROKEN (exhibits the smell)

~~~python
class StringWrapper:
    def __init__(self, value: str):
        self.value = value

    def get(self) -> str:
        return self.value
~~~

### ✅ CORRECT (after Inline Class — use the string directly)

~~~python
name: str = "Alice"
~~~

### ▶ EDGE CASE

A thin class may be justified if it serves as a type-safe marker (e.g., `UserId` vs. raw `str`) or is expected to grow with domain logic soon.

---

## DS-4: Data Class

### ❌ BROKEN (exhibits the smell)

A class with only fields and getters — behavior that operates on its data lives elsewhere.

~~~python
class Invoice:
    def __init__(self, items: list, tax_rate: float):
        self.items = items
        self.tax_rate = tax_rate


def calculate_total(invoice: Invoice) -> float:
    subtotal = sum(i.price for i in invoice.items)
    return subtotal + subtotal * invoice.tax_rate
~~~

### ✅ CORRECT (after Move Method into the class)

~~~python
class Invoice:
    def __init__(self, items: list, tax_rate: float):
        self.items = items
        self.tax_rate = tax_rate

    def total(self) -> float:
        subtotal = sum(i.price for i in self.items)
        return subtotal + subtotal * self.tax_rate
~~~

### ▶ EDGE CASE

Intentional DTOs, API request/response models, and configuration objects are legitimate data-only classes. Flag only when behavior that belongs with the data lives in a separate class.

---

## DS-5: Dead Code

### ❌ BROKEN (exhibits the smell)

~~~python
def process(data):
    result = transform(data)
    # old_result = legacy_transform(data)  # commented out months ago
    return result


def legacy_transform(data):
    """No call sites remain anywhere in the codebase."""
    ...
~~~

### ✅ CORRECT (after deletion)

~~~python
def process(data):
    return transform(data)
~~~

---

## DS-6: Speculative Generality

### ❌ BROKEN (exhibits the smell)

~~~python
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    @abstractmethod
    def process(self, data): ...

    @abstractmethod
    def validate(self, data): ...

    @abstractmethod
    def pre_hook(self, data): ...

    @abstractmethod
    def post_hook(self, data): ...


class CsvProcessor(DataProcessor):
    """The only implementation — pre_hook and post_hook are always no-ops."""

    def process(self, data):
        return parse_csv(data)

    def validate(self, data):
        return bool(data)

    def pre_hook(self, data):
        pass

    def post_hook(self, data):
        pass
~~~

### ✅ CORRECT (after Collapse Hierarchy + Remove Parameter)

~~~python
class CsvProcessor:
    def process(self, data):
        if not data:
            raise ValueError("empty data")
        return parse_csv(data)
~~~
