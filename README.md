# イベント用フォトフレーム

QRコードから開いて、スマホのカメラにイベント用フレームを重ねて撮影・保存・シェアできるWebページです。アプリのインストールは不要です。写真は端末の中だけで合成し、外部には送信しません。

公開URL: https://eassk-0610.github.io/event-photo-frame/

## ファイル構成

- `app.html` … 編集用のソース。イベント名・ハッシュタグ・フレームはファイル内の `CONFIG` で設定する
- `docs/` … GitHub Pages で配信するファイル（`tools/build.py` で生成）
  - `index.html` … 本番ページ（CSP 付き）
  - `fonts/` … セルフホストのフォント（Zen Kaku Gothic New, SIL OFL 1.1 / `fonts/OFL.txt`）
  - `frames/` … 作家素材のフレーム（1080×1920 の透過PNG）
  - `_headers` … Cloudflare Pages / Netlify に移す場合のセキュリティヘッダー
- `tools/build.py` … `app.html` から `docs/index.html` を生成する
- `tools/fetch_fonts.py` … フォントを `docs/fonts/` にダウンロードする

## 更新の手順

```sh
# app.html を編集したら必ず実行（CSP のハッシュが変わるため）
python3 tools/build.py
# 動作確認（http://localhost:8000 を開く）
python3 -m http.server 8000 --directory docs
```

フレームを追加するときは、PNG を `docs/frames/` に置き、`CONFIG.frames` に `{ id: "artist-a", name: "作家A", src: "frames/artist-a.png" }` を追加する。
