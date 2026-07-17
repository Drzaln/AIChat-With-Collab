# 🎨 Design System: Luminous Tech-Pop

## 🌟 Overview
**Luminous Tech-Pop** is a *light-mode* design system built to make a positive, friendly, and energetic first impression. It pairs clean *whitespace* with bright accent colors (Indigo, Hot Pink, Cyan) to create enthusiasm without sacrificing professionalism.

Well suited for modern SaaS products, gamified analytics dashboards, or productivity tools.

> ⚠️ **Implementation note:** the current AIChat-With-Collab app ships with a different, already-implemented theme — a dark "glassmorphism" palette (`--bg-primary: #0a0a0f`, indigo/purple/pink accent gradient, etc. in `public/styles.css`). This document describes the *Luminous Tech-Pop* light-mode system as a separate design reference, not what's currently live in the app. If the goal is to eventually reskin the app to match this doc, the dark-theme tokens in `styles.css` would need to be swapped for the ones below. The new **Character Search** component in this update is specified using this doc's light-mode tokens for consistency with the rest of the system — the version actually shipped in the app's code uses the app's existing dark tokens instead (see `public/styles.css`, `.sidebar-search*` rules) so it matches everything else already on screen.

---

## 🎨 Color Palette Reference

The table below lists each color's role, hex code, and usage guidance in the UI.

| Role / Variable Name | Hex Code | Visual | Usage Guidelines & Notes |
| :--- | :--- | :--- | :--- |
| **Base Background** | `#F8FAFC` | ⬜ Ice White | Main page background. Gives an open, spacious, clean feel. |
| **Surface / Cards** | `#FFFFFF` | ⚪ Pure White | Background for cards, modals, or panels, to stand out from the base background. |
| **Primary Action** | `#6366F1` | 🟣 Vibrant Indigo | Main button (CTA) and active-link color. Reads as technically capable while staying dynamic. |
| **Primary Hover** | `#4F46E5` | 🔵 Deep Indigo | Darker version of Primary Action, used for hover / pressed / active states. |
| **Energy Accent** | `#EC4899` | 🩷 Hot Pink | High-energy accent. Use sparingly — for "New" badges, notifications, or special icons. |
| **Fresh Accent** | `#06B6D4` | 🩵 Bright Cyan | Complementary color for secondary elements, charts, or icon backgrounds. Balances the pink. |
| **Text Primary** | `#0F172A` | ⚫ Deep Slate | Main text color (headings & body copy). A blue-black that's easier to read than pure black. |
| **Text Muted** | `#64748B` | 🔘 Slate Gray | Secondary text, card descriptions, input placeholders, or metadata (dates, categories). |

---

## 💻 Implementation (CSS Variables)

Use the CSS variables below in your main stylesheet (e.g. `style.css` or `global.css`) so the palette is applied consistently across the project.

```css
:root {
  /* Backgrounds */
  --bg-base: #F8FAFC;
  --surface: #FFFFFF;

  /* Brand & Accents */
  --primary: #6366F1;
  --primary-hover: #4F46E5;
  --accent-energy: #EC4899;
  --accent-fresh: #06B6D4;

  /* Typography */
  --text-main: #0F172A;
  --text-muted: #64748B;

  /* Utilities (Optional - Shadows) */
  --shadow-card: 0 20px 40px rgba(15, 23, 42, 0.08);
  --shadow-button: 0 10px 25px rgba(99, 102, 241, 0.4);
}
```

---

## 🔍 Character Search

**Why:** as a user's character library grows, scrolling a long unfiltered list to find one character stops scaling. This component lets users filter the sidebar character list by name as they type — no page reload, no extra screen.

### Anatomy
1. **Search field** — icon-left text input, full width of its container.
2. **Search icon** — a static magnifying-glass glyph, left-aligned inside the field, non-interactive.
3. **Clear ("×") button** — right-aligned inside the field; only visible once the user has typed something; resets the query and refocuses the field.
4. **Result list** — the existing character list, filtered live as the user types.
5. **Empty state** — a centered message shown when the query matches nothing, distinct from the "you have no characters yet" empty state.

### Behavior
- Matching is **case-insensitive substring match on character name only** (not personality/bio), so results stay predictable as the list grows.
- Filtering happens instantly on every keystroke — the list is already loaded client-side, so no debounce or loading state is needed.
- The active/selected character stays visually marked (border + glow) even while filtered, if it's part of the visible results.
- Clearing the query (via the "×" button or deleting all text) restores the full, unfiltered list.
- Creating or editing a character automatically clears any active search, so the result is guaranteed to be visible.

### States & Tokens (Luminous Tech-Pop)

| State | Border | Background | Notes |
| :--- | :--- | :--- | :--- |
| Default | 1px `--text-muted` at 20% opacity | `--surface` | Search icon in `--text-muted`. |
| Focus | 1px `--primary` | `--surface` | Add `box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15)` (primary at low opacity) as a focus ring. |
| Filled (has query) | Same as focus/default | `--surface` | Clear button fades in, colored `--text-muted`, hovers to `--text-main`. |
| No results | — | — | Centered `--text-muted` copy, e.g. "No characters match your search," inside the list area where cards would normally render. |

```css
.character-search {
  position: relative;
  margin: 0 14px 10px;
}
.character-search-input {
  width: 100%;
  padding: 9px 32px;
  background: var(--surface);
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.85rem;
}
.character-search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}
.character-search-input::placeholder {
  color: var(--text-muted);
}
```

### Accessibility
- The input needs a real placeholder ("Search characters…") and, ideally, a visually-hidden `<label>` for screen readers.
- The clear button needs a `title`/`aria-label` ("Clear search"), not just an icon.
- Minimum touch target for the clear button: 24×24px hit area on top of a smaller visual glyph is acceptable; below that, tap accuracy suffers on mobile.

---

## 📱 Responsive / Multi-Platform Guidelines

The whole app — search included — needs to hold up across three rough device classes. Breakpoints below match what's already used elsewhere in the app's stylesheet (`768px`), extended with a tablet/desktop split for anything that needs finer control.

| Breakpoint | Range | Sidebar / Character list & search behavior |
| :--- | :--- | :--- |
| **Mobile** | `< 768px` | Sidebar (and the search bar inside it) becomes a full-height off-canvas drawer, toggled by a hamburger button, sliding in over the chat view rather than sitting beside it. Search input and touch targets should be comfortably tappable (≥ 40px effective height). |
| **Tablet** | `768px – 1023px` | Sidebar is docked (not an overlay) but can still be collapsed by the user to reclaim width for the chat view; search bar keeps the same layout as desktop. Verify the character list doesn't feel cramped at the narrow end of this range. |
| **Desktop** | `≥ 1024px` | Sidebar is docked at a fixed width (300px in the current implementation); search bar and list have the most breathing room. Hover states (border highlight, clear-button hover) are meaningful here since a pointer is assumed. |

### General rules
- Never rely on `:hover` alone to reveal functionality that's needed to operate the component (e.g. the clear button should show based on "has text," not on hover, since touch devices don't hover).
- Text in the character list (name, filtered result count if shown) must truncate with ellipsis rather than wrap or overflow at narrow widths.
- Use `100dvh` rather than `100vh` for full-height containers so mobile browser chrome (address bar show/hide) doesn't clip content — already the convention used elsewhere in this app.
- Test the empty/no-results state at each breakpoint; short messages that look fine on desktop can wrap awkwardly in a narrow mobile drawer.

### Manual test checklist
- [ ] Typing in the search field filters the list with no visible lag on a mid-range mobile device.
- [ ] Clear button appears only once text is entered, and correctly restores the full list.
- [ ] No-match state renders legibly at 320px width (smallest common mobile viewport).
- [ ] Sidebar drawer (mobile) still opens/closes correctly with an active search query.
- [ ] Search state doesn't leak between characters/chats in a confusing way (e.g. switching characters shouldn't silently clear an intentional search).
