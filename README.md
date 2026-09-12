# Camnemi × Asan Medical Center — Website

A static mirror of the Camnemi / Asan Medical Center platform
(`https://mfbcbt.readdy.co`), published to GitHub Pages.

## Pages

| Route | Content |
|-------|---------|
| `/` | Home — Asan Medical Center overview, health check-up programs, plastic surgery, medical specialties, inquiry form |
| `/about-asan` | About Asan Medical Center |
| `/plastic-surgery` | Plastic surgery procedures |

The app is a client-routed single page application, so deep links such as
`/about-asan` are served through `404.html` (a byte-identical copy of
`index.html`), which boots the SPA at that route.

## Structure

```
index.html                  entry point (SPA shell)
404.html                    copy of index.html — deep-link fallback for GitHub Pages
assets/index-*.js           application bundle (single chunk, self-contained)
assets/index-*.css          application stylesheet
assets/img/*                18 images localized from the original CDN
```

All imagery was downloaded from the original host and is served from
`assets/img/` so the mirror has no third-party asset dependency.
Fonts (Google Fonts) and icon fonts (Font Awesome, Remixicon) still load
from their public CDNs, and the YouTube embeds are unchanged.

## Local preview

```bash
# from the parent directory, so the subpath matches GitHub Pages
python -m http.server 8080
# open http://localhost:8080/camnemi-medical/
```

## Notes

* The bundle's router basename is resolved at runtime from the URL, so the
  same files work at a domain root or under the `/camnemi-medical/` project
  subpath.
* The original readdy.ai telemetry/event-reporting script was removed. The
  inquiry form still posts to the original endpoint, and the Readdy footer
  badge is retained — replace both if this mirror becomes the production site.
