# Event-Typed Observer – TypeScript Example

Minimal Event-Typed Observer example with per-type subscriber lists managed by an EventManager.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The event manager broadcasts all events to all subscribers regardless of the event type they subscribed to.

~~~typescript
/**
 * What breaks
 * - No per-type filtering; every subscriber receives every event
 * - Event-type discriminator exists but is ignored during dispatch
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/event_manager.ts
// +++ b/event_manager.ts
// @@
// - for (const subscriber of this.listeners.get(eventType) ?? []) {
// -   subscriber.update(eventType, data);
// - }
// + for (const [, subs] of this.listeners) {
// +   for (const subscriber of subs) {
// +     subscriber.update(eventType, data);
// +   }
// + }
//   // ❌ BUG: broadcasts all events to all subscribers; no per-type filtering.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
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
publisher.publish("sports", "Local team wins"); // only email receives this
~~~

---

## ▶ EXPLICIT EXAMPLE (DYNAMIC EVENT-TYPE REGISTRATION)

Observers can subscribe and unsubscribe from specific event types at runtime.

~~~typescript
const publisher = new NewsPublisher();
const email = new EmailSubscriber();

publisher.events.subscribe("breaking", email);
publisher.publish("breaking", "Alert!"); // email receives

publisher.events.subscribe("sports", email);
publisher.publish("sports", "Goal!"); // email receives

publisher.events.unsubscribe("breaking", email);
publisher.publish("breaking", "Update"); // email does NOT receive
publisher.publish("sports", "Final score"); // email still receives
~~~
