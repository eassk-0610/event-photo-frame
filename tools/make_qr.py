"""会場掲示用のQRコードと A4 ポスター画像を qr/ に作る。

    python3 tools/make_qr.py [URL]

必要なライブラリ: segno, pillow（検証用に zxing-cpp があれば読み取りテストも行う）
URL を省略すると GitHub Pages の公開URLを使う。
"""
import pathlib
import sys

import segno
from PIL import Image, ImageDraw, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "https://eassk-0610.github.io/event-photo-frame/"
TITLE = "フォトフレームで記念撮影"
STEPS = [
    "スマホのカメラでQRコードを読み取る",
    "フレームを選んで撮影する",
    "写真に保存して、SNSでシェア",
]
NOTE = "写真は端末の中だけで処理され、外部には送信されません。"
COLORS = ["#e8432e", "#f6b81c", "#2f8f5b", "#2c5fb8", "#e86fa2"]
INK = "#1d1d1f"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REG = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "qr"
out.mkdir(exist_ok=True)

# 誤り訂正レベル Q（約25%の汚れ・欠けまで読める）。印刷物向け
qr = segno.make(URL, error="q", micro=False)
qr.save(out / "qr.svg", scale=10, border=4, dark=INK)
qr.save(out / "qr.png", scale=40, border=4, dark=INK)

# ---- A4 ポスター（300dpi: 2480×3508） ----
W, H = 2480, 3508
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
bold = lambda s: ImageFont.truetype(FONT_BOLD, s)
reg = lambda s: ImageFont.truetype(FONT_REG, s)


def center(y, text, font, fill=INK):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)


# 上下の色帯
band = W / len(COLORS)
for i, c in enumerate(COLORS):
    d.rectangle([i * band, 0, (i + 1) * band, 60], fill=c)
    d.rectangle([i * band, H - 60, (i + 1) * band, H], fill=c)

center(260, TITLE, bold(150))
center(470, "アプリのインストールは不要です", reg(72), "#5c5a57")

qr_size = 1500
qr_img = Image.open(out / "qr.png").convert("RGB").resize((qr_size, qr_size), Image.NEAREST)
qy = 680
img.paste(qr_img, ((W - qr_size) // 2, qy))

# URL を文字でも載せる（QRのすり替えに気づけるように）
center(qy + qr_size + 40, URL, bold(64))

y = qy + qr_size + 230
for i, step in enumerate(STEPS):
    x = 420
    r = 62
    d.ellipse([x - r, y - 8, x + r, y - 8 + 2 * r], fill=COLORS[i % len(COLORS)])
    n = str(i + 1)
    f = bold(80)
    d.text((x - d.textlength(n, font=f) / 2, y + 2), n, font=f, fill="white")
    d.text((x + 120, y + 8), step, font=bold(84), fill=INK)
    y += 210

center(H - 300, NOTE, reg(54), "#5c5a57")
center(H - 210, "QRコードの上にシールなどが貼られていないか、ご確認ください。", reg(46), "#8a8884")
img.save(out / "poster-a4.png", dpi=(300, 300))

# 読み取りテスト
try:
    import zxingcpp

    for name in ["qr.png", "poster-a4.png"]:
        texts = [r.text for r in zxingcpp.read_barcodes(Image.open(out / name))]
        status = "OK" if URL in texts else f"NG {texts}"
        print(f"{name}: 読み取り {status}")
except ImportError:
    print("zxing-cpp が無いため読み取りテストは省略しました")
print(f"qr/ に qr.svg, qr.png, poster-a4.png を書き出しました（{URL}）")
