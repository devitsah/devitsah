#!/usr/bin/env python3
"""
Fetches the live GitHub stats / streak / top-langs / snake SVGs and nests
each one, as native inline <svg> content (not a rasterized/base64 <image>),
inside a small self-contained "frame" SVG with a rounded, always-light
background and an animated moving dashed border.

Why inline <svg> instead of <image href="data:...">: embedding a source
SVG via <image> effectively treats it as an opaque raster reference in most
browsers when rendered inside a GitHub README, so any SMIL <animate> tags
in the source (like the contribution snake) freeze on the first frame
(see https://github.com/github/markup/issues/1864). Nesting the source's
markup directly as a child <svg> element instead keeps it as live vector
content in the same document, so its animations keep running normally.

Run via .github/workflows/profile-cards.yml on a schedule.
"""
import re
import sys
import time
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
        # streak-stats.demolab.com is the real public instance; the old
        # github-readme-streak-stats.herokuapp.com URL used here previously
        # was never a live public endpoint.
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
    # snake-frame.svg is handled separately below: it's built from the
    # snake SVG generated earlier in THIS SAME job run (dist/github-snake.svg),
    # not fetched over the network from the output branch. Fetching it from
    # the output branch was racy: this workflow and the snake-generation
    # step used to be two separate workflows publishing to the same output
    # branch, and whichever one published last would wipe out the other's
    # files, causing the snake (or the stats cards) to intermittently 404.
}

LOCAL_SOURCES = {
    "snake-frame.svg": "dist/github-snake.svg",
}

FALLBACK_SIZE = {
    "stats-frame.svg": (495, 195),
    "streak-frame.svg": (495, 195),
    "langs-frame.svg": (300, 300),
    "snake-frame.svg": (880, 130),
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


def extract_inner_svg(svg_bytes: bytes) -> str:
    """Strip the outer <svg ...> ... </svg> wrapper, keeping only the
    children, so we can re-nest them inside our own <svg> element."""
    text = svg_bytes.decode("utf-8", errors="ignore")
    m_open = re.search(r"<svg\b[^>]*>", text, re.IGNORECASE | re.DOTALL)
    if not m_open:
        raise ValueError("no <svg> opening tag found in source")
    start = m_open.end()
    end = text.rfind("</svg>")
    if end == -1:
        raise ValueError("no </svg> closing tag found in source")
    return text[start:end]


def frame_svg(name: str, img_w: float, img_h: float, inner_content: str, uid: str) -> str:
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
  <svg x="{pad+2}" y="{pad+2}" width="{inner_w-4:.0f}" height="{inner_h-4:.0f}" viewBox="0 0 {img_w:.0f} {img_h:.0f}" preserveAspectRatio="xMidYMid meet">
    {inner_content}
  </svg>
</g>
<rect x="3" y="3" width="{canvas_w-6:.0f}" height="{canvas_h-6:.0f}" rx="{radius+pad-3}" fill="none" stroke="url(#bg{uid})" stroke-width="3" stroke-linecap="round" stroke-dasharray="18 10">
  <animate attributeName="stroke-dashoffset" values="0;-56" dur="3.5s" repeatCount="indefinite"/>
</rect>
</svg>
'''


def build_one(out_name, raw, uid):
    w, h = intrinsic_size(raw, FALLBACK_SIZE[out_name])
    inner = extract_inner_svg(raw)
    svg = frame_svg(out_name, w, h, inner, uid=uid)
    out_path = os.path.join("dist", out_name)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path} ({w:.0f}x{h:.0f})")


def main():
    global os
    import os
    os.makedirs("dist", exist_ok=True)
    ok = True

    for i, (out_name, url) in enumerate(SOURCES.items()):
        try:
            raw = fetch(url)
            build_one(out_name, raw, uid=f"u{i}")
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

    # Snake: built from the file this same job just generated locally
    # (no network round-trip to the output branch, so no race condition).
    for i, (out_name, local_path) in enumerate(LOCAL_SOURCES.items(), start=len(SOURCES)):
        try:
            with open(local_path, "rb") as f:
                raw = f.read()
            build_one(out_name, raw, uid=f"u{i}")
        except Exception as e:
            print(f"WARN: failed to build {out_name} from {local_path}: {e}", file=sys.stderr)
            ok = False
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
        print("Some frames were not updated this run.")


if __name__ == "__main__":
    main()
