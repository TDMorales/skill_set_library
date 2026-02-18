# Composing Methods – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## CM-1: Extract Method

### ❌ BEFORE

~~~typescript
function printInvoice(invoice: Invoice): void {
  console.log(`Invoice: ${invoice.id}`);
  let outstanding = 0;
  for (const item of invoice.items) {
    outstanding += item.amount;
  }
  if (invoice.dueDate < new Date()) {
    outstanding *= 1.1;
  }
  console.log(`Name: ${invoice.customer.name}`);
  console.log(`Outstanding: $${outstanding.toFixed(2)}`);
}
~~~

### ✅ AFTER (Extract Method applied)

Mechanical steps:
1. Identify the coherent block (outstanding calculation).
2. Check which local variables are read (invoice) and written (outstanding).
3. Create a new function with the read variables as parameters; return the written variable.
4. Replace the original block with a call.

~~~typescript
function calculateOutstanding(invoice: Invoice): number {
  let outstanding = 0;
  for (const item of invoice.items) {
    outstanding += item.amount;
  }
  if (invoice.dueDate < new Date()) {
    outstanding *= 1.1;
  }
  return outstanding;
}

function printInvoice(invoice: Invoice): void {
  console.log(`Invoice: ${invoice.id}`);
  const outstanding = calculateOutstanding(invoice);
  console.log(`Name: ${invoice.customer.name}`);
  console.log(`Outstanding: $${outstanding.toFixed(2)}`);
}
~~~

### ▶ EDGE CASE

When the block writes multiple local variables, consider returning an object. If the block is too entangled, apply Split Temporary Variable or Replace Temp with Query first.

---

## CM-2: Decompose Conditional

### ❌ BEFORE

~~~typescript
function getCharge(date: Date, quantity: number, plan: Plan): number {
  if (date < plan.summerStart || date > plan.summerEnd) {
    return quantity * plan.winterRate + plan.winterServiceCharge;
  }
  return quantity * plan.summerRate;
}
~~~

### ✅ AFTER (Decompose Conditional applied)

Mechanical steps:
1. Extract the condition into a named function (`isSummer`).
2. Extract the then-branch into a named function (`summerCharge`).
3. Extract the else-branch into a named function (`winterCharge`).

~~~typescript
function isSummer(date: Date, plan: Plan): boolean {
  return date >= plan.summerStart && date <= plan.summerEnd;
}

function summerCharge(quantity: number, plan: Plan): number {
  return quantity * plan.summerRate;
}

function winterCharge(quantity: number, plan: Plan): number {
  return quantity * plan.winterRate + plan.winterServiceCharge;
}

function getCharge(date: Date, quantity: number, plan: Plan): number {
  return isSummer(date, plan)
    ? summerCharge(quantity, plan)
    : winterCharge(quantity, plan);
}
~~~
