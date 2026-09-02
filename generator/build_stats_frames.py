#!/usr/bin/env python3
"""
Fetches the live GitHub stats / streak / top-langs / snake SVGs, base64-embeds
each one into a small self-contained "frame" SVG with a rounded, always-light
background and an animated moving dashed border. Because the source image is
baked in as a data URI at build time (not linked at render time), the result
works correctly when GitHub displays it as <img src="...frame.svg">  -- browsers
block an SVG-used-as-<img> from fetching further external resources, so a
plain <image href="https://..."> nested inside a wrapper SVG does not render.

Run via .github/workflows/profile-cards.yml on a schedule.
"""
import base64
import re
import sys
import urllib.request

USERNAME = "devitsah"

SOURCES = {
    "stats-frame.svg": (
        "https://github-readme-stats.vercel.app/api"
        f"?username={USERNAME}&show_icons=true&theme=default&hide_border=true"
        "&title_color=2563EB&icon_color=0891B2&text_color=475569&bg_color=FFFFFF"
        "&count_private=true&hide_rank=true"
    ),
    "streak-frame.svg": (
        # github-readme-streak-stats.herokuapp.com is not a live public
        # instance (that name is only a placeholder used in the project's
        # "deploy your own" docs). streak-stats.demolab.com is the actual
        # public endpoint.
        "https://streak-stats.demolab.com/"
        f"?user={USERNAME}&hide_border=true&background=FFFFFF&stroke=2563EB"
        "&ring=0891B2&fire=10B981&currStreakLabel=2563EB&sideLabels=475569"
        "&currStreakNum=0F172A&sideNums=0F172A&dates=94A3B8&titleColor=2563EB"
    ),
    "langs-frame.svg": (
        "https://github-readme-stats.vercel.app/api/top-langs/"
        f"?username={USERNAME}&layout=compact&hide_border=true"
        "&title_color=2563EB&text_color=475569&bg_color=FFFFFF"
    ),
    # NOTE: the snake is intentionally NOT built into a frame here.
    # Baking an animated SVG into a base64 data URI and nesting it via
    # <image href="data:..."> inside another SVG does not reliably keep
    # the SMIL animation running once GitHub renders it in a README
    # (see https://github.com/github/markup/issues/1864) — you just get a
    # frozen first frame. The snake stays a plain, unwrapped <img> pointing
    # straight at the output branch instead; see README.md.
}

FALLBACK_SIZE = {
    "stats-frame.svg": (495, 195),
    "streak-frame.svg": (495, 195),
    "langs-frame.svg": (300, 300),
}

UA = {"User-Agent": "Mozilla/5.0 (profile-card-builder)"}


def fetch(url: str, attempts: int = 3) -> bytes:
    last_err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as e:
            last_err = e
            if i < attempts - 1:
                import time
                time.sleep(3 * (i + 1))  # simple backoff for rate limits
    raise last_err


def intrinsic_size(svg_bytes: bytes, fallback):
    text = svg_bytes.decode("utf-8", errors="ignore")
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text)
    if m:
        return float(m.group(1)), float(m.group(2))
    mw = re.search(r'width="([\d.]+)"', text)
    mh = re.search(r'height="([\d.]+)"', text)
    if mw and mh:
        return float(mw.group(1)), float(mh.group(1))
    return fallback


def frame_svg(name: str, img_w: float, img_h: float, mime: str, b64: str, uid: str) -> str:
    pad = 8
    radius = 16
    aspect = img_w / img_h
    canvas_w = 520 if aspect > 2 else max(320, min(920, img_w + pad * 2 + 20))
    canvas_h = canvas_w / aspect + pad * 2 + 20
    inner_w = canvas_w - pad * 2
    inner_h = canvas_h - pad * 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.0f}" height="{canvas_h:.0f}" viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}" role="img" aria-label="{name}">
<defs>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#2563EB"><animate attributeName="stop-color" values="#2563EB;#0891B2;#10B981;#2563EB" dur="6s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="#0891B2"><animate attributeName="stop-color" values="#0891B2;#10B981;#2563EB;#0891B2" dur="6s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#2563EB;#0891B2;#10B981" dur="6s" repeatCount="indefinite"/></stop>
</linearGradient>
<clipPath id="clip{uid}"><rect x="{pad+2}" y="{pad+2}" width="{inner_w-4:.0f}" height="{inner_h-4:.0f}" rx="{radius-4}"/></clipPath>
</defs>
<rect x="1" y="1" width="{canvas_w-2:.0f}" height="{canvas_h-2:.0f}" rx="{radius+pad-1}" fill="#FFFFFF"/>
<g clip-path="url(#clip{uid})">
  <image href="data:{mime};base64,{b64}" x="{pad+2}" y="{pad+2}" width="{inner_w-4:.0f}" height="{inner_h-4:.0f}" preserveAspectRatio="xMidYMid meet"/>
</g>
<rect x="3" y="3" width="{canvas_w-6:.0f}" height="{canvas_h-6:.0f}" rx="{radius+pad-3}" fill="none" stroke="url(#bg{uid})" stroke-width="3" stroke-linecap="round" stroke-dasharray="18 10">
  <animate attributeName="stroke-dashoffset" values="0;-56" dur="3.5s" repeatCount="indefinite"/>
</rect>
</svg>
'''


def main():
    import os
    os.makedirs("dist", exist_ok=True)
    ok = True
    for i, (out_name, url) in enumerate(SOURCES.items()):
        try:
            raw = fetch(url)
            w, h = intrinsic_size(raw, FALLBACK_SIZE[out_name])
            b64 = base64.b64encode(raw).decode()
            svg = frame_svg(out_name, w, h, "image/svg+xml", b64, uid=f"u{i}")
            out_path = os.path.join("dist", out_name)
            with open(out_path, "w") as f:
                f.write(svg)
            print(f"wrote {out_path} ({w:.0f}x{h:.0f})")
        except Exception as e:
            print(f"WARN: failed to build {out_name}: {e}", file=sys.stderr)
            ok = False
            # Keep whatever was already published rather than deleting it
            # from the output branch just because this run's fetch failed.
            try:
                prev_url = (
                    f"https://raw.githubusercontent.com/{USERNAME}/{USERNAME}"
                    f"/output/{out_name}"
                )
                prev = fetch(prev_url)
                out_path = os.path.join("dist", out_name)
                with open(out_path, "wb") as f:
                    f.write(prev)
                print(f"kept previous {out_name}")
            except Exception as e2:
                print(f"WARN: no previous {out_name} to keep: {e2}", file=sys.stderr)
    if not ok:
        # Don't fail the whole workflow just because one source (e.g. the
        # snake, before it has been generated once) wasn't ready yet.
        print("Some frames were not updated this run.")


if __name__ == "__main__":
    main()
