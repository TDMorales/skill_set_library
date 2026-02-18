# Composing Methods – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## CM-1: Extract Method

### ❌ BEFORE

~~~python
def print_invoice(invoice):
    print(f"Invoice: {invoice.id}")
    outstanding = 0.0
    for item in invoice.items:
        outstanding += item.amount
    if invoice.due_date < date.today():
        outstanding *= 1.1
    print(f"Name: {invoice.customer.name}")
    print(f"Outstanding: ${outstanding:.2f}")
~~~

### ✅ AFTER (Extract Method applied)

Mechanical steps:
1. Identify the coherent block (outstanding calculation).
2. Check which local variables are read (invoice) and written (outstanding).
3. Create a new method with the read variables as parameters; return the written variable.
4. Replace the original block with a call.

~~~python
def calculate_outstanding(invoice) -> float:
    outstanding = 0.0
    for item in invoice.items:
        outstanding += item.amount
    if invoice.due_date < date.today():
        outstanding *= 1.1
    return outstanding


def print_invoice(invoice):
    print(f"Invoice: {invoice.id}")
    outstanding = calculate_outstanding(invoice)
    print(f"Name: {invoice.customer.name}")
    print(f"Outstanding: ${outstanding:.2f}")
~~~

### ▶ EDGE CASE

When the block writes multiple local variables, consider Extract Method with a returned tuple or a named result object. If the block is too entangled, apply Split Temporary Variable or Replace Temp with Query first.

---

## CM-2: Decompose Conditional

### ❌ BEFORE

~~~python
def get_charge(date, quantity, plan):
    if date < plan.summer_start or date > plan.summer_end:
        charge = quantity * plan.winter_rate + plan.winter_service_charge
    else:
        charge = quantity * plan.summer_rate
    return charge
~~~

### ✅ AFTER (Decompose Conditional applied)

Mechanical steps:
1. Extract the condition into a named method (`is_summer`).
2. Extract the then-branch into a named method (`summer_charge`).
3. Extract the else-branch into a named method (`winter_charge`).

~~~python
def is_summer(date, plan) -> bool:
    return plan.summer_start <= date <= plan.summer_end


def summer_charge(quantity, plan) -> float:
    return quantity * plan.summer_rate


def winter_charge(quantity, plan) -> float:
    return quantity * plan.winter_rate + plan.winter_service_charge


def get_charge(date, quantity, plan) -> float:
    if is_summer(date, plan):
        return summer_charge(quantity, plan)
    return winter_charge(quantity, plan)
~~~
