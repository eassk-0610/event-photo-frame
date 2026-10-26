"""app.html から本番公開用の docs/index.html を生成する（GitHub Pages は docs/ を配信する）: python3 tools/build.py

- Google Fonts の読み込みを外し、docs/fonts/fonts.css（tools/fetch_fonts.py で作成）があればそれを使う。
  無ければ端末標準フォントで表示する。どちらの場合も外部サーバーへの通信は発生しない。
- インラインの <style> と <script> の SHA-256 ハッシュで許可する Content-Security-Policy を付ける。
  app.html を編集したら必ずこのスクリプトを実行し直すこと（ハッシュが変わるため）。
"""
import base64
import hashlib
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "app.html").read_text(encoding="utf-8")

font_links = re.findall(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\n?', src)
if len(font_links) != 3:
    raise SystemExit(f"Google Fonts の <link> が想定の3行ではありません（{len(font_links)}行）")
self_hosted = (root / "docs" / "fonts" / "fonts.css").exists()
for i, link in enumerate(font_links):
    replacement = '<link rel="stylesheet" href="fonts/fonts.css">\n' if self_hosted and i == len(font_links) - 1 else ""
    src = src.replace(link, replacement, 1)


def sha(tag):
    bodies = re.findall(rf"<{tag}>(.*?)</{tag}>", src, re.S)
    if len(bodies) != 1:
        raise SystemExit(f"<{tag}> が1つではありません")
    return "'sha256-" + base64.b64encode(hashlib.sha256(bodies[0].encode("utf-8")).digest()).decode() + "'"


if re.search(r"\sstyle=\"", src) or re.search(r"\son[a-z]+=\"", src):
    raise SystemExit("style 属性やインラインのイベント属性は CSP で拒否されるため使わないでください")

csp = "; ".join([
    "default-src 'none'",
    f"script-src {sha('script')}",
    f"style-src 'self' {sha('style')}",
    "font-src 'self'",
    "img-src 'self' data: blob:",
    "media-src 'self' blob:",
    "connect-src 'none'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
])

head = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#111213">
</head>
<body>
"""
(root / "docs" / "index.html").write_text(head + src + "\n</body>\n</html>\n", encoding="utf-8")
print("index.html を生成しました（フォント: " + ("セルフホスト" if self_hosted else "端末標準 ※tools/fetch_fonts.py 未実行") + "）")
