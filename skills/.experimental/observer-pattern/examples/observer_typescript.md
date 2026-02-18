# Observer – TypeScript Example

Minimal Observer example showing a subscriber interface, a publisher with subscription management, and concrete observers.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The publisher is hard-wired to concrete observer classes—no subscriber interface, no dynamic subscription.

~~~typescript
/**
 * What breaks
 * - Publisher depends on concrete observer classes, not a Subscriber interface
 * - No attach/detach mechanism; observer set is fixed at construction
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/news_publisher.ts
// +++ b/news_publisher.ts
// @@
// - private subscribers: Subscriber[] = [];
// + private email = new EmailSubscriber();
// + private sms = new SmsSubscriber();
// ...
// - for (const subscriber of this.subscribers) {
// -   subscriber.update(this, message);
// - }
// + this.email.sendEmail(message);
// + this.sms.sendSms(message);
//   // ❌ BUG: publisher coupled to concrete observers; no subscriber interface.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
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
~~~

---

## ▶ EXPLICIT EXAMPLE (DYNAMIC UNSUBSCRIPTION)

Observers can detach at runtime; the publisher keeps working with the remaining subscribers.

~~~typescript
const publisher = new NewsPublisher();
const email = new EmailSubscriber();
const sms = new SmsSubscriber();

publisher.attach(email);
publisher.attach(sms);
publisher.publish("First story");

publisher.detach(sms);
publisher.publish("Second story"); // only email receives this
~~~
