# Builder – TypeScript Example

Minimal Builder example with an abstract builder interface, step methods, a build gate that prevents invalid partial state, and a reset mechanism for reuse.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The builder returns partially-initialized results without validation.

~~~typescript
/**
 * What breaks
 * - No build gate validation
 * - Partial state escapes as a "finished" object
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/report_builder.ts
// +++ b/report_builder.ts
// @@
// - if (!this.title || !this.body) {
// -   throw new Error("title and body are required");
// - }
// - const result = { title: this.title, body: this.body, footer: this.footer ?? "" };
// - this.reset();
// - return result;
// + return {
// +   title: this.title ?? "",
// +   body: this.body ?? "",
// +   footer: this.footer ?? "",
// + };
//   // ❌ BUG: silently accepts invalid partial state; no reset after build.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
type ReportDraft = {
  title: string;
  body: string;
  footer: string;
};

interface ReportBuilder {
  withTitle(title: string): ReportBuilder;
  withBody(body: string): ReportBuilder;
  withFooter(footer: string): ReportBuilder;
  build(): ReportDraft;
  reset(): void;
}

class StandardReportBuilder implements ReportBuilder {
  private title?: string;
  private body?: string;
  private footer?: string;

  withTitle(title: string): this {
    this.title = title;
    return this;
  }

  withBody(body: string): this {
    this.body = body;
    return this;
  }

  withFooter(footer: string): this {
    this.footer = footer;
    return this;
  }

  build(): ReportDraft {
    if (!this.title || !this.body) {
      throw new Error("title and body are required");
    }
    const result: ReportDraft = {
      title: this.title,
      body: this.body,
      footer: this.footer ?? "",
    };
    this.reset();
    return result;
  }

  reset(): void {
    this.title = undefined;
    this.body = undefined;
    this.footer = undefined;
  }
}

const builder: ReportBuilder = new StandardReportBuilder();
const report = builder
  .withTitle("Q1")
  .withBody("Summary")
  .withFooter("Confidential")
  .build();

console.log(report.title);
~~~

---

## ▶ EXPLICIT EXAMPLE (DIRECTOR WITH SETTER + BOTH PATHS)

Director accepts the builder via a setter so it can be swapped at runtime.
Client code works both with and without the Director.

~~~typescript
class ReportDirector {
  private _builder?: ReportBuilder;

  set builder(builder: ReportBuilder) {
    this._builder = builder;
  }

  get builder(): ReportBuilder {
    if (!this._builder) throw new Error("builder not set");
    return this._builder;
  }

  minimalReport(): ReportDraft {
    return this.builder.withTitle("Untitled").withBody("").build();
  }

  fullReport(): ReportDraft {
    return this.builder
      .withTitle("Q1")
      .withBody("Summary")
      .withFooter("Confidential")
      .build();
  }
}

// With Director
const director = new ReportDirector();
director.builder = new StandardReportBuilder();
console.log(director.fullReport().title);

// Without Director (builder reused directly — reset clears state between builds)
const builder = new StandardReportBuilder();
const first = builder.withTitle("Report A").withBody("Body A").build();
const second = builder.withTitle("Report B").withBody("Body B").build();
console.log(first.title, second.title);
~~~
