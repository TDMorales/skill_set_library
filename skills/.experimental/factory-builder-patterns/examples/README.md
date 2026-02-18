# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants. Keep these minimal and adapt names to your domain.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of Factory Method and/or Builder rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Factory Method: creators, factory methods, product abstractions, creation seams.
   - Builder: abstract builder interfaces, concrete builders, step methods, build() gates, reset mechanisms, optional directors.
2. **Locate call sites**
   - Trace instantiation points for concrete products or built results.
3. **Map flows**
   - Factory Method: selection seam → creator → product → client usage.
   - Builder: step ordering → validation → build() → result usage.
4. **Check invariants**
   - Evaluate FM-* and/or B-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as “verified” (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant creation seams
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- pattern target:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `FB-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of FM-* or B-* invariants)
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

## Factory Method (Python)

```python
from abc import ABC, abstractmethod

# Product abstraction
class Report(ABC):
    @abstractmethod
    def render(self) -> str: ...

# Concrete products
class PdfReport(Report):
    def render(self) -> str:
        return "PDF"

class HtmlReport(Report):
    def render(self) -> str:
        return "HTML"

# Creator with factory method
class ReportCreator(ABC):
    @abstractmethod
    def create_report(self) -> Report: ...

    def generate(self) -> str:
        report = self.create_report()
        return report.render()

# Concrete creators
class PdfReportCreator(ReportCreator):
    def create_report(self) -> Report:
        return PdfReport()

class HtmlReportCreator(ReportCreator):
    def create_report(self) -> Report:
        return HtmlReport()

# Client depends on abstraction
creator: ReportCreator = PdfReportCreator()
print(creator.generate())
```

## Factory Method (TypeScript)

```ts
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
```

---

## Builder (Python)

```python
from abc import ABC, abstractmethod

class ReportDraft:
    def __init__(self, title: str, body: str, footer: str):
        self.title = title
        self.body = body
        self.footer = footer

class ReportBuilder(ABC):
    @abstractmethod
    def with_title(self, title: str) -> "ReportBuilder": ...
    @abstractmethod
    def with_body(self, body: str) -> "ReportBuilder": ...
    @abstractmethod
    def with_footer(self, footer: str) -> "ReportBuilder": ...
    @abstractmethod
    def build(self) -> ReportDraft: ...
    @abstractmethod
    def reset(self) -> None: ...

class StandardReportBuilder(ReportBuilder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._title: str | None = None
        self._body: str | None = None
        self._footer: str | None = None

    def with_title(self, title: str) -> "StandardReportBuilder":
        self._title = title
        return self

    def with_body(self, body: str) -> "StandardReportBuilder":
        self._body = body
        return self

    def with_footer(self, footer: str) -> "StandardReportBuilder":
        self._footer = footer
        return self

    def build(self) -> ReportDraft:
        if self._title is None or self._body is None:
            raise ValueError("title and body are required")
        footer = self._footer or ""
        result = ReportDraft(self._title, self._body, footer)
        self.reset()
        return result

builder: ReportBuilder = StandardReportBuilder()
report = (
    builder
    .with_title("Q1")
    .with_body("Summary")
    .with_footer("Confidential")
    .build()
)
```

## Builder (TypeScript)

```ts
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
```

---

## Builder + Optional Director (when repeated choreography exists)

Use a Director only if you have 2+ repeated build sequences that would otherwise be duplicated.
Director accepts the builder via a setter so it can be swapped at runtime.

```python
class ReportDirector:
    def __init__(self) -> None:
        self._builder: ReportBuilder | None = None

    @property
    def builder(self) -> ReportBuilder:
        if self._builder is None:
            raise ValueError("builder not set")
        return self._builder

    @builder.setter
    def builder(self, builder: ReportBuilder) -> None:
        self._builder = builder

    def minimal_report(self) -> ReportDraft:
        return self.builder.with_title("Untitled").with_body("").build()

    def full_report(self) -> ReportDraft:
        return (
            self.builder
            .with_title("Q1")
            .with_body("Summary")
            .with_footer("Confidential")
            .build()
        )

director = ReportDirector()
director.builder = StandardReportBuilder()
print(director.full_report().title)
```

```ts
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

const director = new ReportDirector();
director.builder = new StandardReportBuilder();
console.log(director.fullReport().title);
```
