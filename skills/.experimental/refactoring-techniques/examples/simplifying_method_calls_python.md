# Simplifying Method Calls – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## SM-1: Rename Method

### ❌ BEFORE

Method name does not communicate purpose.

~~~python
class Customer:
    def sc(self) -> float:
        return sum(r.amount for r in self.rentals)
~~~

### ✅ AFTER

Mechanical steps:
1. Create a new method with the better name and copy the body.
2. Update all call sites to use the new name.
3. Remove the old method.

~~~python
class Customer:
    def total_rental_charge(self) -> float:
        return sum(r.amount for r in self.rentals)
~~~

---

## SM-2: Introduce Parameter Object

### ❌ BEFORE

The same group of parameters repeats across multiple methods.

~~~python
def readings_outside_range(readings, min_temp: float, max_temp: float):
    return [r for r in readings if r.temp < min_temp or r.temp > max_temp]


def alert_outside_range(readings, min_temp: float, max_temp: float):
    for r in readings_outside_range(readings, min_temp, max_temp):
        send_alert(r)
~~~

### ✅ AFTER

Mechanical steps:
1. Create a class or dataclass that bundles the recurring parameters.
2. Replace parameter groups with the new object at all call sites.
3. Move behavior that operates solely on the grouped data into the new class.

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class TemperatureRange:
    min: float
    max: float

    def contains(self, value: float) -> bool:
        return self.min <= value <= self.max


def readings_outside_range(readings, temp_range: TemperatureRange):
    return [r for r in readings if not temp_range.contains(r.temp)]


def alert_outside_range(readings, temp_range: TemperatureRange):
    for r in readings_outside_range(readings, temp_range):
        send_alert(r)
~~~

---

## SM-3: Preserve Whole Object

### ❌ BEFORE

Multiple fields are extracted from an object and passed as separate arguments.

~~~python
def is_within_plan(plan, low: float, high: float) -> bool:
    return plan.min <= low and plan.max >= high


temp_range = station.readings
is_within_plan(plan, temp_range.low, temp_range.high)
~~~

### ✅ AFTER

Mechanical steps:
1. Change the method signature to accept the whole object.
2. Update the method body to pull needed values from the object.
3. Update all call sites to pass the object instead of extracted fields.

~~~python
def is_within_plan(plan, readings) -> bool:
    return plan.min <= readings.low and plan.max >= readings.high


is_within_plan(plan, station.readings)
~~~

### ▶ EDGE CASE

Do not pass the whole object if it would create an unwanted dependency between the called method and the object's class. If only one or two stable fields are needed and the object is from a different layer (e.g., HTTP request), extracting fields may preserve better separation of concerns.
