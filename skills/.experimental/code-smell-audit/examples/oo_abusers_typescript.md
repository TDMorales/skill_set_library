# Object-Orientation Abusers – TypeScript Examples

Before/after examples for each OO Abuser smell. Each section shows the smell, then the refactored version.

---

## OA-1: Switch Statements

### ❌ BROKEN (exhibits the smell)

~~~typescript
function calculateArea(shape: { type: string; [k: string]: any }): number {
  switch (shape.type) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return 0.5 * shape.base * shape.height;
    default:
      throw new Error(`unknown shape: ${shape.type}`);
  }
}
~~~

### ✅ CORRECT (after Replace Conditional with Polymorphism)

~~~typescript
interface Shape {
  area(): number;
}

class Circle implements Shape {
  constructor(private radius: number) {}
  area(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  area(): number {
    return this.width * this.height;
  }
}

class Triangle implements Shape {
  constructor(private base: number, private height: number) {}
  area(): number {
    return 0.5 * this.base * this.height;
  }
}
~~~

### ▶ EDGE CASE

A simple switch on 2–3 values that is unlikely to grow (e.g., parsing a CLI flag) may be clearer than a full class hierarchy. Apply polymorphism when the switch appears in multiple places or new cases are anticipated.

---

## OA-2: Temporary Field

### ❌ BROKEN (exhibits the smell)

~~~typescript
class ReportGenerator {
  private header?: string;
  private data?: string;
  private footer?: string;

  generateFull(data: string): string {
    this.header = "FULL REPORT";
    this.data = data;
    this.footer = "END";
    return this.render();
  }

  generateSummary(data: string): string {
    this.header = "SUMMARY";
    this.data = data;
    // footer is undefined here — only used in generateFull
    return this.render();
  }

  private render(): string {
    const parts = [this.header, this.data];
    if (this.footer) parts.push(this.footer);
    return parts.join("\n");
  }
}
~~~

### ✅ CORRECT (after Extract Class)

~~~typescript
class FullReport {
  constructor(private data: string) {}
  render(): string {
    return `FULL REPORT\n${this.data}\nEND`;
  }
}

class SummaryReport {
  constructor(private data: string) {}
  render(): string {
    return `SUMMARY\n${this.data}`;
  }
}
~~~

---

## OA-3: Refused Bequest

### ❌ BROKEN (exhibits the smell)

~~~typescript
class Animal {
  walk(): string { return "walking"; }
  speak(): string { return "..."; }
}

class Dog extends Animal {
  speak(): string { return "woof"; }
}

class Fish extends Animal {
  walk(): string { throw new Error("fish can't walk"); }
  speak(): string { throw new Error("fish can't speak"); }
}
~~~

### ✅ CORRECT (after Extract Superclass / Replace Inheritance with Delegation)

~~~typescript
interface Animal {
  move(): string;
}

class Dog implements Animal {
  move(): string { return "walking"; }
  speak(): string { return "woof"; }
}

class Fish implements Animal {
  move(): string { return "swimming"; }
}
~~~

---

## OA-4: Alternative Classes with Different Interfaces

### ❌ BROKEN (exhibits the smell)

~~~typescript
class PdfRenderer {
  renderPdf(content: string): Uint8Array { /* ... */ }
}

class HtmlRenderer {
  toHtml(content: string): string { /* ... */ }
}
~~~

### ✅ CORRECT (after Rename Method + Extract Superclass)

~~~typescript
interface Renderer {
  render(content: string): string | Uint8Array;
}

class PdfRenderer implements Renderer {
  render(content: string): Uint8Array { /* ... */ }
}

class HtmlRenderer implements Renderer {
  render(content: string): string { /* ... */ }
}
~~~
