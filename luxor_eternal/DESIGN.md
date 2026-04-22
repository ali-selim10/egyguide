# Design System Specification: High-End Editorial Tourism

## 1. Overview & Creative North Star: "The Modern Curator"
This design system moves away from the utilitarian, "utility-first" density of traditional travel platforms. Instead, it adopts the persona of **The Modern Curator**. We are not building a directory; we are crafting a digital gallery of experiences.

The aesthetic foundation is **High-End Editorial**. We break the "template" look by utilizing intentional asymmetry, expansive negative space, and a sophisticated layering of tonal surfaces. By overlapping high-resolution imagery with elevated typography and "glass" containers, we create a sense of depth that mirrors the architectural layering of Egypt itself—where the ancient and the contemporary coexist.

**The Creative North Star:**
*   **Asymmetry over Grids:** Don’t just align to a 12-column grid; let elements breathe and overlap.
*   **Depth over Borders:** Use light and tone to define space, never hard lines.
*   **Atmospheric Immersion:** Use the color palette to evoke the warmth of the Sahara and the depth of the Nile.

---

## 2. Colors
Our palette is a dialogue between the warmth of the desert and the cool authority of the river. 

### The Color Tokens
*   **Primary (`#00556f` / `primary`):** The deep Nile. Use for high-impact brand moments.
*   **Primary Container (`#1C6E8C` / `primary_container`):** The active Nile. Use for primary action buttons and header backgrounds.
*   **Secondary (`#685d46` / `secondary`):** Earthy sand. Used for secondary UI elements and grounding the interface.
*   **Tertiary (`#755b00` / `tertiary`):** Liquid Gold. Reserved exclusively for ratings, highlights, and "Prestige" status indicators.
*   **Background (`#fbf9f5` / `background`):** A warm, off-white "fine paper" base that prevents the eye-strain of pure white.

### The "No-Line" Rule
**Borders are prohibited for sectioning.** To separate a hero section from a discovery grid, shift the background from `surface` to `surface-container-low`. Use the color tokens to create "zones" rather than "boxes." 

### Surface Hierarchy & Nesting
Treat the UI as physical layers. Use the following hierarchy to create depth without shadows:
1.  **Base Layer:** `surface` (The foundation).
2.  **Sectioning:** `surface-container-low` (Subtle shifts for content grouping).
3.  **Interactive Cards:** `surface-container-lowest` (The brightest white to draw the eye).
4.  **Floating Elements:** `surface-variant` with 80% opacity and a 16px backdrop-blur (The "Glass" effect).

### Signature Textures
For main CTAs, do not use flat hex codes. Apply a subtle linear gradient (135°) from `primary` to `primary_container`. This provides a "jewel-toned" finish that feels premium and bespoke.

---

## 3. Typography
We utilize a pairing of **Plus Jakarta Sans** for expressive moments and **Inter** for functional clarity.

*   **Display (Plus Jakarta Sans):** Large, confident, and slightly tracked-in (-2%). Used for destination names and evocative headlines.
*   **Headline (Plus Jakarta Sans):** Medium weight. Conveys authority and editorial "voice."
*   **Body & Labels (Inter):** High legibility. We use `body-md` (0.875rem) as our standard to maintain a sophisticated, airy feel.

**Editorial Hierarchy:**
*   **Display-LG (3.5rem):** Reserved for "Hero" moments. Overlap this over images to break the container.
*   **Title-LG (1.375rem):** Used for card titles. Always paired with `secondary` color for a softer look than pure black.

---

## 4. Elevation & Depth
In this system, elevation is a feeling, not a technical attribute.

### The Layering Principle
Instead of shadows, use **Tonal Layering**. 
*   A `surface-container-lowest` card sitting on a `surface-container-low` background creates a "natural lift" that feels architectural.

### Ambient Shadows
Where floating is required (e.g., a "Book Now" floating bar), use the **Ambient Shadow**:
*   `box-shadow: 0 20px 40px rgba(27, 28, 26, 0.05);` 
*   The shadow must be tinted with the `on-surface` color to ensure it looks like a natural occlusion of light rather than a gray smudge.

### The "Ghost Border" Fallback
If contrast is legally required for accessibility:
*   Use `outline-variant` at **15% opacity**. It should be felt, not seen.

---

## 5. Components

### Buttons
*   **Primary:** Gradient from `primary` to `primary_container`. Roundedness: `md` (0.75rem). No border.
*   **Secondary:** Ghost style. No background. `outline` token at 20% opacity. Text in `primary`.
*   **Tertiary:** `surface-container-highest` background with `on-surface` text. For low-emphasis utility.

### Cards (The "Gallery" Card)
*   **Structure:** No divider lines.
*   **Image:** 16:9 ratio with `xl` (1.5rem) top-corner rounding.
*   **Content:** Use 24px padding (`spacing-6`). 
*   **Separation:** Vertical whitespace only. Use 8px (`spacing-2`) between title and location, and 16px (`spacing-4`) between location and price.

### Elegant Forms
*   **Input Fields:** Use `surface-container-low` as the fill. On focus, transition the background to `surface-container-lowest` and add a 1px "Ghost Border" using the `primary` token at 40%.
*   **Floating Labels:** Labels should use `label-md` and be positioned above the field, never inside as placeholder text.

### Egyptian Discovery Chips
*   **Style:** Pill-shaped (`full` roundedness).
*   **State:** Unselected chips use `surface-variant`. Selected chips use `primary` with `on-primary` text.

---

## 6. Do's and Don'ts

### Do
*   **DO** use oversized imagery that bleeds off the edge of the screen or container.
*   **DO** use "Glassmorphism" for navigation bars. `surface` at 70% opacity + `backdrop-filter: blur(12px)`.
*   **DO** allow text to overlap images if contrast ratios (via a 20% black scrim) are maintained.

### Don't
*   **DON'T** use 1px solid borders to separate sections. Use background color shifts.
*   **DON'T** use high-contrast black (`#000000`). Always use `on-surface` (`#1b1c1a`) for a softer, premium feel.
*   **DON'T** use standard "Drop Shadows." If a shadow is needed, make it large, soft, and nearly invisible.
*   **DON'T** use "divider lines" in lists or cards. Let the whitespace do the work.