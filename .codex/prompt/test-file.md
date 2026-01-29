# React Functional Component (TypeScript)

This guide explains how to create a **simple React functional component** using **TypeScript**. It focuses on the core concepts you’ll use most often: props, typing, and rendering JSX.

---

## What is a React Functional Component?

A functional component is a plain JavaScript/TypeScript function that:
- Accepts **props** as input
- Returns **JSX** (the UI)
- Has no required class or lifecycle boilerplate

With TypeScript, we explicitly type the props to catch errors early and improve editor autocomplete.

---

## Basic Structure

A React functional component in TypeScript usually has:
1. A **props type or interface**
2. A **function** that uses those props
3. An **export** so it can be used elsewhere

---

## Example: Simple Greeting Component

Below is a minimal example of a typed React functional component.

~~~ts
import React from "react";

type GreetingProps = {
  name: string;
  isLoggedIn?: boolean;
};

export const Greeting: React.FC<GreetingProps> = ({
  name,
  isLoggedIn = false,
}) => {
  return (
    <div>
      {isLoggedIn ? (
        <p>Hello, {name}! Welcome back 👋</p>
      ) : (
        <p>Hello, {name}! Please log in.</p>
      )}
    </div>
  );
};
~~~

---

## Key Points Explained

### Props typing
- `GreetingProps` defines exactly what data the component expects.
- `isLoggedIn?: boolean` is optional (`?`), so it doesn’t have to be passed.

### Default values
- `isLoggedIn = false` sets a default if the prop is not provided.

### `React.FC`
- `React.FC<GreetingProps>` tells TypeScript:
  - This is a React component
  - It accepts `GreetingProps`
- Using `React.FC` is optional, but common in many codebases.

---

## Using the Component

Here’s how you might use this component elsewhere in your app:

~~~tsx
<Greeting name="Alex" isLoggedIn />
<Greeting name="Sam" />
~~~

---

## When to Use This Pattern

Use a typed functional component when:
- You want strong type safety
- The component is reusable
- You want clear documentation through types

This pattern scales well from tiny UI elements to large application features.

---

## Summary

- Functional components are simple functions that return JSX
- TypeScript adds safety and clarity with typed props
- Start small, keep components focused, and rely on types to guide usage