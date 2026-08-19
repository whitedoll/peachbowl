import os, sys, glob
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

REF = r"D:\peach\reference"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

def pdf_to_png(pid):
    """render any PDF in the product folder to page PNGs (needs pymupdf)."""
    import pymupdf
    made = []
    for src in sorted(glob.glob(os.path.join(REF, pid, "*.pdf"))):
        doc = pymupdf.open(src)
        stem = os.path.splitext(src)[0]
        for i, page in enumerate(doc):
            out = "%s_p%02d.png" % (stem, i + 1)
            if not os.path.exists(out):
                page.get_pixmap(dpi=72).save(out)
            made.append(out)
    return made

def parts(pid):
    """capture files in stitch order: base first, then -2, -3 ..."""
    if glob.glob(os.path.join(REF, pid, "*.pdf")):
        pdf_to_png(pid)
    fs = glob.glob(os.path.join(REF, pid, "*.png"))
    def key(f):
        b = os.path.splitext(os.path.basename(f))[0]
        if "_p" in b and b.rsplit("_p", 1)[-1].isdigit():
            return int(b.rsplit("_p", 1)[-1])
        tail = b.rsplit("-", 1)[-1]
        return int(tail) if tail.isdigit() and len(tail) <= 2 else 1
    return sorted(fs, key=key)

def load(pid):
    ims = [Image.open(f).convert("RGB") for f in parts(pid)]
    w = max(i.width for i in ims)
    H = sum(i.height for i in ims)
    full = Image.new("RGB", (w, H), "white")
    y = 0
    for i in ims:
        full.paste(i, (0, y)); y += i.height
    return full

def profile(full, band=40):
    """per-band mean brightness + dark-pixel fraction, pure PIL."""
    g = full.convert("L")
    H = g.height
    nb = H // band
    small  = g.resize((1, nb), Image.BOX)                       # mean brightness
    darkim = g.point(lambda v: 255 if v < 110 else 0)
    dark   = darkim.resize((1, nb), Image.BOX)                  # dark fraction * 255
    return [(i * band, small.getpixel((0, i)), dark.getpixel((0, i)) / 255.0)
            for i in range(nb)]

def contact(pid, full, col_orig=6000, colw=260):
    s = colw / full.width
    sh = int(full.height * s)
    small = full.resize((colw, sh), Image.LANCZOS)
    colh = int(col_orig * s)
    ncol = (sh + colh - 1) // colh
    gap = 10
    sheet = Image.new("RGB", (ncol * (colw + gap) - gap, colh), "#cccccc")
    for c in range(ncol):
        box = small.crop((0, c * colh, colw, min((c + 1) * colh, sh)))
        sheet.paste(box, (c * (colw + gap), 0))
    p = os.path.join(OUT, "sheet_%s.png" % pid)
    sheet.save(p)
    return p, ncol, col_orig

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        for pid in sys.argv[2:]:
            f = load(pid)
            p, ncol, co = contact(pid, f)
            print("%s  full=%dx%d  sheet=%s  cols=%d each=%dpx" %
                  (pid, f.width, f.height, os.path.basename(p), ncol, co))
    elif cmd == "prof":
        pid = sys.argv[2]
        f = load(pid)
        rows = profile(f)
        # text-likely band: bright background, sparse dark pixels
        runs, cur = [], None
        for y, mean, dk in rows:
            hit = mean > 225 and 0.004 < dk < 0.14
            if hit and cur is None: cur = [y, y]
            elif hit: cur[1] = y
            elif cur: runs.append(cur); cur = None
        if cur: runs.append(cur)
        print("full height", f.height)
        for a, b in runs:
            if b - a >= 80: print("TEXT? %6d - %6d  (%d px)" % (a, b + 40, b - a + 40))
    elif cmd == "crop":
        pid, y0, y1 = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        f = load(pid)
        c = f.crop((0, y0, f.width, min(y1, f.height)))
        if c.width > 1400:
            c = c.resize((1400, int(c.height * 1400 / c.width)), Image.LANCZOS)
        p = os.path.join(OUT, "crop_%s_%d_%d.png" % (pid, y0, y1))
        c.save(p); print(p, c.size)
