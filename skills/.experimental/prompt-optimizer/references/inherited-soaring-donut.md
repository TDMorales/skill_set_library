# Plan: SectionHeader + MediaGrid Components

## Context
The user wants a Grid component to display image collections in two layout variants (uniform equal-size grid and a featured/mixed-size layout), plus a reusable section header with title + action link. Reference images show "Album Grid" cards with a header row ("Album 1" + "View All" link) and image grids below.

## New Files (4)

| File | Type |
|---|---|
| `src/components/molecules/SectionHeader.tsx` | Component |
| `src/components/molecules/SectionHeader.stories.tsx` | Stories |
| `src/components/organisms/MediaGrid.tsx` | Component |
| `src/components/organisms/MediaGrid.stories.tsx` | Stories |

## 1. SectionHeader (Molecule)

**Path:** `src/components/molecules/SectionHeader.tsx`

Horizontal bar with title left, optional action slot right. Follows molecule pattern: `forwardRef`, extends `HTMLAttributes<HTMLDivElement>`, `displayName`.

**Props:**
- `title: string` — heading text
- `action?: ReactNode` — right-side slot (Link, Button, etc.)
- `size?: "sm" | "md" | "lg"` — title text size (default `"md"`)
- `className?: string`

**Structure:**
- `<div class="flex items-center justify-between gap-4">` wrapper
- `<h3>` for title with `font-semibold text-text-primary` + size class from Record map
- Action wrapped in `<div class="shrink-0">` to prevent squeezing
- No padding/border — Card's header slot handles that

**Stories:** Default, WithAction (Link), Small, Large, AllVariants

## 2. MediaGrid (Organism)

**Path:** `src/components/organisms/MediaGrid.tsx`

Display-only image grid using Thumbnail atom. Two layout variants via CSS Grid.

**Props:**
- `items: MediaGridItem[]` — `{ id, src, alt }`
- `variant?: "uniform" | "featured"` (default `"uniform"`)
- `columns?: 2 | 3 | 4` (default `3`, uniform only)
- `gap?: "none" | "sm" | "md" | "lg"` (default `"sm"`)
- `radius?: "none" | "sm" | "md" | "lg" | "xl"` (default `"lg"`)
- `onItemClick?: (item, index) => void`
- `className?: string`

**Uniform variant** (Album Grid 1):
```
grid grid-cols-{2|3|4} gap-{0|1|2|3}
```
Each cell: `<Thumbnail ratio="1:1" radius={radius} />`

**Featured variant** (Album Grid 2):
```
grid grid-cols-2 grid-rows-2 gap-{0|1|2|3}
```
- First item: `row-span-2` — large image spanning full height
- Items 2-3: fill right column cells
- If `items.length > 3`: show `+N` overlay on last visible tile
- If `items.length < 3`: fall back to uniform layout

**Featured image height:** The featured Thumbnail gets `className="h-full"` to fill the row-span-2 cell. If Tailwind's aspect ratio conflicts, override with `!aspect-auto`.

**Stories:** Uniform (3-col), TwoColumns, FourColumns, Featured, FeaturedWithOverflow, AlbumCardUniform (Card + SectionHeader + MediaGrid composition matching reference), AlbumCardFeatured (same for featured variant)

## Implementation Order
1. `SectionHeader.tsx` (no new dependencies)
2. `SectionHeader.stories.tsx`
3. `MediaGrid.tsx` (depends on existing Thumbnail atom)
4. `MediaGrid.stories.tsx` (composes Card + SectionHeader + MediaGrid)

## Key Files Referenced
- `src/components/atoms/Thumbnail.tsx` — image rendering (ratio, radius, width, className)
- `src/components/molecules/Link.tsx` — molecule pattern reference, used in SectionHeader action slot
- `src/components/organisms/Card.tsx` — container with `header` ReactNode slot for composed demos
- `src/components/organisms/GalleryGrid.tsx` — grid pattern reference (columnsClass Record map, gap classes)

## Verification
- Run `pnpm storybook` and confirm:
  - "Molecules/SectionHeader" appears with all story variants
  - "Organisms/MediaGrid" appears with uniform + featured variants
  - AlbumCard composed stories match reference images (header + grid)
  - Light/dark theme toggle works on all stories
  - Controls (variant, columns, gap, radius) update correctly
