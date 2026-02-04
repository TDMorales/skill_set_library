# Builder – Python Example

Minimal Builder example with step methods and a build gate that prevents invalid partial state.

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
# - return ReportDraft(self._title, self._body, footer)
# + return ReportDraft(self._title or "", self._body or "", self._footer or "")
#   # ❌ BUG: silently accepts invalid partial state.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
class ReportDraft:
    def __init__(self, title: str, body: str, footer: str):
        self.title = title
        self.body = body
        self.footer = footer


class ReportBuilder:
    def __init__(self) -> None:
        self._title: str | None = None
        self._body: str | None = None
        self._footer: str | None = None

    def with_title(self, title: str) -> "ReportBuilder":
        self._title = title
        return self

    def with_body(self, body: str) -> "ReportBuilder":
        self._body = body
        return self

    def with_footer(self, footer: str) -> "ReportBuilder":
        self._footer = footer
        return self

    def build(self) -> ReportDraft:
        if self._title is None or self._body is None:
            raise ValueError("title and body are required")
        footer = self._footer or ""
        return ReportDraft(self._title, self._body, footer)


report = (
    ReportBuilder()
    .with_title("Q1")
    .with_body("Summary")
    .with_footer("Confidential")
    .build()
)
print(report.title)
~~~

---

## ▶ EXPLICIT EXAMPLE (DIRECTOR ONLY IF REUSED)

Use a Director when you have repeated construction sequences.

~~~python
class ReportDirector:
    def __init__(self, builder: ReportBuilder) -> None:
        self._builder = builder

    def minimal(self) -> ReportDraft:
        return self._builder.with_title("Untitled").with_body("").build()

    def full(self) -> ReportDraft:
        return (
            self._builder
            .with_title("Q1")
            .with_body("Summary")
            .with_footer("Confidential")
            .build()
        )


director = ReportDirector(ReportBuilder())
print(director.full().title)
~~~
