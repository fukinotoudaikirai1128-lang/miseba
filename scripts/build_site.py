#!/usr/bin/env python3
"""info.json から試作サイトの「骨組み＋デザイン＋画像」までを一気に埋める補助スクリプト。

これは new-preview スキルの STEP1〜3 を機械的に済ませるためのもの。
STEP4（文言の作り込み）と STEP5（最終チェック）は Claude が手で行う。

  python3 scripts/build_site.py <slug>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# CLAUDE.md §2-1 の業種カラー
INDUSTRY = {
    "roofing": {
        "label": "屋根工事店", "main": "#1B4965", "accent": "#F4A261", "bg": "#F8F9FA",
        "hero": "https://images.unsplash.com/photo-1632759145351-1d592919f522?w=1600&q=80",
        "headline": "雨漏り・屋根の傷み、\nそのままにしていませんか",
        "sub": "小さな不具合のうちにご相談いただければ、費用も工期も抑えられます。まずはお気軽にお電話ください。",
        "troubles": ["天井にシミができてきた", "屋根の瓦がずれている気がする",
                     "台風のあと、様子が気になる", "そろそろ点検した方がいいか分からない"],
        "services": [
            ("屋根の点検・診断", "気になるところを実際に見て、状態をお伝えします。",
             "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800&q=80"),
            ("雨漏りの修理", "原因を特定したうえで、必要な範囲を修理します。",
             "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"),
            ("屋根の葺き替え・補修", "傷みが進んでいる場合の張り替えにも対応します。",
             "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800&q=80"),
        ],
    },
    "plumbing": {
        "label": "水道工事店", "main": "#0077B6", "accent": "#00B4D8", "bg": "#F8FBFD",
        "hero": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=1600&q=80",
        "headline": "水まわりのトラブル、\nすぐに駆けつけます",
        "sub": "つまり・水漏れ・蛇口の交換など、暮らしの水まわりのことならご相談ください。",
        "troubles": ["トイレや排水口がつまった", "蛇口から水がぽたぽた落ちる",
                     "お湯が出にくくなった", "水道代が急に高くなった"],
        "services": [
            ("つまりの解消", "トイレ・台所・浴室の排水のつまりに対応します。",
             "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=800&q=80"),
            ("水漏れの修理", "蛇口・配管からの水漏れを調べて修理します。",
             "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=800&q=80"),
            ("機器の交換・取付", "蛇口や給湯設備の交換もご相談ください。",
             "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&q=80"),
        ],
    },
    "construction": {
        "label": "工務店", "main": "#3E2723", "accent": "#8D6E63", "bg": "#FAF7F2",
        "hero": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=1600&q=80",
        "headline": "住まいのことは、\n地元の工務店へ",
        "sub": "小さな修繕から間取りの見直しまで、住まいのご相談を承ります。",
        "troubles": ["ドアや床のきしみが気になる", "水まわりを新しくしたい",
                     "収納を増やしたい", "どこに頼めばいいか分からない"],
        "services": [
            ("リフォーム", "キッチン・浴室・お部屋の改修に対応します。",
             "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80"),
            ("修繕・メンテナンス", "小さな傷みのうちの手当てもお任せください。",
             "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&q=80"),
            ("お住まいのご相談", "何から始めるかの段階からご相談いただけます。",
             "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80"),
        ],
    },
    "electrical": {
        "label": "電気工事店", "main": "#264653", "accent": "#E9C46A", "bg": "#F8F9FA",
        "hero": "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=1600&q=80",
        "headline": "電気のこと、\n安心してお任せください",
        "sub": "コンセントの増設から照明の交換まで、暮らしの電気工事を承ります。",
        "troubles": ["ブレーカーがよく落ちる", "コンセントを増やしたい",
                     "照明を新しくしたい", "配線が古くなってきた"],
        "services": [
            ("配線・コンセント工事", "増設や移設のご相談に対応します。",
             "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"),
            ("照明の交換・取付", "LED化や器具の交換も承ります。",
             "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=800&q=80"),
            ("設備の点検", "気になる箇所の点検を行います。",
             "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&q=80"),
        ],
    },
    "clinic": {
        "label": "整体院", "main": "#00897B", "accent": "#4DB6AC", "bg": "#E8F5E9",
        "hero": "https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?w=1600&q=80",
        "headline": "つらい肩こり・腰痛、\n我慢していませんか",
        "sub": "お身体の状態をうかがったうえで、無理のない施術を行います。",
        "troubles": ["肩や首のこりがとれない", "腰が重い日が続いている",
                     "デスクワークで姿勢が気になる", "眠りが浅い"],
        "services": [
            ("肩こり・首のこり", "こりの元になっている部分から整えていきます。",
             "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800&q=80"),
            ("腰の不調", "日常の動作を伺いながら施術します。",
             "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?w=800&q=80"),
            ("姿勢のご相談", "普段の姿勢についてもご相談いただけます。",
             "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&q=80"),
        ],
    },
}


def stars(rating) -> str:
    if rating is None:
        return ""
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    return "★" * full + ("☆" if half else "") + "☆" * (5 - full - half)


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build(slug: str) -> Path:
    pdir = ROOT / "prospects" / slug
    info_path = pdir / "info.json"
    if not info_path.exists():
        sys.exit(f"エラー: {info_path} がありません。先に find-prospects を実行してください。")

    info = json.loads(info_path.read_text(encoding="utf-8"))
    ind = INDUSTRY.get(info.get("industry", "roofing"), INDUSTRY["roofing"])

    tpl = (ROOT / "templates" / "base" / "index.html").read_text(encoding="utf-8")

    # --- 差し込むパーツを組み立てる ---
    troubles = "\n        ".join(f"<li>{esc(t)}</li>" for t in ind["troubles"])

    cards = []
    for title, desc, img in ind["services"]:
        cards.append(
            f'<div class="card">\n'
            f'          <img src="{img}" alt="{esc(title)}のイメージ" loading="lazy">\n'
            f'          <div class="card-body"><h3>{esc(title)}</h3><p>{esc(desc)}</p></div>\n'
            f'        </div>'
        )
    service_cards = "\n        ".join(cards)

    voices = []
    for v in (info.get("review_highlights") or [])[:4]:
        voices.append(
            f'<div class="voice"><p>{esc(v)}</p>'
            f'<cite>Googleマップの口コミより</cite></div>'
        )
    voice_items = "\n        ".join(voices) if voices else \
        '<div class="voice"><p>口コミは準備中です。</p></div>'

    hours = info.get("hours") or []
    hours_html = "<br>".join(esc(h) for h in hours) if hours else "お問い合わせください"

    # 住所から市区町村を推定（それ以外の対応エリアは書かない）
    m = re.search(r"([^\s]+?[市区町村])", info.get("address", ""))
    area = m.group(1) if m else ""

    phone = info.get("phone", "")
    phone_raw = re.sub(r"[^\d+]", "", phone)

    repl = {
        "{{SHOP_NAME}}": esc(info.get("name", "")),
        "{{AREA}}": esc(area),
        "{{INDUSTRY_LABEL}}": ind["label"],
        "{{ADDRESS}}": esc(info.get("address", "")),
        "{{PHONE}}": esc(phone),
        "{{PHONE_RAW}}": phone_raw,
        "{{HOURS}}": hours_html,
        "{{RATING}}": str(info.get("rating", "")),
        "{{STARS}}": stars(info.get("rating")),
        "{{REVIEW_COUNT}}": str(info.get("review_count", "")),
        "{{COLOR_MAIN}}": ind["main"],
        "{{COLOR_ACCENT}}": ind["accent"],
        "{{COLOR_BG}}": ind["bg"],
        "{{HERO_IMAGE}}": ind["hero"],
        "{{HERO_HEADLINE}}": ind["headline"].replace("\n", "<br>"),
        "{{HERO_SUB}}": ind["sub"],
        "{{TROUBLE_ITEMS}}": troubles,
        "{{SERVICES_LEAD}}": f"{area}を中心に対応しております。" if area else "お気軽にご相談ください。",
        "{{SERVICE_CARDS}}": service_cards,
        "{{VOICE_ITEMS}}": voice_items,
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    left = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
    if left:
        print(f"  警告: 未置換のプレースホルダーが残っています: {set(left)}")

    site = pdir / "site"
    site.mkdir(parents=True, exist_ok=True)
    out = site / "index.html"
    out.write_text(tpl, encoding="utf-8")

    info["status"] = "site_draft"
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 scripts/build_site.py <slug>")
    p = build(sys.argv[1])
    print(f"生成しました: {p}")
    print("次: Claude が STEP4(文言の作り込み) と STEP5(最終チェック) を行ってください。")
