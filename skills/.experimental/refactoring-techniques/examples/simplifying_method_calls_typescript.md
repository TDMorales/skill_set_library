# Simplifying Method Calls – TypeScript Examples

Before/after examples showing the mechanical steps for each technique.

---

## SM-1: Rename Method

### ❌ BEFORE

Method name does not communicate purpose.

~~~typescript
class Customer {
  sc(): number {
    return this.rentals.reduce((sum, r) => sum + r.amount, 0);
  }
}
~~~

### ✅ AFTER

Mechanical steps:
1. Create a new method with the better name and copy the body.
2. Update all call sites to use the new name.
3. Remove the old method.

~~~typescript
class Customer {
  totalRentalCharge(): number {
    return this.rentals.reduce((sum, r) => sum + r.amount, 0);
  }
}
~~~

---

## SM-2: Introduce Parameter Object

### ❌ BEFORE

The same group of parameters repeats across multiple functions.

~~~typescript
function readingsOutsideRange(readings: Reading[], minTemp: number, maxTemp: number): Reading[] {
  return readings.filter((r) => r.temp < minTemp || r.temp > maxTemp);
}

function alertOutsideRange(readings: Reading[], minTemp: number, maxTemp: number): void {
  for (const r of readingsOutsideRange(readings, minTemp, maxTemp)) {
    sendAlert(r);
  }
}
~~~

### ✅ AFTER

Mechanical steps:
1. Create a type or class that bundles the recurring parameters.
2. Replace parameter groups with the new object at all call sites.
3. Move behavior that operates solely on the grouped data into the new class.

~~~typescript
class TemperatureRange {
  constructor(readonly min: number, readonly max: number) {}

  contains(value: number): boolean {
    return value >= this.min && value <= this.max;
  }
}

function readingsOutsideRange(readings: Reading[], range: TemperatureRange): Reading[] {
  return readings.filter((r) => !range.contains(r.temp));
}

function alertOutsideRange(readings: Reading[], range: TemperatureRange): void {
  for (const r of readingsOutsideRange(readings, range)) {
    sendAlert(r);
  }
}
~~~

---

## SM-3: Preserve Whole Object

### ❌ BEFORE

Multiple fields are extracted from an object and passed as separate arguments.

~~~typescript
function isWithinPlan(plan: Plan, low: number, high: number): boolean {
  return plan.min <= low && plan.max >= high;
}

const range = station.readings;
isWithinPlan(plan, range.low, range.high);
~~~

### ✅ AFTER

Mechanical steps:
1. Change the function signature to accept the whole object.
2. Update the function body to pull needed values from the object.
3. Update all call sites to pass the object instead of extracted fields.

~~~typescript
function isWithinPlan(plan: Plan, readings: Readings): boolean {
  return plan.min <= readings.low && plan.max >= readings.high;
}

isWithinPlan(plan, station.readings);
~~~

### ▶ EDGE CASE

Do not pass the whole object if it would create an unwanted dependency between the called function and the object's type. If only one or two stable fields are needed and the object is from a different layer (e.g., HTTP request), extracting fields may preserve better separation of concerns.
