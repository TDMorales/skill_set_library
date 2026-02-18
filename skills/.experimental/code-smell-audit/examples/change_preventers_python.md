# Change Preventers – Python Examples

Before/after examples for each Change Preventer smell. Each section shows the smell, then the refactored version.

---

## CP-1: Divergent Change

### ❌ BROKEN (exhibits the smell)

A single class is modified for unrelated reasons — database schema changes AND notification format changes AND report logic changes all touch `OrderService`.

~~~python
class OrderService:
    def save_order(self, order):
        db = connect_db()
        db.execute("INSERT INTO orders ...", order.to_dict())

    def notify_customer(self, order):
        body = f"Order {order.id} confirmed"
        send_email(order.customer.email, "Confirmation", body)

    def generate_monthly_report(self):
        rows = connect_db().execute("SELECT * FROM orders WHERE ...")
        return format_csv(rows)
~~~

### ✅ CORRECT (after Extract Class — one class per axis of change)

~~~python
class OrderRepository:
    def save(self, order):
        db = connect_db()
        db.execute("INSERT INTO orders ...", order.to_dict())


class OrderNotifier:
    def notify_customer(self, order):
        body = f"Order {order.id} confirmed"
        send_email(order.customer.email, "Confirmation", body)


class OrderReporter:
    def generate_monthly_report(self):
        rows = connect_db().execute("SELECT * FROM orders WHERE ...")
        return format_csv(rows)
~~~

---

## CP-2: Shotgun Surgery

### ❌ BROKEN (exhibits the smell)

Changing the logging format requires edits in every file that logs.

~~~python
# file: auth.py
def login(user, password):
    print(f"[INFO] {datetime.now()} auth.login called")
    ...

# file: orders.py
def place_order(order):
    print(f"[INFO] {datetime.now()} orders.place_order called")
    ...

# file: payments.py
def charge(card, amount):
    print(f"[INFO] {datetime.now()} payments.charge called")
    ...
~~~

### ✅ CORRECT (after Move Method — consolidate into one module)

~~~python
# file: logger.py
import logging

logger = logging.getLogger(__name__)

def log_call(name: str):
    logger.info(f"{name} called")


# file: auth.py
from logger import log_call

def login(user, password):
    log_call("auth.login")
    ...

# file: orders.py
from logger import log_call

def place_order(order):
    log_call("orders.place_order")
    ...

# file: payments.py
from logger import log_call

def charge(card, amount):
    log_call("payments.charge")
    ...
~~~

---

## CP-3: Parallel Inheritance Hierarchies

### ❌ BROKEN (exhibits the smell)

Every new `Shape` subclass requires a matching `ShapeSerializer` subclass.

~~~python
class Shape: ...
class Circle(Shape): ...
class Rectangle(Shape): ...

class ShapeSerializer: ...
class CircleSerializer(ShapeSerializer): ...
class RectangleSerializer(ShapeSerializer): ...
~~~

### ✅ CORRECT (after Move Method — collapse one hierarchy into the other)

~~~python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def serialize(self) -> dict: ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def serialize(self) -> dict:
        return {"type": "circle", "radius": self.radius}


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def serialize(self) -> dict:
        return {"type": "rectangle", "width": self.width, "height": self.height}
~~~

### ▶ EDGE CASE

Keeping separate hierarchies is justified when serialization logic is complex enough to warrant its own tests and the serialization format changes independently from shape behavior (e.g., supporting multiple wire formats).
