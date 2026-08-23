#!/usr/bin/env python3
"""ポストに投函するA4チラシを作る。

  python3 scripts/make_flyer.py            汎用（どのお店にも使える）
  python3 scripts/make_flyer.py <slug>     宛名入り（そのお店あて）

はがき（make_postcard.py）との違い：
- はがきは1枚85円かかるが、これは紙代だけ。自分で印刷して投函する
- そのお店専用の試作サイトのURLは載せない。**ミセバのサイトだけ**を案内する
  → 勝手に他店のサイトを作って公開しないので、LEGAL.md §2 の危険が発生しない
  → 興味を持った人だけが連絡してくる

出力: docs/ ではなく prospects/<slug>/flyer.html（または out/flyer.html）
      ブラウザで開いて Ctrl+P → A4 → 余白なし
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_postcard import qr_svg, esc, load_config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def yen(n):
    return f"{int(n):,}円"


def build(slug=None):
    cfg = load_config()
    brand = cfg.get("brand", {})
    pub = cfg.get("publish", {})
    pricing = cfg.get("outreach", {}).get("pricing", {})

    site_url = (pub.get("site_url") or "").rstrip("/")
    if not site_url:
        sys.exit(
            "エラー: config.json の publish.site_url が空です。\n"
            "  ミセバのサイトのURLが決まっていないと、チラシに載せるQRコードが作れません。\n"
            "  公開先を決めてから、そのURLを publish.site_url に入れてください。"
        )

    line_url = brand.get("line_url", "")
    contact_name = brand.get("contact_name", "")
    contact_email = brand.get("contact_email", "")

    setup = pricing.get("setup_min", 50000)
    monthly = pricing.get("monthly_min", 5000)
    monitor = 30000

    # 宛名（slug が渡されたときだけ）
    addressee = ""
    if slug:
        info_path = ROOT / "prospects" / slug / "info.json"
        if not info_path.exists():
            sys.exit(f"エラー: {info_path} がありません。")
        info = json.loads(info_path.read_text(encoding="utf-8"))
        addressee = (
            f'<p class="to">{esc(info.get("area", ""))}<br>'
            f'<strong>{esc(info.get("name", ""))}</strong> 御中</p>'
        )

    site_qr = qr_svg(site_url, size_mm=34)
    line_qr = qr_svg(line_url, size_mm=22) if line_url else ""
    line_block = (
        f'<div class="lineqr">{line_qr}<span>LINEで<br>相談する</span></div>' if line_qr else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>チラシ｜ミセバ</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@700&display=swap" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "Noto Sans JP", sans-serif; background: #EDEAE4; }}
  .guide {{
    max-width: 210mm; margin: 12px auto; padding: 14px 18px; background: #fff;
    border-left: 4px solid #B0803A; font-size: 13px; line-height: 1.8; color: #333;
  }}
  .sheet {{
    width: 210mm; height: 297mm; margin: 0 auto; background: #FBF9F5;
    padding: 16mm 15mm; position: relative; overflow: hidden;
    color: #101C26; display: flex; flex-direction: column;
  }}
  .sheet::before {{
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 8mm;
    background: linear-gradient(90deg, #101C26 0%, #1d3040 55%, #B0803A 100%);
  }}
  .brandline {{
    font-size: 8pt; letter-spacing: .38em; color: #B0803A; font-weight: 700;
    margin-top: 4mm; margin-bottom: 6mm;
  }}
  .to {{ font-size: 10.5pt; line-height: 1.7; margin-bottom: 7mm; }}
  .to strong {{ font-size: 13pt; }}
  h1 {{
    font-family: "Noto Serif JP", serif; font-size: 25pt; line-height: 1.5;
    letter-spacing: .03em; margin-bottom: 5mm;
  }}
  h1 .em {{ color: #B0803A; }}
  .lead {{ font-size: 10.5pt; line-height: 1.95; margin-bottom: 6mm; max-width: 120mm; }}
  .free {{
    display: inline-block; background: #101C26; color: #F6F2EA; font-weight: 700;
    font-size: 10pt; letter-spacing: .08em; padding: 3mm 6mm; border-radius: 2mm;
    margin-bottom: 6mm;
  }}

  .cols {{ display: flex; gap: 8mm; align-items: flex-start; }}
  .left {{ flex: 1; }}
  .right {{ width: 46mm; flex: none; text-align: center; }}

  .qrbox {{
    background: #fff; border: 1px solid #E4DED4; border-radius: 3mm;
    padding: 4mm 3mm; margin-bottom: 4mm;
  }}
  .qrbox .cap {{ font-size: 8.5pt; font-weight: 700; margin-bottom: 2.5mm; line-height: 1.5; }}
  .qrbox .url {{
    font-size: 7pt; color: #6B7680; margin-top: 2.5mm; word-break: break-all; line-height: 1.5;
  }}
  .lineqr {{
    background: #06C755; border-radius: 3mm; padding: 3mm; color: #fff;
    display: flex; align-items: center; gap: 3mm; text-align: left;
  }}
  .lineqr svg {{ background: #fff; padding: 1mm; border-radius: 1mm; }}
  .lineqr span {{ font-size: 8.5pt; font-weight: 700; line-height: 1.45; }}

  .steps {{ list-style: none; counter-reset: s; margin: 2mm 0 6mm; }}
  .steps li {{
    counter-increment: s; position: relative; padding-left: 9mm;
    margin-bottom: 3mm; font-size: 9.5pt; line-height: 1.7;
  }}
  .steps li::before {{
    content: counter(s); position: absolute; left: 0; top: .4mm;
    width: 6mm; height: 6mm; background: #B0803A; color: #fff; border-radius: 50%;
    font-size: 8pt; font-weight: 700; display: flex; align-items: center; justify-content: center;
  }}
  .steps b {{ display: block; }}

  .price {{
    background: #fff; border: 1px solid #E4DED4; border-radius: 3mm;
    padding: 5mm 6mm; margin-bottom: 5mm;
  }}
  .price .row {{ display: flex; justify-content: space-between; align-items: baseline;
    font-size: 10pt; padding: 1.6mm 0; }}
  .price .row .v {{ font-family: "Noto Serif JP", serif; font-weight: 700; font-size: 14pt; }}
  .price .monitor {{
    margin-top: 3mm; padding-top: 3mm; border-top: 1px dashed #E4DED4;
    font-size: 9pt; line-height: 1.7; color: #2B3B47;
  }}
  .price .monitor b {{ color: #B0803A; font-size: 11pt; }}
  .cmp {{ font-size: 8.5pt; color: #6B7680; line-height: 1.75; margin-top: 2mm; }}

  footer {{
    margin-top: auto; border-top: 1px solid #E4DED4; padding-top: 4mm;
    font-size: 8pt; line-height: 1.75; color: #4a5560;
  }}
  footer .name {{ font-family: "Noto Serif JP", serif; font-size: 11pt; letter-spacing: .18em;
    color: #101C26; }}
  footer .opt {{ margin-top: 2mm; color: #6B7680; }}

  @media print {{
    body {{ background: #fff; }}
    .guide {{ display: none; }}
    .sheet {{ margin: 0; }}
  }}
</style>
</head>
<body>

<div class="guide">
  <strong>印刷のしかた</strong><br>
  Ctrl+P →「用紙サイズ: A4」→「余白: なし」→「背景のグラフィック」にチェック。<br>
  この案内は印刷されません。投函するときは、事業所のポストに。
  「チラシお断り」の表示があるお宅には入れないでください。
</div>

<div class="sheet">
  <div class="brandline">MISEBA</div>
  {addressee}

  <h1>ホームページ、<br><span class="em">作ってみませんか。</span></h1>

  <p class="lead">
    Googleマップでお店を拝見して、ホームページをお持ちでないようでしたので、
    このお便りをお届けしました。突然のお便りで失礼いたします。
  </p>

  <div class="free">まず1ページ、無料でお作りします</div>

  <div class="cols">
    <div class="left">
      <ol class="steps">
        <li><b>ご連絡ください</b>お店の名前と場所を教えていただくだけで大丈夫です。</li>
        <li><b>試作をお見せします</b>1ページ作ってお届けします。ここまで費用はかかりません。</li>
        <li><b>見てから決めてください</b>いらなければ、そこで終わりで構いません。</li>
      </ol>

      <div class="price">
        <div class="row"><span>作るときの費用</span><span class="v">{yen(setup)}</span></div>
        <div class="row"><span>公開後の月額</span><span class="v">{yen(monthly)}</span></div>
        <div class="monitor">
          いまは実績を作っている段階のため、<b>はじめの3件は {yen(monitor)}</b> でお引き受けしています。
          （実績として紹介させていただくことが条件です）
        </div>
      </div>

      <p class="cmp">
        ホームページ制作は、制作会社に頼むと15〜65万円ほどが相場です。
        ご自分で作れる方はそのほうが安く済みます。作る時間がない方、
        何を書けばいいか分からない方に向いています。
      </p>
    </div>

    <div class="right">
      <div class="qrbox">
        <div class="cap">どんなものが作れるか<br>ここで見られます</div>
        {site_qr}
        <div class="url">{esc(site_url)}</div>
      </div>
      {line_block}
    </div>
  </div>

  <footer>
    <div class="name">ミセバ</div>
    （個人事業）　{esc(contact_name)}　／　{esc(contact_email)}<br>
    本サービスは事業者さま向けのサービスです。
    所在地・電話番号はご請求により遅滞なくお知らせします。
    <div class="opt">
      今後このようなお便りが不要でしたら、ご一報ください。二度とお送りいたしません。
    </div>
  </footer>
</div>

</body>
</html>
"""

    if slug:
        out = ROOT / "prospects" / slug / "flyer.html"
    else:
        out = ROOT / "out" / "flyer.html"
        out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out, site_url


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    path, url = build(target)
    print(f"✅ チラシを作りました: {path}")
    print("   ブラウザで開いて Ctrl+P → 用紙A4 → 余白なし → 背景のグラフィックにチェック")
    print(f"   QRの行き先: {url}")
    if target:
        print(f"   宛名入り（{target}）")
    else:
        print("   宛名なし（どのお店にも使える汎用版）")
