# Factory Method – Python Example

Minimal Factory Method example showing a product abstraction, creator factory method, and concrete creators.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

The client constructs concrete products directly and no factory method exists.

~~~python
"""
What breaks
- Client depends on concrete classes, not a Product abstraction
- Creation logic is scattered across call sites
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/reporting.py
# +++ b/reporting.py
# @@
# - creator: ReportCreator = PdfReportCreator()
# - print(creator.generate())
# + report = PdfReport()
# + print(report.render())
#   # ❌ BUG: client knows concrete type; no factory method seam.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
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
~~~

---

## ▶ EXPLICIT EXAMPLE (RUNTIME SELECTION SEAM)

Concrete creator is selected at the seam, and the client still depends only on the abstraction.

~~~python
def select_creator(kind: str) -> ReportCreator:
    if kind == "pdf":
        return PdfReportCreator()
    if kind == "html":
        return HtmlReportCreator()
    raise ValueError("unknown report kind")


creator = select_creator("html")
print(creator.generate())
~~~
