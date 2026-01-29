# WebSocket Client – Health Protocol Compliance

Minimal WebSocket client example that complies with the server-side
health ping/pong contract.
---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The following client violates the health protocol and frame-handling rules.

~~~typescript
/**
  * What breaks
  * - event.data is not parsed from a string frame
  * - health_ping is ignored, causing server-side timeouts
  * - Sending non-string payloads will fail in browsers
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/client.ts
// +++ b/client.ts
// @@
// - if (message.type === 'health_ping') { send health_pong; return; }
// + // ignore health_ping
//   // ❌ BUG: server pings will timeout; server will disconnect you as stale.
//
// @@
// - this.ws.onmessage = (...) => JSON.parse(event.data)
// + this.ws.onmessage = (event) => this.handleMessage(event.data as any)
//   // ❌ BUG: treats event.data as object; breaks on real string frames.
//
// @@
// - this.ws?.send(JSON.stringify(...))
// + this.ws?.send(...)
//   // ❌ BUG: sends object directly; browser expects string/ArrayBuffer/Blob.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
/**
 * Minimal WebSocket client that obeys the health protocol.
 * - Responds immediately to health_ping
 * - Separates message dispatch from transport
 */

export type WsMessage = Record<string, any>;

export class WebSocketClient {
  private ws: WebSocket | null = null;

  connect(url: string) {
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      // Optional: send hello/auth if your server expects it (not required by this skill)
    };

    this.ws.onmessage = (event) => {
      let message: WsMessage;
      try {
        message = JSON.parse(String(event.data));
      } catch {
        // Defensive: ignore malformed frames
        return;
      }

      // Health protocol: respond immediately and do not run app logic
      if (message.type === "health_ping") {
        this.ws?.send(
          JSON.stringify({
            type: "health_pong",
            timestamp: message.timestamp,
          })
        );
        return;
      }

      this.handleMessage(message);
    };

    this.ws.onerror = () => {
      // Don't throw inside event handlers
    };

    this.ws.onclose = () => {
      // App may reconnect here; keep policy outside this minimal example
    };
  }

  send(message: WsMessage) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify(message));
  }

  protected handleMessage(message: WsMessage) {
    // Override in your app
  }
}
~~~

---

### Notes
- Clients **must** respond to `health_ping`
- Clients **must** parse inbound frames safely
- Clients **must** serialize outbound messages