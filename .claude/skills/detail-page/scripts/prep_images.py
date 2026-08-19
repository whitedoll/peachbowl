"""상품 사진 폴더를 훑어보고, 역할별로 이름 붙여 배치한다.

1) 색인 대지 만들기 — 사진 수십 장을 한 장으로 압축해서 한 번에 분류한다

    python scripts/prep_images.py grid <사진폴더> [출력.png]

   격자 칸마다 번호가 찍힌다. 이 대지 한 장만 Read 로 열면 전부 분류할 수 있다.
   사진 한 장씩 Read 로 여는 것은 낭비다 — 대지로 먼저 훑고, 애매한 것만 개별로 본다.

2) 역할별 배치 — 분류 결과대로 리사이즈해서 복사한다

    python scripts/prep_images.py place <사진폴더> <출력폴더> key=1 point1=12 model1=5 ...

   번호는 grid 에서 본 그 번호(1부터)다. 가로 860px 로 줄여 저장하므로
   원본을 그대로 쓰는 것보다 최종 HTML 이 훨씬 가벼워진다.

역할 이름 규칙 (템플릿의 img 경로와 맞춘다)
    key            최상단 히어로 컷 1장
    point1~4       Peachy Point 라벨이 붙은 소구점 컷
    color-<이름>   컬러별 대표컷
    model-<접두><n> 연출컷
    detail<n>      플랫레이·클로즈업
"""
import os, sys, glob
from PIL import Image, ImageDraw, ImageFont

WIDTH = 860
EXT = ("*.png", "*.jpg", "*.jpeg", "*.webp")
FONT = r"C:\Windows\Fonts\malgun.ttf"      # 한글 라벨용. 기본 폰트는 한글이 깨진다


def files(folder):
    out = []
    for e in EXT:
        out += glob.glob(os.path.join(folder, e))
    return sorted(out)


def grid(folder, dst=None, cols=6, tw=330):
    fs = files(folder)
    if not fs:
        print("이미지 없음:", folder); return
    font = ImageFont.truetype(FONT, 30) if os.path.exists(FONT) else ImageFont.load_default()
    thumbs = []
    for f in fs:
        im = Image.open(f).convert("RGB")
        thumbs.append(im.resize((tw, int(im.height * tw / im.width)), Image.LANCZOS))
    th = max(t.height for t in thumbs)
    rows = (len(fs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) - 8, rows * (th + 42) - 8), "#fff")
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(thumbs):
        x, y = (i % cols) * (tw + 8), (i // cols) * (th + 42)
        d.rectangle([x, y, x + tw, y + th + 38], fill="#F4F2F0")
        sheet.paste(t, (x, y + 38))
        d.text((x + 10, y + 4), "%02d" % (i + 1), font=font, fill="#111")
    dst = dst or os.path.join(folder, "_grid.png")
    sheet.save(dst)
    print("대지 %s  (%d장, %dx%d)" % (dst, len(fs), *sheet.size))
    for i, f in enumerate(fs, 1):
        print("  %02d  %s" % (i, os.path.basename(f)))


def place(folder, outdir, pairs):
    fs = files(folder)
    os.makedirs(outdir, exist_ok=True)
    used = set()
    for p in pairs:
        if "=" not in p:
            print("건너뜀(형식 오류):", p); continue
        role, idx = p.split("=", 1)
        try:
            src = fs[int(idx) - 1]
        except (ValueError, IndexError):
            print("건너뜀(번호 없음): %s -> %s" % (p, idx)); continue
        im = Image.open(src).convert("RGB")
        if im.width != WIDTH:
            im = im.resize((WIDTH, int(im.height * WIDTH / im.width)), Image.LANCZOS)
        dst = os.path.join(outdir, role + ".jpg")
        im.save(dst, quality=88, optimize=True)
        used.add(int(idx))
        print("  %-14s <- %02s  %s  (%dx%d)" % (role + ".jpg", idx, os.path.basename(src)[:28], *im.size))
    unused = [i for i in range(1, len(fs) + 1) if i not in used]
    if unused:
        print("미사용: %s" % ", ".join("%02d" % i for i in unused))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "grid":
        grid(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "place":
        place(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        print(__doc__); sys.exit(1)
