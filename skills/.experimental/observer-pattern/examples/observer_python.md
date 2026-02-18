# Observer – Python Example

Minimal Observer example showing a subscriber interface, a publisher with subscription management, and concrete observers.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The publisher is hard-wired to concrete observer classes—no subscriber interface, no dynamic subscription.

~~~python
"""
What breaks
- Publisher depends on concrete observer classes, not a Subscriber abstraction
- No attach/detach mechanism; observer set is fixed at construction
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/news_publisher.py
# +++ b/news_publisher.py
# @@
# - self._subscribers: list[Subscriber] = []
# + self._email = EmailSubscriber()
# + self._sms = SmsSubscriber()
# ...
# - for subscriber in self._subscribers:
# -     subscriber.update(self, message)
# + self._email.send_email(message)
# + self._sms.send_sms(message)
#   # ❌ BUG: publisher coupled to concrete observers; no subscriber interface.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
from abc import ABC, abstractmethod


class Subscriber(ABC):
    @abstractmethod
    def update(self, publisher: "NewsPublisher", message: str) -> None: ...


class EmailSubscriber(Subscriber):
    def update(self, publisher: "NewsPublisher", message: str) -> None:
        print(f"Email: {message}")


class SmsSubscriber(Subscriber):
    def update(self, publisher: "NewsPublisher", message: str) -> None:
        print(f"SMS: {message}")


class NewsPublisher:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []

    def attach(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)

    def detach(self, subscriber: Subscriber) -> None:
        self._subscribers.remove(subscriber)

    def notify(self, message: str) -> None:
        for subscriber in self._subscribers:
            subscriber.update(self, message)

    def publish(self, message: str) -> None:
        print(f"Publishing: {message}")
        self.notify(message)


publisher = NewsPublisher()
email = EmailSubscriber()
sms = SmsSubscriber()

publisher.attach(email)
publisher.attach(sms)
publisher.publish("Breaking: new release!")
~~~

---

## ▶ EXPLICIT EXAMPLE (DYNAMIC UNSUBSCRIPTION)

Observers can detach at runtime; the publisher keeps working with the remaining subscribers.

~~~python
publisher = NewsPublisher()
email = EmailSubscriber()
sms = SmsSubscriber()

publisher.attach(email)
publisher.attach(sms)
publisher.publish("First story")

publisher.detach(sms)
publisher.publish("Second story")  # only email receives this
~~~
