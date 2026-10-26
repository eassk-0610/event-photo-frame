"""Google Fonts のフォントを docs/fonts/ にダウンロードし、セルフホスト用の docs/fonts/fonts.css を作る。

本番ページから Google への通信をなくすために使う（来場者の IP などを外部に渡さない）。
フォントを変えたときだけ実行する: python3 tools/fetch_fonts.py
"""
import pathlib
import re
import time
import urllib.error
import urllib.request

CSS_URL = "https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@500;700;900&display=swap"
# woff2 版の CSS を返してもらうため、新しめのブラウザの UA を名乗る
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ALLOWED_HOST = "https://fonts.gstatic.com/"

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "docs" / "fonts"
out.mkdir(parents=True, exist_ok=True)


def get(url, retries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries:
                raise SystemExit(f"\nダウンロードに失敗しました（{e}）。再実行すると続きから取得します")
            time.sleep(2 * (attempt + 1))


css = get(CSS_URL).decode("utf-8")
urls = sorted(set(re.findall(r"url\((https://[^)]+)\)", css)))
for i, url in enumerate(urls):
    if not url.startswith(ALLOWED_HOST) or not url.endswith(".woff2"):
        raise SystemExit(f"想定外の URL を含むため中止します: {url}")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", url[len(ALLOWED_HOST):])
    path = out / name
    if not path.exists():
        path.write_bytes(get(url))
    css = css.replace(f"url({url})", f"url({name})")
    if (i + 1) % 50 == 0 or i + 1 == len(urls):
        print(f"{i + 1}/{len(urls)}")
(out / "fonts.css").write_text(css, encoding="utf-8")
print(f"\nfonts/fonts.css と {len(urls)} 個のフォントファイルを書き出しました")
