# अख़बार वाले — Frontend Application

> Modern editorial digital newspaper frontend for **अख़बार वाले**, built with **Next.js 16 (Turbopack)**, **React 19**, and **Tailwind CSS v4**.

---

## 🎨 Design & Editorial Typography System

The frontend implements a broadsheet typography and design-token system:

- **Typography Stack**:
  - **Inter**: Primary UI font for navigation (14px), buttons (14px), filter labels (12px), news card headlines (19–20px bold), and executive summaries (14–15px).
  - **Newsreader Serif**: Broadsheet serif font for hero headings (44–48px) and article detail modal headlines (36–40px).
  - **Noto Sans Devanagari**: Weight 800 for the Hindi brand title **अख़बार वाले**.
- **Colour & Theme Tokens**:
  - **Light Theme**: Warm off-white background (`#F7F7F5`), crisp white cards (`#FFFFFF`), secondary panel surfaces (`#F1F1EF`), high-contrast text (`#191919`), muted metadata (`#707070`), and editorial red accents (`#D92D35`).
  - **Dark Theme**: Charcoal background (`#111318`), elevated dark surface (`#191C23`), secondary surface (`#20242D`), soft white text (`#F5F5F5`), muted grey (`#A1A1AA`), and night red accents (`#F05252`).
  - Automatic system detection with manual toggle and `localStorage` persistence (`akhbar_theme`).

---

## ⚡ Fluidity & Zero-CLS Architecture

- **`scrollbar-gutter: stable`**: Prevents horizontal layout jumping when modals open or close on Windows.
- **Fixed Top Progress Line**: Indeterminate progress shimmer fixed beneath the 68px header eliminates layout shifts during background refilling or filtering.
- **GPU-Accelerated Card Transitions**: Hardware-accelerated hover elevation (`transform-gpu will-change-transform`) with Apple-style spring easing (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Smooth Image Fade-In**: Smooth opacity transition upon image load prevents harsh popping.
- **Custom Floating Pill Scrollbar**: Rounded floating scrollbar with transparent borders.

---

## 📁 Key Components

| Component | Description |
| :--- | :--- |
| **`components/Header.tsx`** | 68px sticky navigation bar with Hindi branding, active tabs (`Trending`, `Explore`, `Search`), live batch rotation counter `(50/50)`, theme toggle, and auth controls. |
| **`components/HeroStats.tsx`** | Understated broadsheet hero with dynamic uppercase dateline, Newsreader heading, and live article counter. |
| **`components/FilterBar.tsx`** | Compact 2-row panel with search input, live count, and 3 equal-width filter dropdowns (`REGION`, `ORIGINAL LANGUAGE`, `CATEGORY`) with custom SVG chevrons. |
| **`components/ArticleCard.tsx`** | 16:9 news card with GPU-accelerated elevation, source/language badges, category kicker, line-clamped typography, and quick controls. |
| **`components/ArticleReaderModal.tsx`** | 850px reading modal with Web Speech TTS, dynamic expandable original headline, central executive summary (Inter 17px, line-height 1.75), word count, source footer, and context tags. |
| **`components/AuthModal.tsx`** | Sign-in and registration dialog with JWT authentication. |
| **`components/ProfileDrawer.tsx`** | Reader profile slide-over drawer with preferences. |

---

## 🚀 Development & Build

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run automated component & multilingual tests
node test_modal.mjs
node test_interactive_modal.mjs

# Build production bundle with Turbopack
npm run build
```

---

## 📜 License
MIT License.
