# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants. Keep these minimal and adapt names to your domain.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of Observer rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Observer: subjects/publishers, observer interfaces, subscription methods, notification calls.
   - Event-typed: event managers, event-type registries, filtered dispatch logic.
2. **Locate call sites**
   - Trace notification trigger points and observer registration points.
3. **Map flows**
   - Observer: state change → notify → observer.update → side effect.
   - Event-typed: state change → event type → filtered dispatch → observer.update → side effect.
4. **Check invariants**
   - Evaluate OB-* and/or ET-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as "verified" (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant notification seams
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- variant target:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `OP-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of OB-* or ET-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what breaks or becomes harder to change
- **Minimal Fix:** concrete change (describe or patch snippet)
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified
  - `[ ]` not verified / missing
  - `[!]` violated (must link to finding IDs)

---

## Observer – Basic (Python)

```python
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
```

## Observer – Basic (TypeScript)

```ts
interface Subscriber {
  update(publisher: NewsPublisher, message: string): void;
}

class EmailSubscriber implements Subscriber {
  update(publisher: NewsPublisher, message: string): void {
    console.log(`Email: ${message}`);
  }
}

class SmsSubscriber implements Subscriber {
  update(publisher: NewsPublisher, message: string): void {
    console.log(`SMS: ${message}`);
  }
}

class NewsPublisher {
  private subscribers: Subscriber[] = [];

  attach(subscriber: Subscriber): void {
    this.subscribers.push(subscriber);
  }

  detach(subscriber: Subscriber): void {
    this.subscribers = this.subscribers.filter((s) => s !== subscriber);
  }

  private notify(message: string): void {
    for (const subscriber of this.subscribers) {
      subscriber.update(this, message);
    }
  }

  publish(message: string): void {
    console.log(`Publishing: ${message}`);
    this.notify(message);
  }
}

const publisher = new NewsPublisher();
const email = new EmailSubscriber();
const sms = new SmsSubscriber();

publisher.attach(email);
publisher.attach(sms);
publisher.publish("Breaking: new release!");
```

---

## Event-Typed Observer (Python)

```python
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
publisher.publish("sports", "Local team wins")
```

## Event-Typed Observer (TypeScript)

```ts
interface Subscriber {
  update(eventType: string, data: string): void;
}

class EmailSubscriber implements Subscriber {
  update(eventType: string, data: string): void {
    console.log(`Email [${eventType}]: ${data}`);
  }
}

class SmsSubscriber implements Subscriber {
  update(eventType: string, data: string): void {
    console.log(`SMS [${eventType}]: ${data}`);
  }
}

class EventManager {
  private listeners: Map<string, Subscriber[]> = new Map();

  subscribe(eventType: string, subscriber: Subscriber): void {
    const subs = this.listeners.get(eventType) ?? [];
    subs.push(subscriber);
    this.listeners.set(eventType, subs);
  }

  unsubscribe(eventType: string, subscriber: Subscriber): void {
    const subs = this.listeners.get(eventType) ?? [];
    this.listeners.set(
      eventType,
      subs.filter((s) => s !== subscriber)
    );
  }

  notify(eventType: string, data: string): void {
    for (const subscriber of this.listeners.get(eventType) ?? []) {
      subscriber.update(eventType, data);
    }
  }
}

class NewsPublisher {
  readonly events = new EventManager();

  publish(eventType: string, message: string): void {
    console.log(`Publishing [${eventType}]: ${message}`);
    this.events.notify(eventType, message);
  }
}

const publisher = new NewsPublisher();
const email = new EmailSubscriber();
const sms = new SmsSubscriber();

publisher.events.subscribe("breaking", email);
publisher.events.subscribe("breaking", sms);
publisher.events.subscribe("sports", email);

publisher.publish("breaking", "Server outage resolved");
publisher.publish("sports", "Local team wins");
```
