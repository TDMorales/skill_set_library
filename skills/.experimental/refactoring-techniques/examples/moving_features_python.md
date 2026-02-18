# Moving Features between Objects – Python Examples

Before/after examples showing the mechanical steps for each technique.

---

## MF-1: Move Method

### ❌ BEFORE

`overdraft_charge` uses `Account`'s data but lives on `AccountType`.

~~~python
class AccountType:
    def __init__(self, is_premium: bool):
        self.is_premium = is_premium


class Account:
    def __init__(self, account_type: AccountType, days_overdrawn: int):
        self.type = account_type
        self.days_overdrawn = days_overdrawn

    def overdraft_charge(self) -> float:
        if self.type.is_premium:
            return 10 + (self.days_overdrawn - 7) * 0.85 if self.days_overdrawn > 7 else 10
        return self.days_overdrawn * 1.75
~~~

### ✅ AFTER

~~~python
class AccountType:
    def __init__(self, is_premium: bool):
        self.is_premium = is_premium

    def overdraft_charge(self, days_overdrawn: int) -> float:
        if self.is_premium:
            return 10 + (days_overdrawn - 7) * 0.85 if days_overdrawn > 7 else 10
        return days_overdrawn * 1.75


class Account:
    def __init__(self, account_type: AccountType, days_overdrawn: int):
        self.type = account_type
        self.days_overdrawn = days_overdrawn

    def overdraft_charge(self) -> float:
        return self.type.overdraft_charge(self.days_overdrawn)
~~~

---

## MF-2: Move Field

### ❌ BEFORE

`interest_rate` belongs with `AccountType`, not `Account`.

~~~python
class Account:
    def __init__(self, interest_rate: float, account_type: AccountType):
        self.interest_rate = interest_rate
        self.type = account_type
~~~

### ✅ AFTER

~~~python
class AccountType:
    def __init__(self, is_premium: bool, interest_rate: float):
        self.is_premium = is_premium
        self.interest_rate = interest_rate


class Account:
    def __init__(self, account_type: AccountType):
        self.type = account_type

    @property
    def interest_rate(self) -> float:
        return self.type.interest_rate
~~~

---

## MF-3: Extract Class

### ❌ BEFORE

~~~python
class Person:
    def __init__(self, name: str, area_code: str, number: str):
        self.name = name
        self.area_code = area_code
        self.number = number

    def phone(self) -> str:
        return f"({self.area_code}) {self.number}"
~~~

### ✅ AFTER

~~~python
class PhoneNumber:
    def __init__(self, area_code: str, number: str):
        self.area_code = area_code
        self.number = number

    def __str__(self) -> str:
        return f"({self.area_code}) {self.number}"


class Person:
    def __init__(self, name: str, phone: PhoneNumber):
        self.name = name
        self.phone = phone
~~~

---

## MF-4: Inline Class

### ❌ BEFORE

`PhoneNumber` does too little to justify its existence.

~~~python
class PhoneNumber:
    def __init__(self, number: str):
        self.number = number


class Person:
    def __init__(self, name: str, phone: PhoneNumber):
        self.name = name
        self.phone = phone

    def phone_number(self) -> str:
        return self.phone.number
~~~

### ✅ AFTER

~~~python
class Person:
    def __init__(self, name: str, phone_number: str):
        self.name = name
        self.phone_number = phone_number
~~~

---

## MF-5: Hide Delegate

### ❌ BEFORE

Client navigates through `person` to reach `department`.

~~~python
manager = person.department.manager
~~~

### ✅ AFTER

~~~python
class Person:
    @property
    def manager(self) -> str:
        return self.department.manager


manager = person.manager
~~~

---

## MF-6: Remove Middle Man

### ❌ BEFORE

`Person` just delegates to `Department` for everything.

~~~python
class Person:
    def __init__(self, department: Department):
        self._department = department

    @property
    def manager(self):
        return self._department.manager

    @property
    def budget(self):
        return self._department.budget

    @property
    def headcount(self):
        return self._department.headcount
~~~

### ✅ AFTER

~~~python
class Person:
    def __init__(self, department: Department):
        self.department = department


manager = person.department.manager
~~~

---

## MF-7: Introduce Foreign Method / Local Extension

### ❌ BEFORE

Date arithmetic is scattered because the library lacks `next_business_day`.

~~~python
next_day = start + timedelta(days=1)
while next_day.weekday() >= 5:
    next_day += timedelta(days=1)
~~~

### ✅ AFTER (Foreign Method)

~~~python
def next_business_day(start: date) -> date:
    next_day = start + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day


result = next_business_day(start)
~~~

### ▶ EDGE CASE (Local Extension — when multiple methods are needed)

~~~python
class BusinessDate(date):
    def next_business_day(self) -> "BusinessDate":
        next_day = self + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        return BusinessDate(next_day.year, next_day.month, next_day.day)

    def business_days_until(self, end: date) -> int:
        count = 0
        current = self
        while current < end:
            if current.weekday() < 5:
                count += 1
            current += timedelta(days=1)
        return count
~~~
