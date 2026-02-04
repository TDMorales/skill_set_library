# Builder – TypeScript Example

Minimal Builder example with step methods and a build gate that prevents invalid partial state.

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
// - return { title: this.title, body: this.body, footer: this.footer ?? "" };
// + return {
// +   title: this.title ?? "",
// +   body: this.body ?? "",
// +   footer: this.footer ?? "",
// + };
//   // ❌ BUG: silently accepts invalid partial state.
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

class ReportBuilder {
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
    return {
      title: this.title,
      body: this.body,
      footer: this.footer ?? "",
    };
  }
}

const report = new ReportBuilder()
  .withTitle("Q1")
  .withBody("Summary")
  .withFooter("Confidential")
  .build();

console.log(report.title);
~~~

---

## ▶ EXPLICIT EXAMPLE (DIRECTOR ONLY IF REUSED)

Use a Director when you have repeated construction sequences.

~~~typescript
class ReportDirector {
  constructor(private builder: ReportBuilder) {}

  minimal(): ReportDraft {
    return this.builder.withTitle("Untitled").withBody("").build();
  }

  full(): ReportDraft {
    return this.builder
      .withTitle("Q1")
      .withBody("Summary")
      .withFooter("Confidential")
      .build();
  }
}

const director = new ReportDirector(new ReportBuilder());
console.log(director.full().title);
~~~
