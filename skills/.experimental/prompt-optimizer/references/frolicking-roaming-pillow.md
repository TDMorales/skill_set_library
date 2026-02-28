# Edit Mode Integration — Phase 1

## Context

The Profile Page layout is complete (read-only). All edit mode infrastructure is wired but dormant in `MemorialHomeScreen.js` (`useEditMode`, `canManage`, `beginEditMode`, `runWithEditGuard`, `EditModeToolbar`, hero image upload flow). This plan activates edit mode for 4 sections: **Hero Image**, **Profile Header**, **Biography**, and **Albums**. Testimonies, Highlights, and Family edit modes are deferred to Phase 2.

The user indicated tab-filtered uploads for Albums are correct: All=photos+videos, Photos=photos only, Videos=videos only.

---

## Phase 1 — New UI Components (packages/ui)

### 1. Blockquote (atom)
- **Create:** `packages/ui/src/atoms/Blockquote/Blockquote.native.tsx` + `index.ts`
- **From:** Darkwood `native/components/atoms/Blockquote.tsx`
- **Props:** `children: ReactNode, style?`
- **Renders:** View with left border accent (`tokens.semantic.interactive.primary`), light brand background with 10% opacity, italic text. Border on left side only (borderLeftWidth). Top-right/bottom-right border radius.
- **Barrel:** Add `export * from "./Blockquote"` to `atoms/index.ts`

### 2. DatePicker (molecule)
- **Create:** `packages/ui/src/molecules/DatePicker/DatePicker.native.tsx` + `index.ts`
- **From:** Darkwood `native/components/molecules/DatePicker.tsx`
- **Props:** `value?: Date|null, onChange?, min?, max?, label?, error?, hint?, placeholder?, disabled?`
- **Renders:** Pressable trigger showing formatted date → opens RN Modal with bottom-sheet style calendar grid. Month navigation with prev/next. 7-column day grid. Selected day highlight. Uses pure JS Date (no external lib).
- **Token swap:** `useTheme()` → `useUIThemeTokens()`, `colors.state.error` → `tokens.semantic.state.error`, `colors.interactive.primary` → `tokens.semantic.interactive.primary`, etc.
- **Barrel:** Add `export * from "./DatePicker"` to `molecules/index.ts`

### 3. TabBar (organism)
- **Create:** `packages/ui/src/organisms/TabBar/TabBar.native.tsx` + `index.ts`
- **From:** Darkwood `native/components/organisms/TabBar.tsx`
- **Props:** `items[]{id, label?, icon?, disabled?}, activeId, onChange, variant?("label-only"|"icon-label"|"icon-only"), style?`
- **Renders:** Row of Pressable tabs with animated sliding underline indicator (RN `Animated` API, spring: damping 30, stiffness 300). Each tab measured via `onLayout` for indicator positioning. `flex: 1` per tab for equal distribution.
- **Token swap:** Replace `semanticColors[theme]` lookup with `useUIThemeTokens()`. Remove `theme` prop.
- **Barrel:** Add `export * from "./TabBar"` to `organisms/index.ts`

### 4. GalleryGrid (organism)
- **Create:** `packages/ui/src/organisms/GalleryGrid/GalleryGrid.native.tsx` + `index.ts`
- **From:** Darkwood `native/components/organisms/GalleryGrid.tsx`
- **Props:** `items[]{id, src, alt, type?("photo"|"video"), duration?}, columns?(2|3|4), onItemPress?, maxSlots?, onUpload?, loading?, emptyTitle?, emptyMessage?, style?`
- **Renders:** FlatList with `numColumns`. Each cell uses `Thumbnail` (1:1 ratio). When `onUpload` provided and `items.length < maxSlots`: appends dashed-border UploadSlot cells with "+" icon. Empty state with title+message. Loading skeleton tiles.
- **UploadSlot:** Inline Pressable with dashed border, "+" Text, "Upload" label. Uses `tokens.semantic.border.subtle` for border, `tokens.semantic.interactive.primary` on press.
- **Barrel:** Add `export * from "./GalleryGrid"` to `organisms/index.ts`

---

## Phase 2 — MemorialHomeScreen Edit Affordances

**Modify:** `apps/mobile/src/features/memorial/screens/MemorialHomeScreen.js`

### 2a. Hero Image — Pencil overlay on ImageCarousel
- Wrap the `<ImageCarousel>` in a `<View style={{ position: "relative" }}>` container
- When `canManage && isEditMode`: render an `<IconButton>` with `glyph={<Entypo name="pencil" />}` positioned absolute top-right (matching Figma mockup), `variant="filled"`, `size="sm"`, `rounded`
- `onPress` → calls existing `openHeroImagePicker()` which opens the Camera/Library modal
- The existing hero image upload flow handles everything else (permission check, validation, upload via `useHeroMediaUpload`)

### 2b. Profile Header — Pencil overlay on Surface + ProfileEditModal
- When `canManage && isEditMode`: render `<IconButton>` positioned absolute bottom-right of the profile header `<Surface>`, `variant="filled"`, `size="sm"`
- `onPress` → sets `isProfileEditModalVisible` state to true
- **New state:** `isProfileEditModalVisible` (boolean)
- **ProfileEditModal** (inline in MemorialHomeScreen or extracted to a component):
  - Uses existing `<Modal>` component
  - Title: "Edit Profile"
  - Body: `<Input label="Name" value={draftName} maxLength={160} />` + `<DatePicker label="Date of Birth" value={draftBirthDate} max={new Date()} />` + `<DatePicker label="Date of Death" value={draftDeathDate} min={draftBirthDate} max={new Date()} />`
  - Footer: Cancel + Save buttons
  - Save → calls `updateMemorialMutation` for title + `updateMemorialPersonMutation` for dates (reusing existing `handleSaveEdits` pattern or a focused save function)
  - Local state for draft name, draftBirthDate, draftDeathDate initialized from `memorial.name`, `primaryPersonBirthDate`, `primaryPersonDeathDate`

### 2c. Section Title Edit Icons (Biography, Albums)
- Modify `<SectionHeader>` usage for Biography and Albums to include an inline pencil icon when `canManage && isEditMode`
- Use the SectionHeader's existing `action` slot: when in edit mode, prepend an `<IconButton glyph={<Entypo name="pencil" />} variant="filled" size="sm" />` before the existing `<Link>` action
- Or: wrap SectionHeader in `<View style={{ flexDirection: "row", alignItems: "center" }}>` and add the icon inline after the title
- **Biography pencil** → `navigation.navigate(ROUTES.MEMORIAL_BIOGRAPHY, { memorial, editMode: isEditMode })`
- **Albums pencil** → `navigation.navigate(ROUTES.MEMORIAL_GALLERY, { memorial, editMode: true })`

### 2d. EditModeToolbar
- The existing `EditModeToolbar` component is already imported. Render it in the screen when `isEditMode` is true, docked above the BottomNavBar.
- `onSave` → `handleSaveEdits()` (existing)
- `onCancel` → `handleCancelEditMode()` (existing)
- `isSaving` → `isSavingMemorialProfile` (existing)
- `safeAreaBottom` → `bottomInset`

---

## Phase 3 — New Screens

### 5. BiographyScreen
- **Create:** `apps/mobile/src/features/memorial/screens/BiographyScreen.js`
- **Design ref:** `docs/ui_design/ios_design/ui_issues/BiographyScreen.jpg`
- **Layout:**
  - `NavigationHeader` with `showBack`, `onBack={() => navigation.goBack()}`, back label "Profile"
  - **Read-only mode** (editMode param falsy): `<Blockquote>` showing quote + `<Text>` showing full bio. Purely display.
  - **Edit mode** (editMode param truthy, navigated from MemorialHomeScreen while in edit mode):
    - Quote section: `<TextArea>` replacing the Blockquote, editable, recommended max 300 chars with character count
    - Bio section: `<TextArea>` for editing bio text, character count shown, no hard DB limit
    - Save/Cancel buttons at bottom (or use EditModeToolbar pattern)
- **Data flow:**
  - Receives `memorial` via route params
  - Uses `useUpdateMemorialMutation` to save subtitle changes
  - Uses `useUpdateMemorialPersonMutation` to save bio changes
  - On save success → `navigation.goBack()` with updated data
- **Note:** DB has no character limits on subtitle or bio, but recommend showing count for UX guidance (300 for quote)

### 6. Rewrite GalleryScreen → Albums Screen
- **Modify:** `apps/mobile/src/features/memorial/screens/GalleryScreen.js` (complete rewrite)
- **Design ref:** `docs/ui_design/ios_design/ui_issues/AlbumsScreen.jpg`
- **Layout:**
  - `NavigationHeader` with `showBack`, `onBack={() => navigation.goBack()}`, back label "Profile"
  - `<Text variant="sectionTitle">` "Albums" centered
  - `<TabBar>` with 3 tabs: `[{ id: "all", label: "All" }, { id: "photo", label: "Photos" }, { id: "video", label: "Videos" }]`, variant: `"label-only"`
  - `<GalleryGrid>` with `columns={3}`, items filtered by active tab
  - When `canManage` and `editMode` param is true: `onUpload` callback on GalleryGrid, `maxSlots` set to a reasonable number (e.g., 30)
- **Tab-filtered upload behavior:**
  - "All" tab → `ImagePicker` with `mediaTypes: ["images", "videos"]`
  - "Photos" tab → `ImagePicker` with `mediaTypes: ["images"]`
  - "Videos" tab → `ImagePicker` with `mediaTypes: ["videos"]`
- **Data flow:**
  - Receives `memorial` + optional `editMode` + optional `typeFilter` via route params
  - Gallery data from `memorial.gallery` (currently dummy picsum URLs; will wire to real API later)
  - Upload flow: permission check → ImagePicker → validate (mime type, file size) → upload to Supabase storage (same pattern as hero image upload)

---

## Phase 4 — Route Registration

### routes.js
Add two new routes:
```
MEMORIAL_BIOGRAPHY: "MemorialBiography"
```
(Albums reuses existing `MEMORIAL_GALLERY`)

### MainNavigation.js
- Import `BiographyScreen`
- Add `<Stack.Screen name={ROUTES.MEMORIAL_BIOGRAPHY} component={BiographyScreen} options={{ headerShown: false }} />`
- GalleryScreen is already registered (just rewrite its implementation)

### ROUTE_MAP
Add entry for `MEMORIAL_BIOGRAPHY`

---

## Phase 5 — Barrel Export Updates

| File | Add |
|---|---|
| `packages/ui/src/atoms/index.ts` | `export * from "./Blockquote"` |
| `packages/ui/src/molecules/index.ts` | `export * from "./DatePicker"` |
| `packages/ui/src/organisms/index.ts` | `export * from "./TabBar"`, `export * from "./GalleryGrid"` |

---

## Build Order

1. **Blockquote** atom (no deps)
2. **DatePicker** molecule (no deps beyond existing atoms)
3. **TabBar** organism (no deps beyond existing atoms)
4. **GalleryGrid** organism (depends on Thumbnail atom — already exists)
5. **Barrel exports** for all new components
6. **BiographyScreen** (depends on Blockquote, TextArea, NavigationHeader)
7. **GalleryScreen rewrite** (depends on TabBar, GalleryGrid, NavigationHeader)
8. **Route registration** (routes.js + MainNavigation.js)
9. **MemorialHomeScreen edits** (pencil icons, ProfileEditModal, EditModeToolbar, navigation wiring)

---

## Key Files to Modify

| File | Change |
|---|---|
| `packages/ui/src/atoms/Blockquote/Blockquote.native.tsx` | Create |
| `packages/ui/src/molecules/DatePicker/DatePicker.native.tsx` | Create |
| `packages/ui/src/organisms/TabBar/TabBar.native.tsx` | Create |
| `packages/ui/src/organisms/GalleryGrid/GalleryGrid.native.tsx` | Create |
| `apps/mobile/src/features/memorial/screens/BiographyScreen.js` | Create |
| `apps/mobile/src/features/memorial/screens/GalleryScreen.js` | Rewrite |
| `apps/mobile/src/features/memorial/screens/MemorialHomeScreen.js` | Add edit affordances |
| `apps/mobile/src/app/navigation/routes.js` | Add MEMORIAL_BIOGRAPHY |
| `apps/mobile/src/app/navigation/MainNavigation.js` | Register BiographyScreen |
| `packages/ui/src/atoms/index.ts` | Barrel export |
| `packages/ui/src/molecules/index.ts` | Barrel export |
| `packages/ui/src/organisms/index.ts` | Barrel export |

## Existing Components/Hooks Reused (no modifications needed)

| Component/Hook | Location | Used For |
|---|---|---|
| `IconButton` | `packages/ui/src/molecules/IconButton/` | All pencil edit buttons |
| `Modal` | `packages/ui/src/molecules/Modal/` | Profile edit dialog |
| `Input` | `packages/ui/src/molecules/Input/` | Name field in profile modal |
| `TextArea` | `packages/ui/src/molecules/TextArea/` | Biography editing |
| `NavigationHeader` | `packages/ui/src/organisms/NavigationHeader/` | Back nav on new screens |
| `EditModeToolbar` | `packages/ui/src/organisms/EditModeToolbar/` | Save/Cancel bar |
| `Thumbnail` | `packages/ui/src/atoms/Thumbnail/` | GalleryGrid cells |
| `useEditMode` | `apps/mobile/.../hooks/useEditMode.js` | Edit state management |
| `useHeroMediaUpload` | `apps/mobile/.../hooks/useHeroMediaUpload.js` | Hero image upload |
| `useUpdateMemorialMutation` | `apps/mobile/.../api/` | Save memorial fields |
| `useUpdateMemorialPersonMutation` | `apps/mobile/.../api/` | Save person fields |
| `ImagePicker` | `expo-image-picker` | Photo/video selection |

---

## Verification

1. Run `npm run mobile:start -- -c` from repo root
2. Navigate to Memorial Home screen in iOS simulator
3. Enter edit mode via Settings drawer → "Edit Profile"
4. **Hero**: pencil icon appears top-right of carousel → tap opens Camera/Library modal
5. **Profile header**: pencil icon appears bottom-right of Surface card → tap opens edit modal with name + date pickers → save updates name/dates
6. **Biography**: pencil icon appears inline next to "Biography" title → tap navigates to BiographyScreen with back button "< Profile" → Blockquote at top, bio text below → edit fields when canManage
7. **Albums**: pencil icon appears inline next to "Albums" title → tap navigates to Albums screen → TabBar with All/Photos/Videos → 3-col grid → UploadSlot at end when editing → tap UploadSlot opens camera roll filtered by tab
8. Scroll down hides bottom nav, scroll up shows it (still works)
9. Save/Cancel via EditModeToolbar works
10. Settings drawer still opens
