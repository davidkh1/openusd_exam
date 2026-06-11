"""Generate a v1 KDP ebook cover (1600x2560) from the book's own assets.

Layout: dark ground, green accent rules, title block, the red-cube render on
a white card (the book's signature figure), author + delivery line.

Run:  .venv/bin/python tools/make_cover.py
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parent.parent
FIGURES = REPO / 'usd_exam_companion/figures'
OUT = REPO / 'usd_exam_companion/cover'

W, H = 1600, 2560
BG = (20, 23, 28)
GREEN = (118, 185, 0)
WHITE = (240, 242, 240)
GRAY = (150, 156, 160)

FONT_DIR = pathlib.Path('/usr/share/fonts/truetype/dejavu')
bold = lambda s: ImageFont.truetype(str(FONT_DIR / 'DejaVuSans-Bold.ttf'), s)
regular = lambda s: ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), s)


def main():
    OUT.mkdir(exist_ok=True)
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # accent rules
    d.rectangle([0, 0, W, 18], fill=GREEN)

    # title block
    y = 140
    for line in ('OpenUSD', 'Exam', 'Companion'):
        d.text((120, y), line, font=bold(150), fill=WHITE)
        y += 185

    d.rectangle([120, 740, W - 120, 752], fill=GREEN)
    d.text((120, 790), 'NCP-OUSD Prep Notes and Tested Examples',
           font=regular(54), fill=GREEN)

    # signature figure on a white card (renders carry alpha: flatten to white)
    cube_src = Image.open(FIGURES / 'q13_cube_red.png').convert('RGBA')
    white = Image.new('RGBA', cube_src.size, (250, 250, 248, 255))
    cube = Image.alpha_composite(white, cube_src).convert('RGB')
    card_w = 1160
    scale = card_w / cube.width
    cube = cube.resize((card_w, int(cube.height * scale)))
    card = Image.new('RGB', (card_w + 40, cube.height + 40), (250, 250, 248))
    card.paste(cube, (20, 20))
    cx = (W - card.width) // 2
    cy = 960
    d.rectangle([cx - 6, cy - 6, cx + card.width + 6, cy + card.height + 6],
                fill=GREEN)
    img.paste(card, (cx, cy))

    # delivery line + author
    feats = ['Every example executed against real USD',
             'All 55 study-guide objectives, margin-tagged',
             '60-question mock exam with explained key']
    y = cy + card.height + 110
    for feat in feats:
        d.ellipse([150, y + 18, 174, y + 42], fill=GREEN)
        d.text((210, y), feat, font=regular(52), fill=WHITE)
        y += 90

    d.rectangle([120, H - 300, W - 120, H - 288], fill=GREEN)
    d.text((120, H - 240), 'David Khosid', font=bold(72), fill=WHITE)
    d.text((W - 120, H - 228), 'v0.02 edition', font=regular(48),
           fill=GRAY, anchor='ra')

    img.save(OUT / 'cover.png')
    print('wrote', OUT / 'cover.png')


if __name__ == '__main__':
    main()
