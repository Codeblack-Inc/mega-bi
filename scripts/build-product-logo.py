# /// script
# dependencies = ["fonttools"]
# ///
"""Build a `mega-<product>` wordmark SVG from the existing mega-ppt logo.

Keeps the symbol and the `mega` wordmark path verbatim and outlines only the
`-<product>` suffix in Space Grotesk, in the product colour.

    uv run scripts/build-product-logo.py diagram "#2F6FDB" SpaceGrotesk.ttf

Space Grotesk (OFL): https://github.com/google/fonts/tree/main/ofl/spacegrotesk
The metrics below were least-squares fitted against assets/svg/mega-ppt.svg
(total squared glyph-edge error 0.92px² over 32 edges).
"""

import re
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WGHT, SIZE, TRACK, X0, BASE = 690, 76.983, 0.187, 117.851, 80.0
RIGHT_PAD = 16.94  # mega-ppt.svg: last glyph edge 486.06 → width 503
ROOT = Path(__file__).resolve().parent.parent


def main(product: str, color: str, font_path: str) -> None:
    font = instantiateVariableFont(TTFont(font_path), {"wght": WGHT})
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = SIZE / font["head"].unitsPerEm

    x, parts, right = X0, [], 0.0
    for i, ch in enumerate("mega-" + product):
        glyph = glyphs[cmap[ord(ch)]]
        if i >= 4:  # "mega" is reused verbatim from mega-ppt.svg
            pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
            glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, BASE)))
            parts.append(pen.getCommands())
            bounds = BoundsPen(glyphs)
            glyph.draw(bounds)
            right = x + bounds.bounds[2] * scale
        x += glyph.width * scale + TRACK

    source = (ROOT / "assets/svg/mega-ppt.svg").read_text(encoding="utf-8")
    symbol = re.search(r"<g .*?</g>", source).group(0)
    mega = re.search(r'<path fill="#17152B" d="[^"]+"/>', source).group(0)
    width = round(right + RIGHT_PAD)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="112" viewBox="0 0 {width} 112">'
        f'{symbol}{mega}<path fill="{color}" d="{" ".join(parts)}"/></svg>'
    )
    out = Path(sys.argv[4]) if len(sys.argv) > 4 else ROOT / f"assets/svg/mega-{product}.svg"
    out.write_text(svg, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
