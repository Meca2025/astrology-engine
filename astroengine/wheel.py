"""Chart wheels: dependency-free SVG natal charts.

Pure data in, SVG out. This module never imports the legacy monolith —
the CLI layer computes positions/cusps/aspects and passes plain data.
"""

import math as _math
import xml.sax.saxutils as _sax

# Huginn notes the glyphs: Sun through Pluto and the North Node.
PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "N.Node": "☊", "S.Node": "☋",
}

SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍",
               "♎", "♏", "♐", "♑", "♒", "♓"]

# Aspect colors on the night sky.
ASPECT_COLORS = {
    "conjunction": "#f5f2e8",
    "opposition": "#e5484d",
    "square": "#f76b15",
    "trine": "#3e9bff",
    "sextile": "#46c08a",
}

# Planet rings, outward from the aspect field; a planet takes the first
# ring free of all conflicts (Sólrún D1: never toggle back onto one).
_PLANET_RINGS = (140.0, 116.0, 164.0)
_CONFLICT_DEG = 6.0


def _assign_rings(longitudes: list[float]) -> list[float]:
    """Give each longitude a ring with no neighbor inside _CONFLICT_DEG."""
    placed: list[tuple[float, float]] = []
    rings: list[float] = []
    for lon in longitudes:
        busy = {pring for plon, pring in placed
                if abs((lon - plon + 180) % 360 - 180) < _CONFLICT_DEG}
        ring = next((r for r in _PLANET_RINGS if r not in busy),
                    _PLANET_RINGS[0])
        placed.append((lon, ring))
        rings.append(ring)
    return rings
_BG = "#0d1021"
_GOLD = "#c9a227"
_GOLD_SOFT = "#e8c872"
_INK = "#f2f0e6"
_MUTED = "#8fa3c7"
_HOUSE_LINE = "#5a6b8c"
_GLYPH_FONT = ("'Segoe UI Symbol','Noto Sans Symbols 2',"
               "'DejaVu Sans',Georgia,serif")


def _polar(cx: float, cy: float, r: float, longitude: float, rot: float = 0.0):
    """Zodiac running counterclockwise; rot spins the whole sky."""
    theta = _math.radians(180.0 + ((longitude + rot) % 360.0))
    return (cx + r * _math.cos(theta), cy - r * _math.sin(theta))


def _esc(text) -> str:
    return _sax.escape(str(text or ""))


def wheel_svg(planets: list[dict], cusps: list[float],
              aspects: list[dict], meta: dict | None = None) -> str:
    """Render a natal chart wheel as an SVG string.

    planets: [{name, glyph, longitude}]; cusps: 12 floats;
    aspects: [{a, b, kind}]; meta: {title, subtitle, asc, mc}.
    """
    meta = meta or {}
    cx = cy = 300.0
    # The sky turns so the Ascendant rests at 9 o'clock, as tradition demands.
    asc_lon = meta.get("asc")
    rot = ((0.0 - asc_lon) % 360.0
           if isinstance(asc_lon, (int, float)) else 0.0)

    def pol(r: float, longitude: float):
        return _polar(cx, cy, r, longitude, rot)

    size = 600
    parts: list[str] = []
    w = parts.append

    w(f'<svg xmlns="http://www.w3.org/2000/svg" '
      f'viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
      f'font-family="Georgia, serif">')
    w(f'<rect width="{size}" height="{size}" fill="{_BG}"/>')

    # --- zodiac ring: outer gold circle, sign cells, glyphs, ticks ---
    w(f'<circle cx="{cx}" cy="{cy}" r="290" fill="none" '
      f'stroke="{_GOLD}" stroke-width="2"/>')
    w(f'<circle cx="{cx}" cy="{cy}" r="248" fill="none" '
      f'stroke="{_GOLD}" stroke-width="1.5"/>')
    for i in range(12):
        lon = i * 30.0
        x1, y1 = pol(290, lon)
        x2, y2 = pol(248, lon)
        w(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
          f'stroke="{_GOLD}" stroke-width="1"/>')
        gx, gy = pol(269, lon + 15)
        w(f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="20" '
          f'fill="{_GOLD_SOFT}" font-family="{_GLYPH_FONT}">{SIGN_GLYPHS[i]}</text>')
    for deg in range(0, 360, 5):
        if deg % 30 == 0:
            continue
        r1, r2 = (284, 290) if deg % 10 == 0 else (286, 290)
        x1, y1 = pol(r1, deg)
        x2, y2 = pol(r2, deg)
        w(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
          f'stroke="{_GOLD}" stroke-width="0.7" opacity="0.7"/>')

    # --- house cusps and numbers ---
    if cusps and len(cusps) == 12:
        for i, cusp in enumerate(cusps):
            x1, y1 = pol(248, cusp)
            x2, y2 = pol(172, cusp)
            w(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
              f'y2="{y2:.1f}" stroke="{_HOUSE_LINE}" stroke-width="1"/>')
            nx, ny = pol(208, (cusp + cusps[(i + 1) % 12]) / 2
                            if abs(cusps[(i + 1) % 12] - cusp) < 180
                            else (cusp + cusps[(i + 1) % 12] + 360) / 2)
            w(f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" '
              f'dominant-baseline="central" font-size="13" '
              f'fill="{_MUTED}">{i + 1}</text>')

    # --- ASC / MC markers ---
    for label, lon in (("ASC", meta.get("asc")), ("MC", meta.get("mc"))):
        if lon is None:
            continue
        x, y = pol(236, lon)
        w(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="11" '
          f'fill="{_INK}" font-weight="bold">{label}</text>')

    # --- planets, spread across rings when crowded (Sólrún D1) ---
    ordered = sorted(planets, key=lambda d: d["longitude"] % 360)
    rings = _assign_rings([p["longitude"] % 360 for p in ordered])
    for p, ring in zip(ordered, rings):
        lon = p["longitude"] % 360
        x, y = pol(ring, lon)
        glyph = p.get("glyph") or PLANET_GLYPHS.get(p.get("name", ""), "?")
        w(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="22" fill="{_INK}" font-family="{_GLYPH_FONT}">'
          f'{_esc(glyph)}</text>')

    # --- aspect chords inside the wheel ---
    by_name = {p["name"]: p["longitude"] % 360 for p in planets}
    for a in aspects:
        la = by_name.get(a.get("a"))
        lb = by_name.get(a.get("b"))
        if la is None or lb is None:
            continue
        color = ASPECT_COLORS.get(str(a.get("kind", "")).lower(), "#8a8f9e")
        x1, y1 = pol(100, la)
        x2, y2 = pol(100, lb)
        w(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
          f'stroke="{color}" stroke-width="1.4" opacity="0.85"/>')
    w(f'<circle cx="{cx}" cy="{cy}" r="100" fill="none" '
      f'stroke="{_HOUSE_LINE}" stroke-width="1" opacity="0.6"/>')

    # --- heart of the wheel: name and date ---
    w(f'<circle cx="{cx}" cy="{cy}" r="64" fill="{_BG}" '
      f'stroke="{_GOLD}" stroke-width="1.5"/>')
    w(f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="17" '
      f'fill="{_GOLD_SOFT}">{_esc(meta.get("title", "Natal Chart"))}</text>')
    w(f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="12" '
      f'fill="{_MUTED}">{_esc(meta.get("subtitle", ""))}</text>')

    w('</svg>')
    return "".join(parts)


__all__ = ["PLANET_GLYPHS", "SIGN_GLYPHS", "ASPECT_COLORS", "wheel_svg"]
