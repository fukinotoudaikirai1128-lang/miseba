#!/usr/bin/env python3
"""ミセバのサイトのQRコードを単体で書き出す。

  python3 scripts/make_qr.py              config.json の publish.site_url から作る
  python3 scripts/make_qr.py <URL>        指定したURLから作る

チラシ以外（名刺・ポスター・SNSなど）に貼りたいときに使う。
SVG（拡大しても荒れない・印刷向き）と PNG（貼り付け向き）の両方を出す。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_postcard import qr_svg, load_config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        cfg = load_config()
        url = (cfg.get("publish", {}).get("site_url") or "").rstrip("/")
        if not url:
            sys.exit("エラー: config.json の publish.site_url が空です。")

    OUT.mkdir(parents=True, exist_ok=True)

    # --- SVG（印刷向き）---
    svg = qr_svg(url, size_mm=60)
    svg_path = OUT / "qr-miseba.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"✅ SVG: {svg_path}")

    # --- PNG（貼り付け向き）---
    png_path = OUT / "qr-miseba.png"
    try:
        import qrcode
        q = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=20, border=3,
        )
        q.add_data(url)
        q.make(fit=True)
        q.make_image(fill_color="black", back_color="white").save(png_path)
        print(f"✅ PNG: {png_path}")
    except Exception as e:
        print(f"   PNGは作れませんでした（{e}）。SVGを使ってください。")

    print(f"\n読み取り先: {url}")
    print("印刷するときは 2cm 角より小さくしないこと。読み取れなくなります。")


if __name__ == "__main__":
    main()
