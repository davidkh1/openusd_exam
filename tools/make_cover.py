"""Generate the ebook covers from the book's own assets.

Layout: dark ground, green accent rule, Latin Modern title (the book's own
interior face), the red-cube render on a white card over a ghosted
layer-stack motif, three differentiator lines, a small verified-examples
trust line, author footer.

Two outputs: cover.png (1600x2560, KDP's 1:1.6) and cover_page.png
(1764x2560, the book's 6.375x9.25 trim — bound into the PDF as page one).

Run:  .venv/bin/python tools/make_cover.py
"""
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = pathlib.Path(__file__).resolve().parent.parent
FIGURES = REPO / 'usd_exam_companion/figures'
OUT = REPO / 'usd_exam_companion/cover'

EDITION = 'v0.10 beta edition'
BG = (20, 23, 28)
GREEN = (118, 185, 0)
WHITE = (240, 242, 240)
GRAY = (150, 156, 160)

DEJAVU = pathlib.Path('/usr/share/fonts/truetype/dejavu')
LM = pathlib.Path('/usr/share/texmf/fonts/opentype/public/lm')
serif_bold = lambda s: ImageFont.truetype(str(LM / 'lmroman10-bold.otf'), s)
sans = lambda s: ImageFont.truetype(str(DEJAVU / 'DejaVuSans.ttf'), s)
sans_bold = lambda s: ImageFont.truetype(str(DEJAVU / 'DejaVuSans-Bold.ttf'), s)


def make(W, H, out_name):
    OUT.mkdir(exist_ok=True)
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 120  # side margin

    # top accent rule
    d.rectangle([0, 0, W, 14], fill=GREEN)

    # title block — the book's own Latin Modern, large and tight
    y = 150
    for line in ('OpenUSD', 'Exam', 'Companion'):
        d.text((M, y), line, font=serif_bold(176), fill=WHITE)
        y += 200
    d.rectangle([M, y + 52, W - M, y + 64], fill=GREEN)
    d.text((M, y + 100), 'NCP-OUSD Prep Notes and Tested Examples',
           font=sans(54), fill=GREEN)
    y += 36

    # signature figure on a white card (renders carry alpha: flatten to white)
    cube_src = Image.open(FIGURES / 'q13_cube_red.png').convert('RGBA')
    paper = Image.new('RGBA', cube_src.size, (250, 250, 248, 255))
    cube = Image.alpha_composite(paper, cube_src).convert('RGB')
    card_w = 1100
    scale = card_w / cube.width
    cube = cube.resize((card_w, int(cube.height * scale)))
    card = Image.new('RGB', (card_w + 40, cube.height + 40), (250, 250, 248))
    card.paste(cube, (20, 20))
    cx = (W - card.width) // 2
    cy = y + 190

    # ghosted layer stack behind the card: weaker layers peek out beneath —
    # the book's composition motif
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i, alpha in ((3, 36), (2, 64), (1, 110)):
        off = 30 * i
        od.rounded_rectangle(
            [cx - off, cy + off, cx + card.width - off, cy + card.height + off],
            radius=10, outline=GREEN + (alpha,), width=5)
    # soft shadow under the card
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([cx + 10, cy + 16, cx + card.width + 22, cy + card.height + 28],
                 fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert('RGBA'), shadow)
    img = Image.alpha_composite(img, overlay).convert('RGB')
    img.paste(card, (cx, cy))
    d = ImageDraw.Draw(img)

    # three differentiators (the "tested examples" claim is table stakes —
    # it lives in the small trust line below, not the headline lines)
    feats = ['Which layer wins, and why — LIVRPS, drilled',
             'Traps and gotchas: why each distractor fails',
             '60-question mock exam, scored by domain']
    # anchored from the footer so the block never collides with it
    y_trust = H - 280 - 70
    y = y_trust - 28 - 3 * 96
    for feat in feats:
        d.text((M + 30, y - 6), '✓', font=sans_bold(56), fill=GREEN)
        d.text((M + 116, y), feat, font=sans(52), fill=WHITE)
        y += 96
    d.text((M + 116, y_trust),
           'every example in this book was executed against real USD',
           font=sans(38), fill=GRAY)

    # footer
    d.rectangle([M, H - 280, W - M, H - 268], fill=GREEN)
    d.text((M, H - 220), 'David Khosid', font=serif_bold(78), fill=WHITE)
    d.text((W - M, H - 204), EDITION, font=sans(48), fill=GRAY, anchor='ra')

    img.save(OUT / out_name)
    print('wrote', OUT / out_name)


def main():
    make(1600, 2560, 'cover.png')        # KDP marketplace cover (1:1.6)
    make(1764, 2560, 'cover_page.png')   # book trim 6.375x9.25, page one


if __name__ == '__main__':
    main()
