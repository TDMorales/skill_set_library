# Couplers – Python Examples

Before/after examples for each Coupler smell. Each section shows the smell, then the refactored version.

---

## CL-1: Feature Envy

### ❌ BROKEN (exhibits the smell)

`format_address` reaches into `customer` for every field — it belongs on `Customer` or an `Address` class.

~~~python
def format_address(customer) -> str:
    return (
        f"{customer.street}\n"
        f"{customer.city}, {customer.state} {customer.zip_code}\n"
        f"{customer.country}"
    )
~~~

### ✅ CORRECT (after Move Method)

~~~python
class Customer:
    def __init__(self, street, city, state, zip_code, country):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def format_address(self) -> str:
        return (
            f"{self.street}\n"
            f"{self.city}, {self.state} {self.zip_code}\n"
            f"{self.country}"
        )
~~~

### ▶ EDGE CASE

Utility functions that format/transform data from a single object are not always Feature Envy — if the formatting concern is deliberately separated (e.g., a view layer formatting a model), keeping it external is valid.

---

## CL-2: Inappropriate Intimacy

### ❌ BROKEN (exhibits the smell)

`Order` reaches into `Inventory`'s internal dict, and `Inventory` reads `Order`'s private items.

~~~python
class Order:
    def __init__(self):
        self._items = []

    def check_stock(self, inventory):
        for item in self._items:
            if inventory._stock.get(item.sku, 0) < item.qty:
                raise ValueError(f"{item.sku} out of stock")


class Inventory:
    def __init__(self):
        self._stock = {}

    def reserve_for(self, order):
        for item in order._items:
            self._stock[item.sku] -= item.qty
~~~

### ✅ CORRECT (after Hide Delegate + clean interfaces)

~~~python
class Order:
    def __init__(self):
        self._items = []

    @property
    def items(self):
        return list(self._items)


class Inventory:
    def __init__(self):
        self._stock = {}

    def has_stock(self, sku: str, qty: int) -> bool:
        return self._stock.get(sku, 0) >= qty

    def reserve(self, sku: str, qty: int) -> None:
        if not self.has_stock(sku, qty):
            raise ValueError(f"{sku} out of stock")
        self._stock[sku] -= qty


def fulfill(order: Order, inventory: Inventory) -> None:
    for item in order.items:
        inventory.reserve(item.sku, item.qty)
~~~

---

## CL-3: Message Chains

### ❌ BROKEN (exhibits the smell)

~~~python
city = order.customer.address.city
~~~

### ✅ CORRECT (after Hide Delegate)

~~~python
class Order:
    @property
    def shipping_city(self) -> str:
        return self.customer.address.city


city = order.shipping_city
~~~

### ▶ EDGE CASE

Short chains (one or two dots) accessing well-known, stable structures (e.g., `request.user.id`) are idiomatic in many frameworks. Flag only chains of 3+ or chains into unstable internals.

---

## CL-4: Middle Man

### ❌ BROKEN (exhibits the smell)

`TeamLead` delegates everything to `Developer` with no added logic.

~~~python
class Developer:
    def write_code(self) -> str:
        return "code written"

    def fix_bug(self, bug_id: int) -> str:
        return f"bug {bug_id} fixed"


class TeamLead:
    def __init__(self, dev: Developer):
        self._dev = dev

    def write_code(self) -> str:
        return self._dev.write_code()

    def fix_bug(self, bug_id: int) -> str:
        return self._dev.fix_bug(bug_id)
~~~

### ✅ CORRECT (after Remove Middle Man — use Developer directly)

~~~python
class Developer:
    def write_code(self) -> str:
        return "code written"

    def fix_bug(self, bug_id: int) -> str:
        return f"bug {bug_id} fixed"


dev = Developer()
dev.write_code()
~~~

### ▶ EDGE CASE

A delegating class is justified when it adds access control, logging, caching, or API-stability guarantees. Flag only when delegation is pure pass-through with no added value.

---

## CL-5: Incomplete Library Class

### ❌ BROKEN (exhibits the smell)

The date library lacks a `business_days_between` method, so the logic is scattered across call sites.

~~~python
def days_until_deadline(start, end):
    count = 0
    current = start
    while current < end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count
~~~

### ✅ CORRECT (after Introduce Local Extension — wrapper or helper module)

~~~python
class BusinessCalendar:
    """Local extension wrapping date utilities the library doesn't provide."""

    @staticmethod
    def business_days_between(start, end) -> int:
        count = 0
        current = start
        while current < end:
            if current.weekday() < 5:
                count += 1
            current += timedelta(days=1)
        return count


days = BusinessCalendar.business_days_between(start, end)
~~~
