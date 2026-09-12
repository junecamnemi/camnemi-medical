# Camnemi Korea × Asan Medical Center — Website

A static mirror of the Camnemi Korea / Asan Medical Center platform
(`https://mfbcbt.readdy.co`), published to GitHub Pages.

**Live:** https://junecamnemi.github.io/camnemi-medical/

## Source

The original is a Readdy-built Vite/React single-page app. Its whole
front-end is three files plus imagery:

| File in this repo | Origin |
|---|---|
| `index.html` | `/` (shell, modified — see below) |
| `assets/index-6zuHScgl.js` | `/assets/index-6zuHScgl.js` |
| `assets/index-gS4WCt3f.css` | `/assets/index-gS4WCt3f.css` |
| `assets/img/*` | 14 images from the Readdy CDNs (`public.readdy.ai` and `static.readdy.ai`) |

Rebranded to "Camnemi Korea" and collapsed to a single page (route `/`)
in the build this mirror tracks — the earlier `/about-asan` and
`/plastic-surgery` routes no longer exist upstream.

## Changes made to the original

1. **Images localized.** All 14 images were downloaded from the Readdy
   CDNs and rewritten to `assets/img/`, so the mirror has no dependency on
   Readdy for imagery. Note the origin uses **two** hosts — `public.readdy.ai`
   *and* `static.readdy.ai` (the 1.3 MB hero background) — so a pattern that
   only matches the first will silently leave the hero remote.
2. **Runtime base path.** The original bundle hardcoded
   `basename: "/"`, which breaks under a GitHub Pages project subpath.
   The bundle now reads `basename: window.__APP_BASE__ || "/"`, and
   `index.html` sets `window.__APP_BASE__` (plus a `<base>` tag) from the
   current URL before the bundle loads. The same files therefore work at a
   domain root *or* under `/camnemi-medical/`.
3. **Telemetry removed.** Readdy's `event-reporting.min.js`,
   `EventReportingConfig` and the `readdy-project-version` meta tag were
   dropped.
4. **`404.html`** — a copy of `index.html`, so any stray path still boots
   the app (GitHub Pages serves it for 404s under this project path).
5. **Broken favicon link removed** — `/vite.svg` returns the SPA shell on
   the origin, not an icon.

Fonts (Google Fonts) and icon fonts (Font Awesome, Remixicon) still load
from their public CDNs; YouTube embeds are untouched.

## Still Readdy-dependent

* The inquiry form posts to `readdy.ai/api/form/daieo3roh653ivfvoch0`.
* The Readdy footer badge/watermark is retained.

Repoint both if this mirror ever becomes the production site.

## Local preview

```bash
# run from the PARENT directory so the subpath matches GitHub Pages
python -m http.server 8080
# http://localhost:8080/camnemi-medical/
```

## Re-syncing when the upstream site changes

The upstream bundle is content-hashed, so a stale mirror is detectable:

```bash
curl -s https://mfbcbt.readdy.co/ | grep -oE 'assets/index-[A-Za-z0-9_-]+\.(js|css)'
```

If those differ from the filenames in this repo, the origin was rebuilt.
Re-sync in one step:

```bash
python tools/sync_from_origin.py   # then: git diff --stat, commit, push
```

That script re-does steps 1–4 above from scratch: it discovers the new
asset names, downloads the new bundle/CSS/images, re-applies the image
localization and basename patch, regenerates `index.html` + `404.html`
from the upstream shell, and deletes superseded files.

> **Windows pitfall:** the script writes everything in *binary* mode on
> purpose. A text-mode write translates `\n` → `\r\n` **inside the
> minified JS string literals**, silently corrupting the bundle (it slipped
> through once, adding 10 stray CR bytes). Keep it binary; `.gitattributes`
> pins LF in the repo.

