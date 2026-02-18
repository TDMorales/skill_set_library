# Bloaters – Python Examples

Before/after examples for each Bloater smell. Each section shows the smell, then the refactored version.

---

## BL-1: Long Method

### ❌ BROKEN (exhibits the smell)

~~~python
def process_order(order):
    if not order.items:
        raise ValueError("empty order")
    if not order.customer:
        raise ValueError("no customer")
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    tax = subtotal * 0.08
    total = subtotal + tax
    if order.customer.is_premium:
        total *= 0.9
    invoice = f"Invoice for {order.customer.name}\n"
    for item in order.items:
        invoice += f"  {item.name}: ${item.price * item.quantity:.2f}\n"
    invoice += f"Total: ${total:.2f}"
    send_email(order.customer.email, "Order Confirmed", invoice)
    return total
~~~

### ✅ CORRECT (after Extract Method)

~~~python
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    invoice = generate_invoice(order, total)
    send_confirmation(order.customer, invoice)
    return total


def validate_order(order):
    if not order.items:
        raise ValueError("empty order")
    if not order.customer:
        raise ValueError("no customer")


def calculate_total(order):
    subtotal = sum(i.price * i.quantity for i in order.items)
    tax = subtotal * 0.08
    total = subtotal + tax
    if order.customer.is_premium:
        total *= 0.9
    return total


def generate_invoice(order, total: float) -> str:
    lines = [f"Invoice for {order.customer.name}"]
    for item in order.items:
        lines.append(f"  {item.name}: ${item.price * item.quantity:.2f}")
    lines.append(f"Total: ${total:.2f}")
    return "\n".join(lines)


def send_confirmation(customer, invoice: str) -> None:
    send_email(customer.email, "Order Confirmed", invoice)
~~~

### ▶ EDGE CASE

Sequential setup code (e.g., test fixtures or CLI argument parsing) may be acceptably long if each line is simple and extraction would obscure the flow.

---

## BL-2: Large Class

### ❌ BROKEN (exhibits the smell)

~~~python
class UserManager:
    def create_user(self, name, email): ...
    def delete_user(self, user_id): ...
    def update_profile(self, user_id, data): ...
    def authenticate(self, email, password): ...
    def reset_password(self, email): ...
    def send_welcome_email(self, user): ...
    def send_password_reset_email(self, user): ...
    def generate_report(self, user_id): ...
    def export_to_csv(self, user_id): ...
~~~

### ✅ CORRECT (after Extract Class)

~~~python
class UserRepository:
    def create(self, name, email): ...
    def delete(self, user_id): ...
    def update_profile(self, user_id, data): ...


class AuthService:
    def authenticate(self, email, password): ...
    def reset_password(self, email): ...


class UserNotifier:
    def send_welcome_email(self, user): ...
    def send_password_reset_email(self, user): ...


class UserReportExporter:
    def generate_report(self, user_id): ...
    def export_to_csv(self, user_id): ...
~~~

---

## BL-3: Primitive Obsession

### ❌ BROKEN (exhibits the smell)

~~~python
def create_invoice(
    amount: float,
    currency: str,
    zip_code: str,
    phone: str,
):
    if currency not in ("USD", "EUR", "GBP"):
        raise ValueError("bad currency")
    if len(zip_code) != 5 or not zip_code.isdigit():
        raise ValueError("bad zip")
    ...
~~~

### ✅ CORRECT (after Replace Data Value with Object)

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

    def __post_init__(self):
        if self.currency not in ("USD", "EUR", "GBP"):
            raise ValueError(f"unsupported currency: {self.currency}")


@dataclass(frozen=True)
class ZipCode:
    value: str

    def __post_init__(self):
        if len(self.value) != 5 or not self.value.isdigit():
            raise ValueError(f"invalid zip: {self.value}")


def create_invoice(price: Money, zip_code: ZipCode, phone: str):
    ...
~~~

### ▶ EDGE CASE

Not every string or int needs a wrapper. Reserve value objects for domain concepts with validation rules or formatting logic that would otherwise be duplicated.

---

## BL-4: Long Parameter List

### ❌ BROKEN (exhibits the smell)

~~~python
def schedule_meeting(
    title: str,
    start: datetime,
    end: datetime,
    room: str,
    organizer: str,
    attendees: list[str],
    recurrence: str | None,
    reminder_minutes: int,
):
    ...
~~~

### ✅ CORRECT (after Introduce Parameter Object)

~~~python
@dataclass
class MeetingRequest:
    title: str
    start: datetime
    end: datetime
    room: str
    organizer: str
    attendees: list[str]
    recurrence: str | None = None
    reminder_minutes: int = 15


def schedule_meeting(request: MeetingRequest):
    ...
~~~

---

## BL-5: Data Clumps

### ❌ BROKEN (exhibits the smell)

~~~python
def geocode(street: str, city: str, state: str, zip_code: str) -> tuple:
    ...

def validate_address(street: str, city: str, state: str, zip_code: str) -> bool:
    ...

def format_label(street: str, city: str, state: str, zip_code: str) -> str:
    ...
~~~

### ✅ CORRECT (after Extract Class)

~~~python
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str


def geocode(address: Address) -> tuple:
    ...

def validate_address(address: Address) -> bool:
    ...

def format_label(address: Address) -> str:
    ...
~~~
