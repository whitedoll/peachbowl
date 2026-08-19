# peachbowl

네이버 스마트스토어 **피치보울** 상품 상세페이지를 사진과 짧은 설명만으로 생성하는
Claude Code 스킬과 그 산출물.

## 구조

```
.claude/skills/detail-page/     상세페이지 생성 스킬
├─ SKILL.md                     작업 순서 (학습 모드 / 생성 모드)
├─ assets/template.html         860px 단일 HTML 템플릿, 인라인 CSS만
├─ references/
│  ├─ brand-voice.md            문체·카피 규칙 (기존 상품 15개 분석)
│  ├─ visual-style.md           촬영·연출·레이아웃 규칙 (사진 색분포 측정 포함)
│  ├─ compliance.md             표시광고법 금지 표현 + 상품정보제공고시
│  ├─ copywriting.md            섹션별 기본 작법
│  └─ learn-brand-voice.md      기존 페이지에서 톤을 학습하는 절차
└─ scripts/
   ├─ prep_images.py            사진 폴더 → 색인 대지 → 역할별 배치
   ├─ read_capture.py           초장축 캡처·PDF 를 잘라 읽기
   └─ embed_images.py           이미지를 base64 로 내장해 자립형 HTML 생성

output/                         생성된 상세페이지
reference/                      원본 캡처·상품 사진 (용량 때문에 git 제외)
```

## 규칙 우선순위

```
compliance.md (금지 표현)  >  brand-voice.md (브랜드 톤)  >  copywriting.md (기본 작법)
```

## 사용

Claude Code 에서 상품 사진과 설명을 주고 상세페이지를 요청하면 `detail-page` 스킬이 실행된다.

```bash
# 1. 사진 훑어보기 — 번호 찍힌 색인 대지를 만든다
python .claude/skills/detail-page/scripts/prep_images.py grid <사진폴더>

# 2. 역할별로 배치 (가로 860px 로 리사이즈)
python .claude/skills/detail-page/scripts/prep_images.py place <사진폴더> output/<슬러그>/img \
  key=1 point1=12 model-g1=2 detail1=17

# 3. 이미지를 내장한 단일 HTML 생성
python .claude/skills/detail-page/scripts/embed_images.py \
  output/<슬러그>/index.html output/<슬러그>/standalone.html
```

`index.html` 은 상대경로 작업본, `standalone.html` 은 전달·캡처용이다.
미리보기 창은 HTML 을 `data:` URL 로 띄우기 때문에 상대경로가 깨진다 — 확인할 때는
`standalone.html` 을 쓰거나 로컬 HTTP 서버로 연다.

```bash
cd output && python -m http.server 8765 --bind 127.0.0.1
```

## 산출물

| 폴더 | 내용 |
|---|---|
| `output/bali-three-piece-bikini/` | 발리 쓰리피스 비키니 — 브랜드 톤 그대로 |
| `output/bali-three-piece-bikini-v2/` | 같은 상품 — `copywriting` 스킬 적용 (HOW TO WEAR 3단계 + Q&A 추가) |

## 의존성

```bash
python -m pip install Pillow pymupdf
```

`pymupdf` 는 PDF 형태의 캡처를 읽을 때만 필요하다.
한글 라벨 렌더링에 `C:\Windows\Fonts\malgun.ttf` 를 사용한다.
