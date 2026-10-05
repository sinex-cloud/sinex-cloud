"""Build the profile README images (banner, link buttons, tool strip, two featured project cards),
each in a dark and a light version.

All text is turned into vector paths from JetBrains Mono, so the SVGs need no web fonts
and look the same everywhere GitHub shows them. Only needed when the text changes.

Run (fonttools required):  python make_svgs.py
"""

import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = "/usr/share/fonts/TTF/"
BOLD = TTFont(FONTS + "JetBrainsMonoNerdFont-Bold.ttf")
REGULAR = TTFont(FONTS + "JetBrainsMonoNerdFont-Regular.ttf")
OUT = Path(__file__).parent
ICONS = json.loads((OUT / "icons.json").read_text())  # Simple Icons paths (CC0), 24x24 viewBox

STROKE_ICONS = {
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
    "arrow": '<path d="M7 17 17 7M9 7h8v8"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5"/>',
}

THEMES = {
    "dark": dict(bg="#0c0e12", border="rgba(255,255,255,0.10)", text="#f3f4f6", dim="#8b919c",
                 muted="#a3a9b5", accent="#4ade80", ink="#0c0e12", dot="rgba(255,255,255,0.11)",
                 node="#14171c", line="rgba(255,255,255,0.16)",
                 brand=dict(terraform="#A07AE6", python="#4B8BBE", linux="#FCC624")),
    "light": dict(bg="#f7f6f2", border="rgba(15,23,42,0.12)", text="#111827", dim="#4b5563",
                  muted="#4b5563", accent="#15803d", ink="#ffffff", dot="rgba(15,23,42,0.14)",
                  node="#ffffff", line="rgba(15,23,42,0.18)",
                  brand=dict(terraform="#7B42BC", python="#3776AB", linux="#1f2937")),
}
BRAND = dict(git="#F05032", gitlab="#FC6D26", docker="#2496ED", ansible="#EE0000",
             googlecloud="#4285F4", fastapi="#009688")


def num(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def text(font, s, x, y, size, tracking=0.0, anchor="start"):
    """Turn a string into one SVG path. Returns (d, width). y is the baseline."""
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    width = sum(glyphs[cmap[ord(c)]].width * scale + tracking * size for c in s) - tracking * size
    x -= {"start": 0, "middle": width / 2, "end": width}[anchor]
    pen, cursor = SVGPathPen(glyphs, ntos=num), 0.0
    for c in s:
        glyph = glyphs[cmap[ord(c)]]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x + cursor, y)))
        cursor += glyph.width * scale + tracking * size
    return pen.getCommands(), width


def color(icon, t):
    return t["brand"].get(icon) or BRAND.get(icon, t["text"])


def icon(name, x, y, size, fill):
    s = size / 24
    if name in STROKE_ICONS:
        return (f'<g transform="translate({num(x)} {num(y)}) scale({num(s)})" fill="none" stroke="{fill}" '
                f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{STROKE_ICONS[name]}</g>')
    return f'<path transform="translate({num(x)} {num(y)}) scale({s:.4f})" d="{ICONS[name]}" fill="{fill}"/>'


def svg(w, h, label, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label}">\n<style>{style}\n  @media (prefers-reduced-motion: reduce) '
            f'{{ * {{ animation: none !important; }} }}\n</style>\n{body}\n</svg>\n')


def card(w, h, t):
    """Rounded card with a faded dot grid and a soft green wash."""
    return f"""<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r="1.2" fill="{t['dot']}"/></pattern>
  <radialGradient id="fade" cx="0.3" cy="0.15" r="0.8"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="fadeMask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
  <radialGradient id="wash" gradientUnits="userSpaceOnUse" cx="60" cy="0" r="620"><stop offset="0" stop-color="{t['accent']}" stop-opacity="0.14"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
  <clipPath id="clip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="{w}" height="{h}" fill="{t['bg']}"/>
  <rect width="{w}" height="{h}" fill="url(#wash)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)" mask="url(#fadeMask)"/>
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="20.5" fill="none" stroke="{t['border']}"/>"""


def banner(t):
    w, h = 1200, 290
    name, _ = text(BOLD, "Ahmed Brini", 58, 152, 112, tracking=-0.035)
    role_a, role_a_w = text(REGULAR, "Software Engineer, ", 60, 210, 34)
    role_b, _ = text(REGULAR, "Cloud & DevOps", 60 + role_a_w, 210, 34)
    prompt, prompt_w = text(BOLD, ">", 61, 254, 19)
    line, _ = text(REGULAR, "building CI/CD pipelines and infrastructure as code on Google Cloud", 61 + prompt_w + 12, 254, 19)
    avail, avail_w = text(REGULAR, "open to a PFE internship · Jan. 2027", 1142, 58, 17, anchor="end")
    dot_x = 1142 - avail_w - 18
    style = """
  .ping { transform-box: fill-box; transform-origin: center; animation: ping 2s cubic-bezier(.2,.7,.2,1) infinite; }
  @keyframes ping { 0% { transform: scale(.6); opacity: .9; } 80%, 100% { transform: scale(2.3); opacity: 0; } }"""
    body = f"""{card(w, h, t)}
<defs><linearGradient id="nameFill" gradientUnits="userSpaceOnUse" x1="0" y1="70" x2="0" y2="152"><stop offset="0.3" stop-color="{t['text']}"/><stop offset="1" stop-color="{t['dim']}"/></linearGradient></defs>
<path d="{name}" fill="url(#nameFill)"/>
<path d="{role_a}" fill="{t['text']}"/>
<path d="{role_b}" fill="{t['accent']}"/>
<path d="{prompt}" fill="{t['accent']}"/>
<path d="{line}" fill="{t['muted']}"/>
<circle cx="{num(dot_x)}" cy="52" r="5" fill="{t['accent']}"/>
<circle class="ping" cx="{num(dot_x)}" cy="52" r="5" fill="none" stroke="{t['accent']}" stroke-width="2"/>
<path d="{avail}" fill="{t['muted']}"/>"""
    return svg(w, h, "Ahmed Brini, Software Engineer, Cloud and DevOps", body, style)


def button(label, icon_name, primary, t):
    h, pad, isz, gap, fsize = 48, 18, 20, 10, 16
    _, tw = text(BOLD, label, 0, 0, fsize)
    w = round(pad + isz + gap + tw + pad)
    fg = t["ink"] if primary else t["text"]
    bg = t["accent"] if primary else t["node"]
    stroke = "none" if primary else t["line"]
    d, _ = text(BOLD, label, pad + isz + gap, 30, fsize)
    icon_fill = fg if primary or icon_name in STROKE_ICONS else color(icon_name, t)
    body = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{bg}" stroke="{stroke}"/>\n'
            f'{icon(icon_name, pad, (h - isz) / 2, isz, icon_fill)}\n<path d="{d}" fill="{fg}"/>')
    return svg(w, h, label, body)


TOOLS = [("googlecloud", "GCP"), ("terraform", "Terraform"), ("ansible", "Ansible"), ("gitlab", "GitLab CI"),
         ("docker", "Docker"), ("python", "Python"), ("fastapi", "FastAPI"), ("linux", "Linux"), ("git", "Git")]


def tools(t):
    tile, step, pad = 64, 92, 14
    w, h = pad * 2 + step * (len(TOOLS) - 1) + tile, 112
    parts = []
    for i, (name, label) in enumerate(TOOLS):
        x = pad + i * step
        parts.append(f'<rect x="{x + .5}" y="4.5" width="{tile - 1}" height="{tile - 1}" rx="16" fill="{t["node"]}" stroke="{t["line"]}"/>')
        parts.append(icon(name, x + 18, 22.5, 28, color(name, t)))
        d, _ = text(REGULAR, label, x + tile / 2, 98, 13.5, anchor="middle")
        parts.append(f'<path d="{d}" fill="{t["muted"]}"/>')
    return svg(w, h, "Tools: " + ", ".join(label for _, label in TOOLS), "\n".join(parts))


def project(t, where, title, desc, stack, status, link, stages):
    w, h = 1200, 290
    parts = [card(w, h, t)]
    for font, s, y, size, fill in (
        (REGULAR, f"featured project · hosted on {where}", 62, 15, t["accent"]),
        (BOLD, title, 108, 32, t["text"]),
        (REGULAR, desc[0], 152, 18, t["muted"]),
        (REGULAR, desc[1], 178, 18, t["muted"]),
        (REGULAR, stack, 250, 14, t["dim"]),
    ):
        d, _ = text(font, s, 48, y, size)
        parts.append(f'<path d="{d}" fill="{fill}"/>')

    status_d, status_w = text(BOLD, status, 1146, 62, 15, anchor="end")
    parts.append(f'<circle cx="{num(1146 - status_w - 14)}" cy="57" r="5" fill="{t["accent"]}"/><path d="{status_d}" fill="{t["accent"]}"/>')
    link_d, _ = text(REGULAR, link, 1126, 250, 14, anchor="end")
    parts.append(f'<path d="{link_d}" fill="{t["text"]}"/>{icon("arrow", 1130, 237, 16, t["text"])}')

    size, step, x0, y0 = 52, 102, 690, 132
    style = ["\n  @keyframes node { from { stroke: %s; stroke-opacity: 1; } }" % t["line"],
             "  @keyframes pop { from { transform: scale(0); } }",
             "  @keyframes draw { from { transform: scaleX(0); } }",
             "  .c { transform-box: fill-box; transform-origin: center; }",
             "  .l { transform-box: fill-box; transform-origin: left center; }"]
    for i, (name, label) in enumerate(stages):
        x, delay = x0 + i * step, 0.4 + i * 0.4
        style.append(f"  .n{i} {{ animation: node .4s ease {delay:.2f}s both; }} .c{i} {{ animation: pop .35s cubic-bezier(.3,1.6,.5,1) {delay + .15:.2f}s both; }}")
        if i < len(stages) - 1:
            x1, x2, y = x + size + 12, x + step - 12, y0 + size / 2
            style.append(f"  .l{i} {{ animation: draw .4s ease {delay + .2:.2f}s both; }}")
            parts.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{t["line"]}" stroke-width="2" stroke-linecap="round"/>')
            parts.append(f'<line class="l l{i}" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<rect class="n{i}" x="{x + .5}" y="{y0 + .5}" width="{size - 1}" height="{size - 1}" rx="14" fill="{t["node"]}" stroke="{t["accent"]}" stroke-opacity="0.75"/>')
        parts.append(icon(name, x + 13, y0 + 13, 26, color(name, t)))
        parts.append(f'<g transform="translate({x + size - 2} {y0 + size - 2})"><g class="c c{i}"><circle r="10" fill="{t["accent"]}" stroke="{t["bg"]}" stroke-width="3"/>'
                     f'<path d="M-4 .3-1.1 3.2 4.3-2.5" fill="none" stroke="{t["ink"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
        d, _ = text(REGULAR, label, x + size / 2, y0 + size + 30, 13.5, anchor="middle")
        parts.append(f'<path d="{d}" fill="{t["muted"]}"/>')
    label = f"Featured project hosted on {where}: {title}. {desc[0]} {desc[1]}"
    return svg(w, h, label, "\n".join(parts), "\n".join(style))


PIPELINE = dict(
    where="GitLab", title="CI/CD Delivery Pipeline on GCP",
    desc=("Every push to main is tested, published to Docker Hub", "and deployed to two GCP VMs in under two minutes."),
    stack="GitLab CI/CD · Ansible · Terraform · Docker · FastAPI",
    status="passed in 84 s", link="view on GitLab",
    stages=[("git", "push"), ("gitlab", "test"), ("docker", "build"), ("ansible", "deploy"), ("googlecloud", "live")],
)
TERRAFORM = dict(
    where="GitHub", title="GCP Infrastructure Automation with Terraform",
    desc=("A GitHub App runs policy checks on every Terraform PR,", "and nothing is applied without human approval."),
    stack="Terraform · Cloud Run · Cloud Build · BigQuery · IAM",
    status="approval required before apply", link="view on GitHub",
    stages=[("github", "PR"), ("terraform", "plan"), ("googlecloud", "checks"), ("user", "approve"), ("terraform", "apply")],
)
BUTTONS = [("portfolio", "Portfolio", "globe", True), ("linkedin", "LinkedIn", "linkedin", False),
           ("gitlab", "GitLab", "gitlab", False), ("email", "Email", "mail", False)]

for old in OUT.glob("*.svg"):
    old.unlink()
for theme, palette in THEMES.items():
    (OUT / f"banner-{theme}.svg").write_text(banner(palette))
    (OUT / f"tools-{theme}.svg").write_text(tools(palette))
    (OUT / f"project-pipeline-{theme}.svg").write_text(project(palette, **PIPELINE))
    (OUT / f"project-terraform-{theme}.svg").write_text(project(palette, **TERRAFORM))
    for slug, label, icon_name, primary in BUTTONS:
        (OUT / f"btn-{slug}-{theme}.svg").write_text(button(label, icon_name, primary, palette))
    print("wrote", theme)
