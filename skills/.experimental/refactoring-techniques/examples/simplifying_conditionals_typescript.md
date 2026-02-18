# Simplifying Conditional Expressions – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## SC-1: Replace Conditional with Polymorphism

### ❌ BEFORE

A switch dispatches on a type string.

~~~typescript
type BirdData = { type: string; voltage?: number; coconuts?: number };

function speed(bird: BirdData): number {
  switch (bird.type) {
    case "european":
      return 35;
    case "african":
      return 40 - 12 * (bird.coconuts ?? 0);
    case "norwegian_blue":
      return (bird.voltage ?? 0) < 10 ? 0 : 24;
    default:
      throw new Error(`unknown bird: ${bird.type}`);
  }
}
~~~

### ✅ AFTER (Replace Conditional with Polymorphism)

Mechanical steps:
1. Create a subclass/implementation for each branch of the conditional.
2. Move each branch's logic into the corresponding subclass's override.
3. Remove the conditional from the base.
4. Update creation sites to instantiate the correct subclass.

~~~typescript
interface Bird {
  speed(): number;
}

class European implements Bird {
  speed(): number {
    return 35;
  }
}

class African implements Bird {
  constructor(private coconuts: number) {}
  speed(): number {
    return 40 - 12 * this.coconuts;
  }
}

class NorwegianBlue implements Bird {
  constructor(private voltage: number) {}
  speed(): number {
    return this.voltage < 10 ? 0 : 24;
  }
}
~~~

### ▶ EDGE CASE

If the conditional appears in only one place and new branches are unlikely, a simple switch may be clearer than a class hierarchy. Apply this technique when the switch repeats across multiple methods or new cases are anticipated.
