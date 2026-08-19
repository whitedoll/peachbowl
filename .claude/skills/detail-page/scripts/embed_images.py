"""HTML 안의 로컬 이미지를 base64 로 인라인해 자립형 단일 파일로 만든다.

    python scripts/embed_images.py <입력.html> [출력.html]

출력을 생략하면 <입력>_standalone.html 로 저장한다.

왜 필요한가: 미리보기 창이나 채팅으로 전달된 HTML 은 data: URL 로 렌더링되므로
`./img/x.jpg` 같은 상대경로가 해석되지 않는다. 파일 탐색기에서 직접 열면 보이지만,
그 외 경로에서는 전부 깨진 이미지로 나온다. 내장하면 어디서 열어도 동일하게 보인다.
"""
import base64, os, re, sys

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}


def embed(src, dst=None):
    base = os.path.dirname(os.path.abspath(src))
    html = open(src, encoding="utf-8").read()
    done, missing, total = [], [], [0]

    def repl(m):
        pre, url, post = m.group(1), m.group(2), m.group(3)
        if url.startswith(("data:", "http://", "https://", "//")):
            return m.group(0)
        total[0] += 1
        path = os.path.normpath(os.path.join(base, url))
        ext = os.path.splitext(path)[1].lower()
        if not os.path.isfile(path) or ext not in MIME:
            missing.append(url)
            return m.group(0)
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        done.append((url, len(b64)))
        return "%sdata:%s;base64,%s%s" % (pre, MIME[ext], b64, post)

    html = re.sub(r'(\bsrc=")([^"]+)(")', repl, html)
    html = re.sub(r'(url\(\s*[\'"]?)([^\'")]+)([\'"]?\s*\))', repl, html)

    dst = dst or os.path.splitext(src)[0] + "_standalone.html"
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    mb = os.path.getsize(dst) / 1024 / 1024
    print("내장 %d/%d장  ->  %s  (%.1f MB)" % (len(done), total[0], dst, mb))
    for u in missing:
        print("  [누락] %s" % u)
    if mb > 15:
        print("  ! 15MB 초과. 원본 이미지를 가로 860px 로 리사이즈한 뒤 다시 실행할 것.")
    return dst


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    embed(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
