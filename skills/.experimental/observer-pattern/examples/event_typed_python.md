# Event-Typed Observer – Python Example

Minimal Event-Typed Observer example with per-type subscriber lists managed by an EventManager.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The event manager broadcasts all events to all subscribers regardless of the event type they subscribed to.

~~~python
"""
What breaks
- No per-type filtering; every subscriber receives every event
- Event-type discriminator exists but is ignored during dispatch
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/event_manager.py
# +++ b/event_manager.py
# @@
# - for subscriber in self._listeners.get(event_type, []):
# -     subscriber.update(event_type, data)
# + for subs in self._listeners.values():
# +     for subscriber in subs:
# +         subscriber.update(event_type, data)
#   # ❌ BUG: broadcasts all events to all subscribers; no per-type filtering.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
from abc import ABC, abstractmethod


class Subscriber(ABC):
    @abstractmethod
    def update(self, event_type: str, data: str) -> None: ...


class EmailSubscriber(Subscriber):
    def update(self, event_type: str, data: str) -> None:
        print(f"Email [{event_type}]: {data}")


class SmsSubscriber(Subscriber):
    def update(self, event_type: str, data: str) -> None:
        print(f"SMS [{event_type}]: {data}")


class EventManager:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Subscriber]] = {}

    def subscribe(self, event_type: str, subscriber: Subscriber) -> None:
        self._listeners.setdefault(event_type, []).append(subscriber)

    def unsubscribe(self, event_type: str, subscriber: Subscriber) -> None:
        self._listeners.get(event_type, []).remove(subscriber)

    def notify(self, event_type: str, data: str) -> None:
        for subscriber in self._listeners.get(event_type, []):
            subscriber.update(event_type, data)


class NewsPublisher:
    def __init__(self) -> None:
        self.events = EventManager()

    def publish(self, event_type: str, message: str) -> None:
        print(f"Publishing [{event_type}]: {message}")
        self.events.notify(event_type, message)


publisher = NewsPublisher()
email = EmailSubscriber()
sms = SmsSubscriber()

publisher.events.subscribe("breaking", email)
publisher.events.subscribe("breaking", sms)
publisher.events.subscribe("sports", email)

publisher.publish("breaking", "Server outage resolved")
publisher.publish("sports", "Local team wins")  # only email receives this
~~~

---

## ▶ EXPLICIT EXAMPLE (DYNAMIC EVENT-TYPE REGISTRATION)

Observers can subscribe and unsubscribe from specific event types at runtime.

~~~python
publisher = NewsPublisher()
email = EmailSubscriber()

publisher.events.subscribe("breaking", email)
publisher.publish("breaking", "Alert!")  # email receives

publisher.events.subscribe("sports", email)
publisher.publish("sports", "Goal!")  # email receives

publisher.events.unsubscribe("breaking", email)
publisher.publish("breaking", "Update")  # email does NOT receive
publisher.publish("sports", "Final score")  # email still receives
~~~
