# Factory Method – TypeScript Example

Minimal Factory Method example showing a product interface, creator factory method, and concrete creators.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The client constructs concrete products directly and no factory method exists.

~~~typescript
/**
 * What breaks
 * - Client depends on concrete classes, not a Product abstraction
 * - Creation logic is scattered across call sites
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/reporting.ts
// +++ b/reporting.ts
// @@
// - const creator: ReportCreator = new PdfReportCreator();
// - console.log(creator.generate());
// + const report = new PdfReport();
// + console.log(report.render());
//   // ❌ BUG: client knows concrete type; no factory method seam.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
interface Report {
  render(): string;
}

class PdfReport implements Report {
  render(): string {
    return "PDF";
  }
}

class HtmlReport implements Report {
  render(): string {
    return "HTML";
  }
}

abstract class ReportCreator {
  abstract createReport(): Report;

  generate(): string {
    const report = this.createReport();
    return report.render();
  }
}

class PdfReportCreator extends ReportCreator {
  createReport(): Report {
    return new PdfReport();
  }
}

class HtmlReportCreator extends ReportCreator {
  createReport(): Report {
    return new HtmlReport();
  }
}

const creator: ReportCreator = new PdfReportCreator();
console.log(creator.generate());
~~~

---

## ▶ EXPLICIT EXAMPLE (RUNTIME SELECTION SEAM)

Concrete creator is selected at the seam, and the client still depends only on the abstraction.

~~~typescript
function selectCreator(kind: string): ReportCreator {
  if (kind === "pdf") return new PdfReportCreator();
  if (kind === "html") return new HtmlReportCreator();
  throw new Error("unknown report kind");
}

const creator = selectCreator("html");
console.log(creator.generate());
~~~
