# Builder – Python Example

Minimal Builder example with an abstract builder interface, step methods, a build gate that prevents invalid partial state, and a reset mechanism for reuse.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The builder returns partially-initialized results without validation.

~~~python
"""
What breaks
- No build gate validation
- Partial state escapes as a "finished" object
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/report_builder.py
# +++ b/report_builder.py
# @@
# - if self._title is None or self._body is None:
# -     raise ValueError("title and body are required")
# - footer = self._footer or ""
# - result = ReportDraft(self._title, self._body, footer)
# - self.reset()
# - return result
# + return ReportDraft(self._title or "", self._body or "", self._footer or "")
#   # ❌ BUG: silently accepts invalid partial state; no reset after build.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
from abc import ABC, abstractmethod


class ReportDraft:
    def __init__(self, title: str, body: str, footer: str):
        self.title = title
        self.body = body
        self.footer = footer


class ReportBuilder(ABC):
    """Abstract builder interface — declares step contract for all concrete builders."""

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
print(report.title)
~~~

---

## ▶ EXPLICIT EXAMPLE (DIRECTOR WITH SETTER + BOTH PATHS)

Director accepts the builder via a setter so it can be swapped at runtime.
Client code works both with and without the Director.

~~~python
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


# With Director
director = ReportDirector()
director.builder = StandardReportBuilder()
print(director.full_report().title)

# Without Director (builder reused directly — reset clears state between builds)
builder = StandardReportBuilder()
first = builder.with_title("Report A").with_body("Body A").build()
second = builder.with_title("Report B").with_body("Body B").build()
print(first.title, second.title)
~~~
