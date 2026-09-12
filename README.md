# Camnemi Korea × Asan Medical Center — website

**Live:** https://junecamnemi.github.io/camnemi-medical/

A hand-written static site: one HTML page, one stylesheet, one small script.
No framework, no build step, no third-party platform.

```bash
python -m http.server 8080     # then: http://localhost:8080/
```

## Files

```
index.html                  the whole site (semantic sections + anchors)
404.html                    branded not-found page
assets/css/style.css        design system + all styling
assets/js/main.js           nav, scroll spy, reveal, inquiry form
assets/img/                 logo mark, hero, 7 procedure photos, doctor, og card
```

## Provenance

The content (packages, prices, procedure copy, stats, specialties) was
transcribed out of the site's previous Readdy/Vite build. That build is gone:
the minified bundle, its stylesheet, its watermark/logo assets, its sync tool
and every Readdy reference have been **deleted**. Nothing on this site calls
Readdy, PostHog or any other third party at runtime.

Still loaded from public CDNs (not Readdy):

* Google Fonts — **Playfair Display** (display) + **Noto Sans KR** (body)
* Remixicon 4.5 — the `ri-*` icon font

Everything else, including all imagery, is self-hosted.

## Design system

The brand palette is carried over from the client's existing tokens so this
reads as the same brand — but the layout, hierarchy and components are new.

| Token | Value | Use |
|---|---|---|
| `--primary` | `oklch(.455 .145 262)` | indigo — links, CTAs, prices |
| `--accent` | `oklch(.468 .052 150)` | green — eyebrows, ticks, ranks |
| `--brand-grad` | indigo → green, 135° | brand gradient |
| `--font-display` | Playfair Display | headings, numerals |
| `--font-body` | Noto Sans KR | body, UI |

## What changed vs. the previous build

**Design**
* Real heading hierarchy (`h1` → `h4`) and semantic landmarks; the previous
  build was a flat pile of `div`s.
* Sticky header with a logo mark + wordmark and an "Official Agency of AMC"
  strip; scroll-spy nav that marks the current section.
* Package cards: the duplicated male/female screening lists that bloated every
  card are now a collapsed `<details>`, plus a **comparison table** so the 8
  packages can actually be compared.
* Accessible by default: skip link, visible focus rings, `aria-*` on the
  nav/form/status, `prefers-reduced-motion` respected, screen-reader captions
  on the table.

**Performance**
* Hero image 1,279 KB → **129 KB** (`hero-asan.webp`).
* Logo 385 KB PNG → **10 KB** mark; favicon 6 KB.
* Below-the-fold images lazy-loaded; only the hero is eager/high-priority.
* Removed a 394 KB JS bundle + 31 KB CSS of framework runtime.

**Correctness**
* A **1200×630 social card** (`og-cover.jpg`) was added — previously
  `twitter:card=summary_large_image` had no image at all, so every share
  rendered blank.
* The broken `tel:+855****9079` click-to-call link (masked upstream) is now a
  working `tel:+855969909079`.
* The masked Telegram entry is now a real `https://t.me/` link.

## The inquiry form

There is no backend. The form composes a `mailto:` to
**medical@camnemi.com** — subject and body pre-filled from the fields — and
opens the visitor's own email app. Nothing is sent to any third party, and no
data leaves the browser.

Client-side it validates name and email, marks invalid fields with
`aria-invalid`, and reports status through an `aria-live` region. Without JS
the form still works as a plain HTML form fallback isn't available, so the
page also lists the email address and phone number as direct links.

To upgrade it later, replace the submit handler in `assets/js/main.js` with a
POST to a real endpoint (Apps Script or Supabase) — the markup and validation
already support it.
