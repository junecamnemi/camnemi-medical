#!/usr/bin/env python3
"""
Re-sync this mirror from the upstream Readdy site (https://mfbcbt.readdy.co).

The upstream build is content-hashed, so a stale mirror is detectable by
comparing the asset filenames its shell references. This script:

  1. fetches the upstream index.html and discovers the bundle + CSS names
  2. downloads the bundle, the CSS and every image the bundle references
     into assets/img/
  3. rewrites the bundle so images load locally and the router basename is
     resolved at runtime (so it works under a GitHub Pages project subpath)
  4. regenerates index.html/404.html from the upstream shell with the
     telemetry script stripped and asset paths made relative
  5. deletes assets that are no longer referenced

Run from the repo root:   python tools/sync_from_origin.py

IMPORTANT: everything is written in BINARY mode. On Windows, a text-mode
write translates "\\n" -> "\\r\\n" *inside the minified JS string literals*,
which silently corrupts the bundle. Never "fix" that back to write_text().
"""

import re
import sys
import urllib.request
from pathlib import Path

ORIGIN = "https://mfbcbt.readdy.co/"
IMG_RE = re.compile(
    r"https://public\.readdy\.ai/(ai/img_res|gen_page)/([A-Za-z0-9_.\-]+\.(?:webp|jpg|jpeg|png|svg))"
)
ASSET_RE = re.compile(r'(?:src|href)="/assets/(index-[A-Za-z0-9_-]+\.(?:js|css))"')

BASE_SCRIPT = """    <script>
      /*
       * Resolve the SPA base path at runtime.
       * The original build (Readdy) assumed it was served from a domain root.
       * This lets the identical bundle run either at a root or under a
       * GitHub Pages project subpath (e.g. /camnemi-medical/).
       */
      (function () {
        var p = location.pathname;
        var m = p.match(/^(\\/[^\\/]+\\/)/);
        window.__APP_BASE__ = m ? m[1] : (p.slice(-1) === "/" ? p : p + "/");
        var b = document.createElement("base");
        b.href = window.__APP_BASE__;
        document.head.insertBefore(b, document.head.firstChild);
      })();
    </script>
"""


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mirror-sync"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def build_shell(upstream_html: str, js: str, css: str) -> str:
    html = upstream_html

    # 1. relative asset paths (the origin serves from a domain root)
    html = html.replace(f'src="/assets/{js}"', f'src="assets/{js}"')
    html = html.replace(f'href="/assets/{css}"', f'href="assets/{css}"')

    # 2. drop the broken favicon link (/vite.svg returns the SPA shell upstream)
    html = "\n".join(l for l in html.split("\n") if '<link rel="icon"' not in l)

    # 3. strip Readdy telemetry: version meta + config script + reporting script
    html = re.sub(
        r'\s*<meta name="readdy-project-version".*?event-reporting\.min\.js"></script>',
        "",
        html,
        flags=re.DOTALL,
    )

    # 4. inject the runtime base resolver right after the charset meta
    html = re.sub(
        r'(<meta charset="UTF-8" />\s*)',
        lambda m: m.group(1) + BASE_SCRIPT,
        html,
        count=1,
    )
    return html


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    assets = root / "assets"
    img_dir = assets / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    print(f"fetching {ORIGIN}")
    upstream_html = get(ORIGIN).decode("utf-8")
    names = ASSET_RE.findall(upstream_html)
    js_names = [n for n in names if n.endswith(".js")]
    css_names = [n for n in names if n.endswith(".css")]
    if len(js_names) != 1 or len(css_names) != 1:
        sys.exit(f"unexpected upstream shell: js={js_names} css={css_names}")
    js_name, css_name = js_names[0], css_names[0]
    print(f"  bundle={js_name}  stylesheet={css_name}")

    js = get(ORIGIN + "assets/" + js_name).decode("utf-8")
    css = get(ORIGIN + "assets/" + css_name)

    # images: download every one the bundle references, keep the set exact
    wanted = {m.group(2): m.group(1) for m in IMG_RE.finditer(js)}   # filename -> cdn path
    print(f"  images referenced: {len(wanted)}")
    for fname, prefix in sorted(wanted.items()):
        blob = get(f"https://public.readdy.ai/{prefix}/{fname}")
        (img_dir / fname).write_bytes(blob)  # binary: no newline translation
    for old in list(img_dir.iterdir()):
        if old.name not in wanted:
            print(f"  removing unreferenced {old.name}")
            old.unlink()

    # patch the bundle: localize images + runtime basename
    patched = IMG_RE.sub(lambda m: "assets/img/" + m.group(2), js)
    count = patched.count("basename:`/`")
    if count != 1:
        sys.exit(f'expected exactly one `basename:`/`` in the bundle, found {count}')
    patched = patched.replace("basename:`/`", "basename:window.__APP_BASE__||`/`")

    # write everything in binary; drop bundles from previous builds
    for old in list(assets.glob("index-*.js")) + list(assets.glob("index-*.css")):
        if old.name not in (js_name, css_name):
            print(f"  removing superseded {old.name}")
            old.unlink()
    (assets / js_name).write_bytes(patched.encode("utf-8"))
    (assets / css_name).write_bytes(css)

    shell = build_shell(upstream_html, js_name, css_name)
    for name in ("index.html", "404.html"):
        (root / name).write_bytes(shell.encode("utf-8"))

    print("\nre-synced. review with `git diff --stat`, then commit + push.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
