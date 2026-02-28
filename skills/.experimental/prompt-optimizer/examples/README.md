# Examples

Concrete examples showing how the prompt-optimizer gathers context and produces
specs in both output formats. These examples follow the AGENTS.md Section 1A
requirement: broken, correct, and explicit examples for each format.

---

## Output Format Index

### Creation Spec Examples
- [Correct: UI Component Creation](#correct-creation-spec)
- [Broken: Missing gathering phase](#broken-creation-spec)
- [Explicit: Porting from existing codebase](#explicit-creation-spec)

### Task Spec Examples
- [Correct: Performance Optimization](#correct-task-spec)
- [Broken: Vague acceptance criteria](#broken-task-spec)
- [Explicit: Optimization with baseline](#explicit-task-spec)

---

## Gathering Phase Example (applies to both formats)

This shows the conversational gathering flow before any spec is produced.

**User input:**
> "I need a grid component for image collections"

**Agent response (Step 2 — format selection):**

> That sounds like you're looking to build something new. Which format fits
> your need?
>
> 1. **Creation Spec** — A full implementation blueprint for building new
>    components, screens, or features (includes per-item Create/From/Props/Renders
>    blocks, build order, and file maps).
> 2. **Task Spec** — A lighter action plan for non-creation work like refactors,
>    performance fixes, investigations, or migrations.

**User:** "Creation spec"

**Agent response (Step 3 — gap-driven gathering):**

> Got it. Let me understand what you need. A few questions:
>
> 1. What does your project's component structure look like — do you have an
>    existing atoms/molecules/organisms pattern or similar?
> 2. Do you have a reference image or design for the grid layouts you want?
> 3. Is this a new component from scratch, or are you porting/adapting something
>    from an existing file?

**User answers, agent asks follow-ups as needed, then...**

**Agent response (Step 4 — confirm before producing):**

> Here's what I'll produce. Let me know if anything is off:
>
> - **Format:** Creation Spec
> - **Components:** SectionHeader (molecule) + MediaGrid (organism)
> - **MediaGrid variants:** uniform (equal-size grid) and featured (mixed-size)
> - **Depends on:** existing Thumbnail atom
> - **Includes:** Storybook stories for each component
> - **Scope:** Display-only (no upload, no edit mode)
>
> Ready to produce the spec?

---

<a name="correct-creation-spec"></a>
## Correct: Creation Spec — UI Components

This is a compliant Creation Spec. It was produced after a complete gathering
phase where the user confirmed the summary.

```markdown
# SectionHeader + MediaGrid Components

## Context
The user wants a Grid component to display image collections in two layout
variants (uniform equal-size grid and a featured/mixed-size layout), plus a
reusable section header with title + action link. Reference images show
"Album Grid" cards with a header row ("Album 1" + "View All" link) and image
grids below. The project uses an atoms/molecules/organisms component structure
with Tailwind CSS and Storybook.

---

## Phase 1 — New Components

### 1. SectionHeader (molecule)
- **Create:** `src/components/molecules/SectionHeader.tsx`
- **From:** new
- **Props/Params:**
  - `title: string` — heading text
  - `action?: ReactNode` — right-side slot (Link, Button, etc.)
  - `size?: "sm" | "md" | "lg"` — title text size (default `"md"`)
  - `className?: string`
- **Renders:** Horizontal bar with title left, optional action slot right.
  `<div class="flex items-center justify-between gap-4">` wrapper.
  `<h3>` for title with `font-semibold text-text-primary` + size class.
  Action wrapped in `<div class="shrink-0">` to prevent squeezing.
  No padding/border — Card's header slot handles that.
- **Token/Pattern Swaps:** none
- **Barrel Export:** `export * from "./SectionHeader"` in `molecules/index.ts`

### 2. MediaGrid (organism)
- **Create:** `src/components/organisms/MediaGrid.tsx`
- **From:** new (references existing GalleryGrid.tsx for grid pattern)
- **Props/Params:**
  - `items: MediaGridItem[]` — `{ id, src, alt }`
  - `variant?: "uniform" | "featured"` (default `"uniform"`)
  - `columns?: 2 | 3 | 4` (default `3`, uniform only)
  - `gap?: "none" | "sm" | "md" | "lg"` (default `"sm"`)
  - `radius?: "none" | "sm" | "md" | "lg" | "xl"` (default `"lg"`)
  - `onItemClick?: (item, index) => void`
  - `className?: string`
- **Renders:** Display-only image grid using Thumbnail atom.
  **Uniform variant:** CSS grid `grid-cols-{2|3|4}`, each cell is
  `<Thumbnail ratio="1:1" radius={radius} />`.
  **Featured variant:** `grid grid-cols-2 grid-rows-2`. First item
  `row-span-2` (large), items 2-3 fill right column. If `items.length > 3`:
  `+N` overlay on last visible tile. If `items.length < 3`: fall back to
  uniform.
- **Token/Pattern Swaps:** none
- **Barrel Export:** `export * from "./MediaGrid"` in `organisms/index.ts`

---

## Phase 2 — Stories

### 3. SectionHeader Stories
- **Create:** `src/components/molecules/SectionHeader.stories.tsx`
- **From:** new
- **Props/Params:** n/a (Storybook stories)
- **Renders:** Stories: Default, WithAction (Link), Small, Large, AllVariants

### 4. MediaGrid Stories
- **Create:** `src/components/organisms/MediaGrid.stories.tsx`
- **From:** new
- **Props/Params:** n/a (Storybook stories)
- **Renders:** Stories: Uniform (3-col), TwoColumns, FourColumns, Featured,
  FeaturedWithOverflow, AlbumCardUniform (Card + SectionHeader + MediaGrid
  composition), AlbumCardFeatured (same for featured variant)

---

## Implementation Order
1. `SectionHeader.tsx` (no dependencies beyond existing atoms)
2. `SectionHeader.stories.tsx`
3. `MediaGrid.tsx` (depends on existing Thumbnail atom)
4. `MediaGrid.stories.tsx` (composes Card + SectionHeader + MediaGrid)

---

## Key Files

| File | Change |
|---|---|
| `src/components/molecules/SectionHeader.tsx` | Create |
| `src/components/molecules/SectionHeader.stories.tsx` | Create |
| `src/components/organisms/MediaGrid.tsx` | Create |
| `src/components/organisms/MediaGrid.stories.tsx` | Create |
| `src/components/molecules/index.ts` | Modify (barrel export) |
| `src/components/organisms/index.ts` | Modify (barrel export) |

## Existing Components/Hooks Reused (no modifications needed)

| Component/Hook | Location | Used For |
|---|---|---|
| `Thumbnail` | `src/components/atoms/Thumbnail.tsx` | Image rendering in grid cells |
| `Link` | `src/components/molecules/Link.tsx` | Action slot in SectionHeader |
| `Card` | `src/components/organisms/Card.tsx` | Container in composed story demos |
| `GalleryGrid` | `src/components/organisms/GalleryGrid.tsx` | Pattern reference for grid classes |

---

## Verification
1. Run `pnpm storybook` and confirm "Molecules/SectionHeader" appears
2. Confirm "Organisms/MediaGrid" appears with uniform + featured variants
3. AlbumCard composed stories match reference images (header + grid)
4. Light/dark theme toggle works on all stories
5. Controls (variant, columns, gap, radius) update correctly in Storybook
```

### Why this is correct:
- Complete gathering phase preceded the output (user confirmed summary)
- Context section gives substantive background
- Every item has Create, From, Props/Params, and Renders
- Implementation Order respects dependency chain
- Key Files table is complete
- Verification is concrete and testable

---

<a name="broken-creation-spec"></a>
## Broken: Creation Spec — Missing Gathering Phase

This example violates the skill's procedure by skipping directly to output.

**User input:**
> "I need a grid component"

**Agent output (WRONG — skipped gathering):**

```markdown
# Grid Component

## Context
User wants a grid.

## Phase 1

### 1. Grid (component)
- **Create:** `src/Grid.tsx`
- **From:** new
- **Props/Params:** items, columns
- **Renders:** A grid of items.

## Implementation Order
1. Grid

## Verification
- It works.
```

### What's broken:
- **No format selection** — agent didn't ask which output format
- **No gathering** — agent didn't ask about current state, variants, design refs
- **No confirmation** — agent didn't summarize before producing
- **Context is a placeholder** — "User wants a grid" is not substantive
- **Props are untyped** — "items, columns" has no types or descriptions
- **Renders is vague** — "A grid of items" doesn't describe structure or behavior
- **No Key Files table** — missing required section
- **No Existing Components table** — missing required section
- **Verification is untestable** — "It works" is not concrete

---

<a name="explicit-creation-spec"></a>
## Explicit: Creation Spec — Porting from Existing Codebase

This example covers the edge case where items are being ported from another
codebase with token/pattern swaps required.

```markdown
# DatePicker + TabBar — Ported from Darkwood

## Context
The project is migrating UI components from an older codebase ("Darkwood") into
a new shared `packages/ui` package. Components must be adapted to use the new
theming system (`useUIThemeTokens()` instead of `useTheme()`) and follow the
new file naming convention (`*.native.tsx`). The Darkwood originals are
available as reference but must not be copied verbatim — token swaps and
pattern alignment are required.

---

## Phase 1 — Ported Components

### 1. DatePicker (molecule)
- **Create:** `packages/ui/src/molecules/DatePicker/DatePicker.native.tsx` + `index.ts`
- **From:** `native/components/molecules/DatePicker.tsx` (Darkwood)
- **Props/Params:**
  - `value?: Date | null` — currently selected date
  - `onChange?: (date: Date) => void` — callback on date selection
  - `min?: Date` — earliest selectable date
  - `max?: Date` — latest selectable date
  - `label?: string` — field label
  - `error?: string` — error message
  - `hint?: string` — helper text
  - `placeholder?: string` — placeholder when no date selected
  - `disabled?: boolean`
- **Renders:** Pressable trigger showing formatted date → opens RN Modal with
  bottom-sheet style calendar grid. Month navigation with prev/next. 7-column
  day grid. Selected day highlight. Uses pure JS Date (no external lib).
- **Token/Pattern Swaps:**
  - `useTheme()` → `useUIThemeTokens()`
  - `colors.state.error` → `tokens.semantic.state.error`
  - `colors.interactive.primary` → `tokens.semantic.interactive.primary`
- **Barrel Export:** `export * from "./DatePicker"` in `molecules/index.ts`

### 2. TabBar (organism)
- **Create:** `packages/ui/src/organisms/TabBar/TabBar.native.tsx` + `index.ts`
- **From:** `native/components/organisms/TabBar.tsx` (Darkwood)
- **Props/Params:**
  - `items: { id: string; label?: string; icon?: ReactNode; disabled?: boolean }[]`
  - `activeId: string` — currently active tab
  - `onChange: (id: string) => void`
  - `variant?: "label-only" | "icon-label" | "icon-only"` (default `"label-only"`)
  - `style?: ViewStyle`
- **Renders:** Row of Pressable tabs with animated sliding underline indicator
  (RN `Animated` API, spring: damping 30, stiffness 300). Each tab measured
  via `onLayout` for indicator positioning. `flex: 1` per tab for equal
  distribution.
- **Token/Pattern Swaps:**
  - Replace `semanticColors[theme]` lookup with `useUIThemeTokens()`
  - Remove `theme` prop entirely
- **Barrel Export:** `export * from "./TabBar"` in `organisms/index.ts`

---

## Implementation Order
1. DatePicker (no deps beyond existing atoms)
2. TabBar (no deps beyond existing atoms)
3. Barrel exports for both

---

## Key Files

| File | Change |
|---|---|
| `packages/ui/src/molecules/DatePicker/DatePicker.native.tsx` | Create |
| `packages/ui/src/molecules/DatePicker/index.ts` | Create |
| `packages/ui/src/organisms/TabBar/TabBar.native.tsx` | Create |
| `packages/ui/src/organisms/TabBar/index.ts` | Create |
| `packages/ui/src/molecules/index.ts` | Modify (barrel export) |
| `packages/ui/src/organisms/index.ts` | Modify (barrel export) |

## Existing Components/Hooks Reused (no modifications needed)

| Component/Hook | Location | Used For |
|---|---|---|
| `useUIThemeTokens` | `packages/ui/src/hooks/` | Theme token access (replaces Darkwood `useTheme`) |

---

## Verification
1. Run `npm run mobile:start -- -c` from repo root
2. DatePicker opens modal on press, calendar grid renders, date selection works
3. TabBar renders with sliding underline animation on tab switch
4. Both components use `useUIThemeTokens()` — no references to old `useTheme()`
5. Barrel exports resolve correctly from `packages/ui`
```

### Why this is an edge case worth documenting:
- The "From" field references a specific file in another codebase
- Token/Pattern Swaps are non-trivial and must be listed per-item
- The agent must understand that "porting" ≠ "copying" — swaps are required
- Verification includes checking that old patterns are NOT present

---

<a name="correct-task-spec"></a>
## Correct: Task Spec — Code Refactoring

**User input:**
> "Our API response handler is a mess, can you help clean it up?"

**After gathering phase, user confirms summary. Agent produces:**

```markdown
# Task Spec: Refactor API Response Handler

## Goal
Extract the monolithic API response handler into focused, single-responsibility
functions to improve testability and reduce coupling.

## Context
The current `handleApiResponse()` function in `src/api/handler.ts` is ~280 lines
and handles success parsing, error mapping, retry logic, and cache invalidation
in a single function. The user wants to break it apart but keep the public API
surface unchanged. Existing tests cover the happy path but not error branches.
The project uses TypeScript 5.3 and has no runtime dependency constraints.

## Constraints
- **Languages/frameworks/versions:** TypeScript 5.3
- **Do not change:** Public API surface of `handleApiResponse()` — callers
  must not need updates
- **Performance/latency targets:** No regression in response handling time
- **Security/compliance constraints:** Error mapping must not leak internal
  details to API consumers

## Execution Plan
1. Add test coverage for error branches and retry paths before refactoring
2. Extract success parsing into `parseSuccessResponse()`
3. Extract error mapping into `mapErrorResponse()`
4. Extract retry logic into `withRetry()` wrapper
5. Extract cache invalidation into `invalidateOnMutation()`
6. Update `handleApiResponse()` to compose the extracted functions
7. Run full test suite to confirm behavioral equivalence

## Acceptance Criteria
- All existing tests pass without modification
- New tests cover error branches and retry paths
- No function exceeds 50 lines
- `handleApiResponse()` is a composition of the extracted functions
- No caller changes required
```

---

<a name="broken-task-spec"></a>
## Broken: Task Spec — Vague Acceptance Criteria

**User input:**
> "Make the API faster"

**Agent output (WRONG — skipped gathering, vague criteria):**

```markdown
# Task Spec: Optimize API

## Goal
Make the API faster.

## Context
API is slow.

## Constraints
- None specified.

## Execution Plan
1. Profile the API
2. Fix slow parts

## Acceptance Criteria
- API is faster
```

### What's broken:
- **No gathering phase** — didn't ask what "faster" means, which endpoints, etc.
- **No format selection** — didn't ask the user
- **Context is a placeholder** — "API is slow" gives an agent nothing to work with
- **Execution Plan is vague** — "Fix slow parts" is not actionable
- **Acceptance Criteria is untestable** — "API is faster" has no measurement
- **Missing optimization sections** — user said "faster" so Baseline Measurement,
  Proposed Optimization, and Verification sections are required but absent

---

<a name="explicit-task-spec"></a>
## Explicit: Task Spec — Optimization with Baseline

This covers the edge case where the user mentions performance, triggering the
required optimization sections.

```markdown
# Task Spec: Optimize Dashboard Load Time

## Goal
Reduce the initial load time of the analytics dashboard from ~4.2s to under 2s.

## Context
The analytics dashboard at `src/pages/Dashboard.tsx` fetches 6 API endpoints
sequentially on mount. The user measured 4.2s average load time on staging
(Chrome DevTools, throttled to Fast 3G). The backend endpoints themselves
respond in <200ms each — the bottleneck is sequential fetching and a large
initial bundle (~1.8MB uncompressed). The project uses React 18, React Query,
and Webpack 5.

## Constraints
- **Languages/frameworks/versions:** React 18, React Query 4, Webpack 5
- **Do not change:** API endpoint contracts or backend logic
- **Performance/latency targets:** < 2s initial load on Fast 3G
- **Security/compliance constraints:** No lazy-loading of auth-gated components
  before authentication completes

## Baseline Measurement
- Current average load: 4.2s (Chrome DevTools, Fast 3G throttle, staging)
- Bundle size: 1.8MB uncompressed, 420KB gzipped
- Network waterfall: 6 sequential API calls, ~200ms each = ~1.2s blocked
- Largest component: `ChartPanel` at ~600KB before tree-shaking

## Proposed Optimization
1. Parallelize the 6 API calls using `Promise.all` via React Query
2. Code-split `ChartPanel` and `DataTable` with `React.lazy`
3. Add Webpack bundle analysis and remove unused lodash imports

## Execution Plan
1. Add performance measurement script (Lighthouse CI or DevTools trace)
2. Record baseline metrics
3. Refactor API calls from sequential to parallel via React Query
4. Code-split ChartPanel and DataTable with React.lazy + Suspense
5. Run `webpack-bundle-analyzer`, remove unused lodash methods
6. Record post-optimization metrics
7. Compare against baseline

## Verification
- Run Lighthouse CI on staging before and after
- Confirm initial load < 2s on Fast 3G throttle
- Confirm bundle size reduction (target: < 300KB gzipped)
- Confirm no functional regression (all existing Cypress tests pass)

## Acceptance Criteria
- Dashboard loads in < 2s on Fast 3G (Lighthouse CI measurement)
- Bundle size < 300KB gzipped
- All existing tests pass
- No changes to API contracts
```

### Why this is an edge case worth documenting:
- User said "optimize" → triggers mandatory Baseline/Proposed/Verification sections
- Baseline includes specific measurements, not guesses
- Proposed Optimization is concrete, not "make it faster"
- Verification ties back to the baseline with the same measurement method
