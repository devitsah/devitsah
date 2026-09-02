import json, math

data = json.load(open('/home/claude/work/gen/groups.json'))
GRID_W, GRID_H = 150, 170

PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 36, 84, 400, 492
sx = PANEL_W / GRID_W
sy = PANEL_H / GRID_H
stroke_w = sy * 1.06

def runs_path(runs):
    parts = []
    for (row, start, length) in runs:
        x = start * sx
        y = row * sy + sy / 2
        w = length * sx
        parts.append(f"M{x:.2f} {y:.2f} h{w:.2f}")
    return " ".join(parts)

def intro_groups_svg(groups, color):
    """~60 scattered groups fading in together over ~2s, then held, then hidden after 3.2s (set stays static afterward via CSS opacity 1 baseline)."""
    out = []
    n = len(groups)
    for i, g in enumerate(groups):
        if not g:
            continue
        d = runs_path(g)
        begin = round((i / n) * 1.6, 3)  # interleaved starts across whole 1.6s window -> ~2s incl anim dur
        out.append(
            f'<path d="{d}" stroke="{color}" stroke-width="{stroke_w:.2f}" stroke-linecap="butt" fill="none" opacity="0">'
            f'<animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin}s" fill="freeze" calcMode="spline" keySplines="0.3 0 0.4 1"/>'
            f'</path>'
        )
    return "\n".join(out)

def all_groups_static(groups, color):
    d = runs_path([r for g in groups for r in g])
    return f'<path d="{d}" stroke="{color}" stroke-width="{stroke_w:.2f}" stroke-linecap="butt" fill="none"/>'

# ---------- palettes ----------
LIGHT = dict(
    bg="#FFFFFF", panel="#F8FAFC", panelgrad0="#F8FAFC", panelgrad1="#EEF2F7",
    chrome="#F1F5F9", border="rgba(15,23,42,0.10)", titlebar_text="#475569",
    label="#94A3B8", frame_stroke="#0891B2", frame_fill="#F8FAFC",
    portrait="#4A4470", accent0="#2563EB", accent1="#0891B2", accent2="#10B981",
    row_label="#64748B", row_value="#0F172A", leader="#CBD5E1",
    pill_bg="#EEF2FF", pill_text="#4338CA", live_bg="#FEE2E2", live_text="#DC2626",
    card_bg="#FBFBFE", card_border="rgba(8,145,178,0.20)", dot_off="#CBD5E1",
    window_dots=("#ff5f56", "#ffbd2e", "#27c93f"),
)
DARK = dict(
    bg="#0A101F", panel="#0F172A", panelgrad0="#0F172A", panelgrad1="#0A101F",
    chrome="#111827", border="rgba(148,163,184,0.14)", titlebar_text="#94A3B8",
    label="#64748B", frame_stroke="#22D3EE", frame_fill="#0B1220",
    portrait="#D8D2FF", accent0="#22D3EE", accent1="#7C3AED", accent2="#10B981",
    row_label="#64748B", row_value="#E2E8F0", leader="#1E293B",
    pill_bg="rgba(167,139,250,0.14)", pill_text="#C4B5FD", live_bg="rgba(239,68,68,0.16)", live_text="#F87171",
    card_bg="rgba(148,163,184,0.06)", card_border="rgba(34,211,238,0.22)", dot_off="#334155",
    window_dots=("#ff5f56", "#ffbd2e", "#27c93f"),
)

NAME = "Devit Sah"
HANDLE = "@devitsah"
EMAIL = "sahdevit76@gmail.com"

INFO_ROWS = [
    ("Subject", "Devit Sah"),
    ("Role", "Software Developer"),
    ("Focus", ".NET . Angular . AI Systems"),
    ("Education", "Thapar Institute of Engg &amp; Tech"),
    ("Status", "Building + Learning + Shipping"),
    (None, None),  # spacer
    ("Core.Lang", "C# . TypeScript . Python"),
    ("Core.Frontend", "Angular"),
    ("Core.Backend", "ASP.NET Core . FastAPI . Flask"),
    ("Core.Database", "PostgreSQL . MongoDB . Redis"),
    ("Core.Infra", "Docker . Kafka . Ollama"),
    (None, None),
    ("Grid.Mail", "sahdevit76@gmail.com"),
    ("Grid.LinkedIn", "in/devit-sah-d780"),
    ("Grid.GitHub", "devitsah"),
]

PROJECTS = [
    ("DASHGEN.AI", "NL -> SQL -> live dashboards", "brain"),
    ("APIFORGE", "6-service microservice gateway", "hex"),
    ("AGENTIC.AI", "Currently working on Agentic AI", "orbit"),
]

def project_card(kind, title, desc, cx0, cy0, w, h, color, accent, text_color, label_color, card_bg, card_border):
    icon_cx, icon_cy = cx0 + 34, cy0 + h/2
    icon = project_icon(kind, icon_cx, icon_cy, color, accent)
    return f'''
    <g>
      <rect x="{cx0}" y="{cy0}" width="{w}" height="{h}" rx="10" fill="{card_bg}" stroke="{card_border}" stroke-width="1"/>
      <rect x="{cx0}" y="{cy0}" width="4" height="{h}" rx="2" fill="{accent}"/>
      <g transform="translate(0,0)">
        <animateTransform attributeName="transform" type="scale" values="0.5;1.06;1" keyTimes="0;0.5;1" dur="0.5s" additive="sum" fill="freeze"/>
        {icon}
      </g>
      <text x="{icon_cx+34}" y="{icon_cy-3}" font-size="13" font-weight="600" fill="{text_color}" letter-spacing="1">{title}</text>
      <text x="{icon_cx+34}" y="{icon_cy+13}" font-size="10.5" fill="{label_color}">{desc}</text>
    </g>'''

def project_icon(kind, cx, cy, color, accent):
    """Small original geometric glyph (not traced from any real logo)."""
    if kind == "brain":
        return f'''
        <g stroke="{color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path d="M{cx-22},{cy-6} q-10,-14 2,-20 q10,-5 14,4 q10,-9 18,0 q8,8 -2,16 q10,6 2,18 q-6,10 -18,6 q-4,10 -16,6 q-10,-4 -6,-14 q-10,-2 -8,-14 q1,-8 14,-2 z"/>
          <circle cx="{cx-6}" cy="{cy-4}" r="1.6" fill="{accent}" stroke="none"/>
          <circle cx="{cx+6}" cy="{cy+3}" r="1.6" fill="{accent}" stroke="none"/>
          <circle cx="{cx+1}" cy="{cy-10}" r="1.6" fill="{accent}" stroke="none"/>
        </g>'''
    if kind == "hex":
        pts = []
        for k in range(6):
            ang = math.pi/3*k - math.pi/2
            pts.append((cx+20*math.cos(ang), cy+20*math.sin(ang)))
        poly = " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
        inner = []
        for k in range(6):
            ang = math.pi/3*k - math.pi/2
            inner.append((cx+9*math.cos(ang), cy+9*math.sin(ang)))
        return f'''
        <g stroke="{color}" stroke-width="2.2" fill="none" stroke-linejoin="round">
          <polygon points="{poly}"/>
          <circle cx="{cx}" cy="{cy}" r="4" fill="{accent}" stroke="none"/>
          {"".join(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>' for x,y in inner)}
        </g>'''
    if kind == "eye":
        return f'''
        <g stroke="{color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path d="M{cx-22},{cy} q22,-18 44,0 q-22,18 -44,0 z"/>
          <circle cx="{cx}" cy="{cy}" r="7" fill="none"/>
          <circle cx="{cx}" cy="{cy}" r="2.4" fill="{accent}" stroke="none"/>
        </g>'''
    if kind == "orbit":
        pts = []
        for k in range(3):
            ang = math.pi*2/3*k - math.pi/2
            pts.append((cx+18*math.cos(ang), cy+18*math.sin(ang)))
        lines = "".join(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>' for x, y in pts)
        nodes = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{accent}" stroke="none"/>' for x, y in pts)
        return f'''
        <g stroke="{color}" stroke-width="2" fill="none" stroke-linejoin="round">
          <ellipse cx="{cx}" cy="{cy}" rx="20" ry="9" transform="rotate(-20 {cx} {cy})" opacity="0.6"/>
          {lines}
          <circle cx="{cx}" cy="{cy}" r="4.5" fill="{color}" stroke="none"/>
          {nodes}
        </g>'''
    return ""

def build(palette, is_dark, groups):
    P = palette
    ax0, ax1, ax2 = P["accent0"], P["accent1"], P["accent2"]
    w1, w2, w3 = P["window_dots"]

    intro = intro_groups_svg(groups, P["portrait"])

    # ---- info panel rows with computed dotted leaders ----
    rows_svg = []
    ry = 132
    ROW_H = 23
    LABEL_X = 470
    VALUE_X = 1140
    for label, value in INFO_ROWS:
        if label is None:
            ry += ROW_H * 0.55
            continue
        label_w = len(label) * 6.4
        value_w = len(value) * 6.0
        leader_x0 = LABEL_X + label_w + 8
        leader_x1 = VALUE_X - value_w - 10
        rows_svg.append(f'''
        <text x="{LABEL_X}" y="{ry}" font-size="12.5" fill="{P['row_label']}" letter-spacing="0.5">{label}</text>
        <line x1="{leader_x0:.1f}" y1="{ry-4}" x2="{max(leader_x0, leader_x1):.1f}" y2="{ry-4}" stroke="{P['leader']}" stroke-width="1" stroke-dasharray="1.5,3"/>
        <text x="{VALUE_X}" y="{ry}" font-size="12.5" fill="{P['row_value']}" text-anchor="end" textLength="{value_w:.1f}" lengthAdjust="spacingAndGlyphs">{value}</text>''')
        ry += ROW_H

    # ---- rotating project strip: card carousel with progress dots (distinct "carousel scan" style) ----
    n = len(PROJECTS)
    seg = 4.4
    card_x, card_y, card_w, card_h = 470, ry + 34, 396, 70
    proj_svg = []
    for i, (title, desc, kind) in enumerate(PROJECTS):
        begin = i * seg
        card = project_card(kind, title, desc, card_x, card_y, card_w, card_h,
                             ax1, ax2, P['row_value'], P['row_label'], P['card_bg'], P['card_border'])
        proj_svg.append(f'''
        <g opacity="0">
          <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.82;1" dur="{seg}s" begin="{begin}s;proj{i}.end+{ (n-1)*seg }s" id="proj{i}" fill="freeze"/>
          <animateTransform attributeName="transform" type="translate" values="18,0;0,0;0,0;-18,0" keyTimes="0;0.08;0.82;1" dur="{seg}s" begin="{begin}s;proj{i}t.end+{ (n-1)*seg }s" id="proj{i}t" fill="freeze"/>
          {card}
        </g>''')
    proj_block = "\n".join(proj_svg)

    dots_svg = []
    dot_y = card_y + card_h + 16
    for i in range(n):
        dcx = card_x + 8 + i * 16
        begin = i * seg
        dots_svg.append(f'''
        <circle cx="{dcx}" cy="{dot_y}" r="3" fill="{P['dot_off']}"/>
        <circle cx="{dcx}" cy="{dot_y}" r="3" fill="{ax1}" opacity="0">
          <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.82;1" dur="{seg}s" begin="{begin}s;pdot{i}.end+{ (n-1)*seg }s" id="pdot{i}" fill="freeze"/>
        </circle>''')
    dots_block = "".join(dots_svg)

    handle_pill_w = 12 + len(HANDLE) * 7.2
    email_title = f"{EMAIL} - % ./profile.sh --live"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="{NAME} — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{ax0}"><animate attributeName="stop-color" values="{ax0};{ax1};{ax2};{ax0}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="{ax1}"><animate attributeName="stop-color" values="{ax1};{ax2};{ax0};{ax1}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="{ax2}"><animate attributeName="stop-color" values="{ax2};{ax0};{ax1};{ax2}" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P['panelgrad0']}"/><stop offset="1" stop-color="{P['panelgrad1']}"/></linearGradient>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="beamGlow" x="-80%" y="-200%" width="260%" height="500%"><feGaussianBlur stdDeviation="3.5"/></filter>
<linearGradient id="beamTrail" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{ax1}" stop-opacity="0"/>
  <stop offset="1" stop-color="{ax1}" stop-opacity="0.30"/>
</linearGradient>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<clipPath id="portraitClip"><rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="8"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{P['bg']}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{P['chrome']}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{P['border']}"/>
<circle cx="30" cy="25" r="5.5" fill="{w1}"/>
<circle cx="50" cy="25" r="5.5" fill="{w2}"/>
<circle cx="70" cy="25" r="5.5" fill="{w3}"/>
<text x="590" y="29" text-anchor="middle" font-size="12" fill="{P['titlebar_text']}">{email_title}</text>

<text x="{PANEL_X+2}" y="{PANEL_Y-10}" font-size="10" letter-spacing="3" fill="{P['label']}">VISUAL.MAP</text>
<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="none" stroke="{P['frame_stroke']}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="{P['frame_fill']}" stroke="{P['frame_stroke']}" stroke-opacity="0.4"/>
<g clip-path="url(#portraitClip)">
  <g transform="translate({PANEL_X},{PANEL_Y})" shape-rendering="crispEdges">
    {intro}
  </g>
  <g>
    <rect x="{PANEL_X}" y="{PANEL_Y-46}" width="{PANEL_W}" height="46" fill="url(#beamTrail)">
      <animate attributeName="y" values="{PANEL_Y-46};{PANEL_Y+PANEL_H-2};{PANEL_Y-46}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.2 1;0.45 0 0.2 1"/>
    </rect>
    <rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="2" fill="{ax1}" filter="url(#beamGlow)">
      <animate attributeName="y" values="{PANEL_Y};{PANEL_Y+PANEL_H-2};{PANEL_Y}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.2 1;0.45 0 0.2 1"/>
      <animate attributeName="opacity" values="0.9;0.9;0" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>
</g>
{"".join(
  f'<path d="{p}" stroke="{ax1}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7">'
  f'<animate attributeName="opacity" values="0.35;0.85;0.35" dur="2.4s" repeatCount="indefinite" begin="{0.3*k}s"/></path>'
  for k, p in enumerate([
    f"M{PANEL_X-2},{PANEL_Y+16} v-10 a8,8 0 0 1 8,-8 h10",
    f"M{PANEL_X+PANEL_W+2},{PANEL_Y+16} v-10 a8,8 0 0 0 -8,-8 h-10",
    f"M{PANEL_X-2},{PANEL_Y+PANEL_H-16} v10 a8,8 0 0 0 8,8 h10",
    f"M{PANEL_X+PANEL_W+2},{PANEL_Y+PANEL_H-16} v10 a8,8 0 0 1 -8,8 h-10",
  ])
)}

<text x="470" y="74" font-size="10" letter-spacing="3" fill="{P['label']}">SYSTEM.INFO</text>
<circle cx="1090" cy="70" r="4" fill="{P['live_text']}">
  <animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>
</circle>
<text x="1100" y="74" font-size="12" fill="{P['live_text']}" letter-spacing="1">LIVE</text>

<rect x="470" y="92" width="{handle_pill_w:.0f}" height="26" rx="13" fill="{P['pill_bg']}"/>
<text x="{470+handle_pill_w/2:.0f}" y="109" text-anchor="middle" font-size="13" fill="{P['pill_text']}" font-weight="600">{HANDLE}</text>

{"".join(rows_svg)}

<line x1="470" y1="{ry+8}" x2="1140" y2="{ry+8}" stroke="{P['border']}"/>
<text x="470" y="{ry+26}" font-size="10" letter-spacing="3" fill="{P['label']}">NOW.BUILDING</text>
{proj_block}
{dots_block}
</g>
</svg>'''
    return svg

light_svg = build(LIGHT, False, data["light"])
dark_svg  = build(DARK, True, data["dark"])

open('/home/claude/work/gen/light.svg','w').write(light_svg)
open('/home/claude/work/gen/dark.svg','w').write(dark_svg)
print("light bytes", len(light_svg), "dark bytes", len(dark_svg))
