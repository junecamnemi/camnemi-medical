#!/usr/bin/env python3
"""
Re-sync this mirror from the upstream Readdy site (https://mfbcbt.readdy.co).

The upstream build is content-hashed, so a stale mirror is detectable by
comparing the asset filenames its shell references. This script:

  1. fetches the upstream index.html and discovers the bundle + CSS names
  2. downloads the bundle, the CSS and every image the bundle references
     into assets/img/   (both public.readdy.ai AND static.readdy.ai CDNs)
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

# Any image served off a Readdy CDN. The origin uses two hosts:
#   public.readdy.ai/{ai/img_res,gen_page}/file
#   static.readdy.ai/image/<project-id>/file
# Matching only public.readdy.ai silently leaves the hero background
# (static.readdy.ai) pointing at Readdy — match both.
CDN_RE = re.compile(
    r"https://((?:public|static)\.readdy\.ai)/([A-Za-z0-9_./-]+?\.(?:webp|jpg|jpeg|png|svg|gif))"
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
    with urllib.request.urlopen(req, timeout=90) as r:
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

    # ---- images: download every CDN image the bundle references ----
    # filename -> full remote URL; guard against two remote files sharing a basename
    sources: dict[str, str] = {}
    for host, path in CDN_RE.findall(js):
        url = f"https://{host}/{path}"
        fname = path.rsplit("/", 1)[1]
        if fname in sources and sources[fname] != url:
            stem, _, ext = fname.rpartition(".")
            fname = f"{stem}-{abs(hash(host + path)) % 0xFFFF:04x}.{ext}"
        sources[fname] = url
    print(f"  images referenced: {len(sources)}")
    for fname, url in sorted(sources.items()):
        blob = get(url)
        (img_dir / fname).write_bytes(blob)  # binary: no newline translation
        print(f"    {len(blob):>9,}  {fname}")
    for old in sorted(p for p in img_dir.iterdir() if p.is_file()):
        if old.name not in sources:
            print(f"  removing unreferenced {old.name}")
            old.unlink()

    # ---- patch the bundle: localize images + runtime basename ----
    def localize(m: re.Match) -> str:
        return "assets/img/" + m.group(2).rsplit("/", 1)[1]

    patched = CDN_RE.sub(localize, js)
    if count := patched.count("basename:`/`"):
        if count != 1:
            sys.exit(f'expected one `basename:`/`` in the bundle, found {count}')
        patched = patched.replace("basename:`/`", "basename:window.__APP_BASE__||`/`")
    elif "basename:window.__APP_BASE__||`/`" not in patched:
        sys.exit("basename patch target not found in the bundle")
    leftover = CDN_RE.findall(patched)
    if leftover:
        sys.exit(f"unlocalized CDN references remain: {leftover}")

    # ---- write everything (binary); drop bundles from previous builds ----
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
