#!/usr/bin/env python3
"""ミセバのサイトに載せる「業種ごとの見本ページ」を作る。

  python3 scripts/make_demos.py

実在の店は一切使わない。店名は「会社名」、住所や電話番号もプレースホルダーのまま。
そうすることで、
- 実在の店と間違われない（不正競争防止法・混同惹起の心配がない）
- どの業種のお店にも「あなたのお店ならここに名前が入ります」と説明できる

出力: docs/demo/<業種キー>/index.html
"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "demo"

# 業種ごとの見本データ。実在しない値だけを使う。
DEMOS = {
    "roofing": {
        "order": 1,
        "nav": "屋根工事",
        "reviews": [
            "雨漏りをすぐに見に来てくれました。連絡してから来ていただくまでが早くて助かりました。",
            "見積もりの内訳が分かりやすく、追加の請求もありませんでした。",
            "作業のあと、屋根まわりの掃除まで丁寧にしてくださいました。",
        ],
        "hours": ["月〜金 8:00〜18:00", "土 8:00〜17:00", "日曜・祝日 定休"],
    },
    "plumbing": {
        "order": 2,
        "nav": "水道工事",
        "reviews": [
            "夜に水漏れで困っていたところ、翌朝すぐに来てくださいました。",
            "何が原因かを実際に見せながら説明してもらえて、納得できました。",
            "古い蛇口の交換もその場で対応していただけました。",
        ],
        "hours": ["月〜土 8:00〜19:00", "日曜 定休", "急ぎのご相談はお電話ください"],
    },
    "construction": {
        "order": 3,
        "nav": "工務店",
        "reviews": [
            "小さな修繕でも嫌な顔ひとつせず引き受けてくださいました。",
            "予算の相談に乗ってもらえて、無理のない形にまとめてもらえました。",
            "工事の前に手順を説明してくれるので安心してお任せできました。",
        ],
        "hours": ["月〜金 8:00〜18:00", "土 8:00〜17:00", "日曜・祝日 定休"],
    },
    "electrical": {
        "order": 4,
        "nav": "電気工事",
        "reviews": [
            "コンセントの増設をお願いしました。仕上がりがきれいで満足しています。",
            "照明の交換を頼んだら、その場ですぐ終わりました。",
            "見積もりから工事まで、やりとりが早くて助かりました。",
        ],
        "hours": ["月〜金 8:00〜18:00", "土 9:00〜17:00", "日曜・祝日 定休"],
    },
    "relaxation": {
        "order": 5,
        "nav": "リラクゼーション",
        "reviews": [
            "強さをこまめに聞いてくださるので、心地よく過ごせました。",
            "店内が静かで清潔で、ゆっくりできました。",
            "肩まわりが軽くなった気がします。また伺います。",
        ],
        "hours": ["月〜土 10:00〜20:00", "日曜・祝日 10:00〜18:00", "最終受付は閉店1時間前"],
    },
}

BANNER = """<div class="demo-flag">
  <strong>これは見本です。</strong>実在するお店ではありません。
  <b>会社名</b>・住所・電話番号は、実際のご依頼ではお店のものに置き換わります。
  <a href="../../">ミセバのサイトへ戻る</a>
</div>
"""

BANNER_CSS = """.demo-flag{background:#101C26;color:#F6F2EA;padding:12px 20px;font-size:.84rem;
  line-height:1.75;text-align:center;letter-spacing:.02em}
.demo-flag strong{color:#E7D9BF}
.demo-flag b{background:rgba(231,217,191,.18);padding:1px 7px;border-radius:3px;font-weight:700}
.demo-flag a{color:#E7D9BF;font-weight:700;white-space:nowrap}
"""


def make_info(key, demo):
    """見本用の info.json を組み立てる。すべてプレースホルダー。"""
    return {
        "slug": f"demo-{key}",
        "name": "会社名",
        "industry": key,
        "area": "〇〇市",
        "address": "〇〇県〇〇市〇〇町 1-2-3",
        "phone": "000-0000-0000",
        "rating": 4.8,
        "review_count": 15,
        "hours": demo["hours"],
        "review_highlights": demo["reviews"],
        "maps_url": "",
        "found_at": "",
        "status": "found",
        "_note": "★見本★ 実在しない。ミセバのサイトに業種ごとの作例として載せるためのもの。",
    }


def build_one(key, demo):
    slug = f"demo-{key}"
    pdir = ROOT / "prospects" / slug
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "info.json").write_text(
        json.dumps(make_info(key, demo), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    build_site.build(slug)

    src = pdir / "site" / "index.html"
    h = src.read_text(encoding="utf-8")

    # 見本と分かるようにする
    h = h.replace("</style>", BANNER_CSS + "</style>", 1)
    h = h.replace("<body>", "<body>\n" + BANNER, 1)
    h = h.replace("<title>", "<title>【見本】", 1)

    # 「〇〇市を中心に対応しております。」だと不自然なので言い換える
    h = h.replace("〇〇市を中心に対応しております。",
                  "お店のある地域を中心に対応しております。")

    dest = OUT / key
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(h, encoding="utf-8")
    return dest / "index.html"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for key, demo in sorted(DEMOS.items(), key=lambda kv: kv[1]["order"]):
        if key not in build_site.INDUSTRY:
            print(f"  ★ {key} は build_site.py に定義がありません。飛ばします。")
            continue
        path = build_one(key, demo)
        label = build_site.INDUSTRY[key]["label"]
        made.append((key, label, path))
        print(f"  ✅ {label:14s} → {path.relative_to(ROOT)}")

    print(f"\n{len(made)}件の見本を作りました。")
    print("ミセバのサイト（docs/index.html）の作例タブから開けます。")


if __name__ == "__main__":
    main()
