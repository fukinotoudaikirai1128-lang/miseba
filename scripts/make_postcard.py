#!/usr/bin/env python3
"""はがきの文面と電話台本を作る。

使い方:
    python3 scripts/make_postcard.py <slug>            はがきを作る
    python3 scripts/make_postcard.py <slug> --phone    電話台本を作る

はがきは prospects/<slug>/postcard.html に出力されます。
ブラウザで開いて「印刷」→ 用紙サイズ「はがき(100×148mm)」→ 余白なし。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def load_info(slug):
    p = ROOT / "prospects" / slug / "info.json"
    if not p.exists():
        sys.exit(f"❌ {p} がありません。先に find-prospects で店を登録してください。")
    return json.loads(p.read_text(encoding="utf-8"))


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------- QRコード

def qr_svg(url, size_mm=23):
    """URLをQRコードのSVGにする。qrcode が無ければ自動で入れる。"""
    try:
        import qrcode
    except ImportError:
        print("… qrcode ライブラリを入れています")
        for args in (["pip", "install", "qrcode", "--quiet"],
                     ["pip", "install", "qrcode", "--quiet", "--break-system-packages"],
                     ["pip3", "install", "qrcode", "--quiet", "--break-system-packages"]):
            try:
                if subprocess.run(args, capture_output=True).returncode == 0:
                    break
            except FileNotFoundError:
                continue
        try:
            import qrcode
        except ImportError:
            return ('<div class="qr-missing">QRコードを作れませんでした<br>'
                    '<code>pip install qrcode</code> を実行してください</div>')

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=1, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    m = qr.get_matrix()
    n = len(m)

    rects = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                run = 1
                while x + run < n and row[x + run]:
                    run += 1
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1"/>')
                x += run
            else:
                x += 1

    return (f'<svg class="qr" viewBox="0 0 {n} {n}" width="{size_mm}mm" height="{size_mm}mm" '
            f'shape-rendering="crispEdges" role="img" aria-label="試作サイトのQRコード">'
            f'<rect width="{n}" height="{n}" fill="#fff"/>'
            f'<g fill="#000">{"".join(rects)}</g></svg>')


# ---------------------------------------------------------------- はがき

POSTCARD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>はがき｜{shop}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
<style>
@page {{ size: 100mm 148mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "Noto Sans JP", sans-serif; background: #ddd; }}
.card {{
  width: 100mm; height: 148mm; background: #fff; margin: 12px auto;
  padding: 6.5mm 6mm 5mm; display: flex; flex-direction: column;
  color: #1F2933; line-height: 1.62; overflow: hidden;
}}
.to {{ font-size: 3.1mm; color: #5B6670; margin-bottom: 1mm; }}
.shop {{ font-size: 4.2mm; font-weight: 700; margin-bottom: 3mm;
        border-bottom: 0.4mm solid #E8A33D; padding-bottom: 1.5mm; }}
h1 {{ font-size: 3.9mm; line-height: 1.5; margin-bottom: 2.5mm; color: #2D3E50; }}
p {{ font-size: 3mm; line-height: 1.62; margin-bottom: 2mm; }}
.qrbox {{ display: flex; gap: 3.5mm; align-items: center;
         background: #FBFAF8; border: 0.3mm solid #E6E2DC; border-radius: 2mm;
         padding: 2.5mm; margin: 0.5mm 0 2.5mm; }}
.qrbox .txt {{ font-size: 2.7mm; line-height: 1.5; }}
.qrbox .txt b {{ display: block; font-size: 3mm; color: #2D3E50; margin-bottom: 0.8mm; }}
.url {{ font-size: 2.3mm; color: #5B6670; word-break: break-all; margin-top: 0.8mm; }}
.qr-missing {{ font-size: 2.6mm; color: #b00; width: 24mm; }}
.price {{ font-size: 2.9mm; color: #2D3E50; font-weight: 700; margin-bottom: 2mm; }}
.opt {{ font-size: 2.5mm; line-height: 1.5; color: #5B6670; background: #F4F1EC;
       padding: 1.8mm 2.2mm; border-radius: 1.5mm; margin-bottom: 2.5mm; }}
footer {{ margin-top: auto; border-top: 0.3mm solid #E6E2DC; padding-top: 2mm;
         font-size: 2.7mm; line-height: 1.5; color: #5B6670;
         display: flex; align-items: center; justify-content: space-between; gap: 3mm; }}
footer b {{ color: #2D3E50; font-size: 3mm; }}
.lineqr {{ text-align: center; flex-shrink: 0; }}
.lineqr span {{ display: block; font-size: 2.2mm; color: #2D3E50; margin-top: .5mm; }}
@media print {{ body {{ background: #fff; }} .card {{ margin: 0; }} .note {{ display: none; }} }}
.note {{ max-width: 100mm; margin: 0 auto 16px; font-size: 12px; color: #444;
        background: #fff; padding: 10px 12px; border-radius: 6px; line-height: 1.7; }}
</style>
</head>
<body>

<div class="note">
  <b>印刷のしかた</b><br>
  Ctrl+P →「用紙サイズ: はがき(100×148mm)」→「余白: なし」→「背景のグラフィック」にチェック。<br>
  官製はがきの<b>通信面（宛名を書かない側）</b>に印刷してください。この案内は印刷されません。
</div>

<div class="card">
  <div class="to">{area}</div>
  <div class="shop">{shop} 御中</div>

  <h1>{shop}さんのホームページを、<br>試しに1ページだけ作ってみました。</h1>

  <p>突然のお便りで失礼いたします。Googleマップで{area}のお店を拝見し、
     ホームページが無いようでしたので、勝手ながら試作をお作りしました。</p>

  <div class="qrbox">
    {qr}
    <div class="txt">
      <b>こちらから見られます</b>
      スマホのカメラで読み取ってください。
      <div class="url">{url}</div>
    </div>
  </div>

  <p>AIを使った下書きです。写真も文章も差し替えられます。
     「いらない」と思われたら、そのまま捨てて構いません。</p>

  <div class="price">目安：制作 {setup}／公開後は月 {monthly}</div>

  <div class="opt">今後このようなお便りが不要でしたら、ご一報ください。
    二度とお送りせず、上記のページもすぐに削除いたします。</div>

  <footer>
    <div>
      <b>ミセバ</b>（個人事業）　{name}<br>
      {email}
    </div>
    {line_block}
  </footer>
</div>

</body>
</html>
"""


def yen(n):
    return f"{n:,}円"


def yen_range(lo, hi):
    """min と max が同じなら1つだけ表示する（「5万円〜5万円」を防ぐ）。"""
    return yen(lo) if lo == hi else f"{yen(lo)}〜{yen(hi)}"


def build_postcard(slug):
    cfg = load_config()
    info = load_info(slug)
    url = info.get("public_url")
    if not url:
        sys.exit("❌ public_url がありません。先に publish-preview で公開してください。")

    b, pr = cfg["brand"], cfg["outreach"]["pricing"]

    # LINEで相談できる場合は、フッターに小さなQRを入れる
    line_url = b.get("line_url", "")
    line_block = ""
    if line_url:
        line_block = (f'<div class="lineqr">{qr_svg(line_url, size_mm=15)}'
                      f'<span>LINEでご相談</span></div>')

    out = ROOT / "prospects" / slug / "postcard.html"
    out.write_text(POSTCARD.format(
        shop=esc(info.get("name", "")),
        area=esc(info.get("area") or cfg["search"]["area"]),
        url=esc(url),
        qr=qr_svg(url),
        line_block=line_block,
        setup=yen_range(pr['setup_min'], pr['setup_max']),
        monthly=yen_range(pr['monthly_min'], pr['monthly_max']),
        name=esc(b.get("contact_name", "")),
        email=esc(b.get("contact_email", "")),
    ), encoding="utf-8")

    print(f"✅ はがきを作りました: {out}")
    print("   ブラウザで開いて Ctrl+P → 用紙「はがき」→ 余白なし")
    print(f"   宛名面には手書きで: {info.get('address', '(住所が info.json にありません)')}")
    return out


# ---------------------------------------------------------------- 電話台本

PHONE = """# 電話台本 — {shop}

- 電話番号: **{phone}**
- 住所: {address}
- 試作サイト: {url}
- かける時間帯: 平日 10:00〜11:30 / 14:00〜16:00（昼と夕方は避ける）

---

## ★唯一のルール★

**その場で売らない。契約を取らない。**

用件は「試作ページを見てもらう方法を聞く」だけです。
売り込みを1文でも入れた瞬間に、詐欺の電話と同じ扱いになります。

---

## 台本

**① 名乗る（5秒）**

> お忙しいところ失礼いたします。**ミセバの{name}**と申します。
> 営業のお電話ではなく、確認のご連絡なのですが、少しだけよろしいでしょうか。

**② 用件（15秒）**

> Googleマップで{area}のお店を拝見していて、{shop}さんのホームページが
> 見当たらなかったものですから、勝手ながら**試しに1ページだけお作りしてみました**。
> 見ていただくだけでしたら無料ですので、URLをお伝えできればと思ってお電話しました。

**③ 相手に決めてもらう（ここで止める）**

> お送りするとしたら、はがきとメールと、どちらがよろしいでしょうか。

---

## 相手の反応別

| 相手 | 返し方 |
|---|---|
| 「見てみる」 | 「ありがとうございます。では〇〇でお送りします」→ **すぐ切る** |
| 「いらない」 | 「承知しました。失礼いたしました」→ **すぐ切る**。`do_not_contact: true` にする |
| 「いくらするの？」 | 「お作りするのが{setup}、公開後が月{monthly}です。まずは見ていただいてからで結構です」 |
| 「誰？怪しい」 | 「個人でやっております。{email} です。ご不審でしたらこのまま切っていただいて構いません」 |
| 「今忙しい」 | 「失礼しました。改めます」→ 切る。**かけ直さない** |
| 怒られた | 「申し訳ありませんでした」→ 切る。**その日の営業を全部止める** |

---

## 切ったあとにやること

`prospects/{slug}/outreach.md` に、日時・相手の反応・次にやることを書く。

## やってはいけないこと

- 「今だけ」「今日中なら」と期限を切る
- 「ホームページが無いと損してますよ」と弱点を突く
- 断られた相手にかけ直す
- 留守番電話に長いメッセージを残す（名前と用件だけ、20秒以内）
- **その場で「じゃあお願いします」を取る**（後で必ずもめます）
"""


def build_phone(slug):
    cfg = load_config()
    info = load_info(slug)
    b, pr = cfg["brand"], cfg["outreach"]["pricing"]
    out = ROOT / "prospects" / slug / "phone_script.md"
    out.write_text(PHONE.format(
        shop=info.get("name", ""),
        phone=info.get("phone", "(不明)"),
        address=info.get("address", "(不明)"),
        url=info.get("public_url", "(未公開)"),
        area=info.get("area") or cfg["search"]["area"],
        name=b.get("contact_name", ""),
        email=b.get("contact_email", ""),
        slug=slug,
        setup=yen_range(pr['setup_min'], pr['setup_max']),
        monthly=yen_range(pr['monthly_min'], pr['monthly_max']),
    ), encoding="utf-8")
    print(f"✅ 電話台本を作りました: {out}")
    print("   ★その場で契約を取らないこと★")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    if "--phone" in sys.argv:
        build_phone(slug)
    else:
        build_postcard(slug)
