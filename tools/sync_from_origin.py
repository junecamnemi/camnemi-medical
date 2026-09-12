#!/usr/bin/env python3
"""
Re-sync this mirror from the upstream Readdy site (https://mfbcbt.readdy.co)
and re-apply the local patches.

Upstream build is content-hashed, so a stale mirror is detectable by comparing
the asset filenames its shell references. This script:

  1. fetches the upstream index.html and discovers the bundle + CSS names
  2. downloads the bundle, CSS and every CDN image into assets/img/
     (both public.readdy.ai AND static.readdy.ai)
  3. applies the local patches (see PATCHES below)
  4. regenerates index.html/404.html from the upstream shell
  5. deletes assets no longer referenced

Run from the repo root:   python tools/sync_from_origin.py

Every patch asserts its anchor exists, so an upstream rebuild that moves code
fails LOUDLY here instead of silently shipping an unpatched mirror.

IMPORTANT: everything is written in BINARY mode. On Windows, a text-mode write
translates "\\n" -> "\\r\\n" *inside the minified JS string literals*, which
silently corrupts the bundle. Never "fix" that back to write_text().
"""

import re
import sys
import urllib.request
from pathlib import Path

ORIGIN = "https://mfbcbt.readdy.co/"
PROJECT_ID = "500e2a63-6f35-4da6-9d39-4897f76e46da"  # Readdy project id

# Any image off a Readdy CDN. The origin uses TWO hosts:
#   public.readdy.ai/{ai/img_res,gen_page}/file
#   static.readdy.ai/image/<project-id>/file
# Matching only public.readdy.ai silently leaves the hero background remote.
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

# --------------------------------------------------------------------------
# Literal patches: (description, exact source, replacement)
#
# P1  Readdy platform API + watermark + affiliate ad + PostHog — all in one shot.
#     `_()` fetches is_free; its result drives two renderers:
#       u(data): !watermarkEl && !data -> install watermark AND load PostHog
#       be():    data.is_free || !affiliate_enabled -> return (no ad)
#     Resolving {is_free:!0} makes u() take its "already installed" no-op branch
#     and makes be() bail immediately. Nothing renders, PostHog is never
#     requested, and no call is made to readdy.ai. Patching this one leaf is
#     safer than excising DOM builders, and it leaves React's own unrelated
#     `p()` untouched.
#
# P2  Belt-and-braces on the PostHog loader: even if some path reaches it, an
#     empty data: URL means the script "loads" to an empty module, onload finds
#     no window.posthog and resolves null -> capture calls no-op. No 3rd-party
#     request, no console error.
# --------------------------------------------------------------------------
LITERAL_PATCHES = [
    (
        "disable Readdy is_free / watermark / affiliate ad (and thus PostHog)",
        "function _(e){let t=`https://readdy.ai/api/public/user/is_free?projectId="
        "${encodeURIComponent(e)}`,n=g(),r=n.get(t);if(r)return r;"
        "let i=fetch(t).then(async e=>{if(!e.ok)return null;"
        "let t=await e.json();return t.code===`OK`?t.data:null}).catch(()=>null);"
        "return n.set(t,i),i}",
        "function _(e){return Promise.resolve({is_free:!0})}",
    ),
    (
        "route the inquiry form to a mailto: composer instead of Readdy's API",
        None,  # regex-driven, see REGEX_PATCHES
        None,
    ),
    (
        "success status message now describes the mail client flow",
        "Your inquiry has been received. We will get back to you shortly.",
        "Your email app is opening with your inquiry. Send it to reach medical@camnemi.com.",
    ),
    ("submit button label", "Submit Inquiry", "Send Inquiry by Email"),
    ("form heading label", "`Send an Inquiry`", "`Send an Inquiry by Email`"),
]

# Regex patches: (description, compiled pattern, replacement)
REGEX_PATCHES = [
    (
        "neutralise the PostHog script URL, key and host (loader is never"
        " invoked once is_free is stubbed; this makes that airtight)",
        re.compile(r"u=`https://cdn\.jsdelivr\.net/npm/posthog-js@[^`]+`"),
        "u=`data:text/javascript,`",
    ),
    (None, re.compile(r"l=`phc_[A-Za-z0-9]+`"), "l=``"),
    (None, re.compile(r"api_host:`https://[a-z.]*posthog\.com`"), "api_host:``"),
    (
        "swap the form's POST for a mailto: composer that still reports OK,"
        " so the existing success/reset/error handling is untouched",
        re.compile(
            r"let t=await fetch\(`https://readdy\.ai/api/form/[^`]+`,"
            r"\{method:`POST`,headers:\{\"Content-Type\":"
            r"`application/x-www-form-urlencoded`\},body:e\.toString\(\)\}\)"
        ),
        # `e` is the URLSearchParams built from the form just above this point.
        "let t=await (async()=>{"
        "let g=k=>e.get(k)||'';"
        "let b=['Name: '+g('name'),'Email: '+g('email'),'Phone: '+g('phone'),"
        "'Area of Interest: '+g('interest'),'',g('message')].join('\\n');"
        "window.location.href='mailto:medical@camnemi.com?subject='+"
        "encodeURIComponent('Camnemi Korea - Medical Inquiry')"
        "+'&body='+encodeURIComponent(b);"
        "return{ok:!0,text:async()=>JSON.stringify({code:'OK'})}})()",
    ),
]

# After patching, none of these may remain in the bundle.
FORBIDDEN = [
    "readdy.ai/api/form",
    "is_free?projectId",
    "cdn.jsdelivr.net/npm/posthog",
    "posthog.com",
    "posthog-js",
]


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


def apply_patches(js: str) -> str:
    for desc, src, new in LITERAL_PATCHES:
        if src is None:
            continue
        if src not in js:
            sys.exit(f"PATCH ANCHOR MISSING ({desc}): expected:\n  {src[:120]!r}")
        js = js.replace(src, new)
        print(f"  patched: {desc}")
    for desc, rx, new in REGEX_PATCHES:
        # NB: pass a lambda, never the raw replacement string. re.sub processes
        # backslash escapes in a replacement template, so a '\n' escape in
        # injected JS would silently become a REAL newline inside a JS string
        # literal and break the bundle. A callable is used verbatim.
        js, n = rx.subn(lambda _m, _new=new: _new, js)
        if n != 1:
            sys.exit(f"PATCH ANCHOR MISSING ({desc or rx.pattern}): matched {n} times, expected 1")
        if desc:
            print(f"  patched: {desc}")
    for bad in FORBIDDEN:
        if bad in js:
            sys.exit(f"forbidden reference survived patching: {bad!r}")
    return js


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
    orig_lf = js.count("\n")  # the minified bundle has a few, inside template literals

    # ---- images: download every CDN image the bundle references ----
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
    for old in sorted(p for p in img_dir.iterdir() if p.is_file()):
        if old.name not in sources:
            print(f"  removing unreferenced {old.name}")
            old.unlink()

    # ---- patch: localize images, runtime basename, then the site patches ----
    js = CDN_RE.sub(lambda m: "assets/img/" + m.group(2).rsplit("/", 1)[1], js)
    if js.count("basename:`/`") != 1:
        sys.exit("basename anchor not found exactly once")
    js = js.replace("basename:`/`", "basename:window.__APP_BASE__||`/`")
    if CDN_RE.findall(js):
        sys.exit("unlocalized CDN references remain")
    print("  patched: localized images + runtime basename")
    js = apply_patches(js)

    # Injected code must never introduce a real newline (see the re.sub note
    # above) - that would be a syntax error inside a JS string literal, while
    # still grepping as if the patch had applied. Count, do not assume.
    if js.count("\n") != orig_lf or "\r" in js:
        sys.exit(
            f"integrity: patching changed newline count "
            f"({orig_lf} -> {js.count(chr(10))}) or introduced CR"
        )

    # ---- write everything (binary); drop bundles from previous builds ----
    for old in list(assets.glob("index-*.js")) + list(assets.glob("index-*.css")):
        if old.name not in (js_name, css_name):
            print(f"  removing superseded {old.name}")
            old.unlink()
    (assets / js_name).write_bytes(js.encode("utf-8"))
    (assets / css_name).write_bytes(css)

    shell = build_shell(upstream_html, js_name, css_name)
    for name in ("index.html", "404.html"):
        (root / name).write_bytes(shell.encode("utf-8"))

    print("\nre-synced. review with `git diff --stat`, then commit + push.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
