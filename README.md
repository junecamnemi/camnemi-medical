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
| `assets/img/*` | 13 images from `public.readdy.ai` |

Rebranded to "Camnemi Korea" and collapsed to a single page (route `/`)
in the build this mirror tracks — the earlier `/about-asan` and
`/plastic-surgery` routes no longer exist upstream.

## Changes made to the original

1. **Images localized.** All 13 images were downloaded from
   `public.readdy.ai` and rewritten to `assets/img/`, so the mirror has no
   dependency on Readdy's CDN.
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

If those filenames differ from the ones in this repo, the origin has been
rebuilt: fetch the new shell + bundle + CSS, re-run the image
localization and the `basename` patch, swap the files, then commit.
