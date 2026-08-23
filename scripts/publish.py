#!/usr/bin/env python3
"""試作サイトを docs/p/<random-slug>/ にコピーして、GitHub Pages で公開する。

  python3 scripts/publish.py <slug>           コピーと検証だけ（pushしない）
  python3 scripts/publish.py <slug>

"""
import json
import re
import secrets
import shutil
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ROBOTS = """User-agent: *
Disallow: /p/
"""


def clear_dir(d):
    """フォルダの中身を消す。フォルダ自体が消せなくても失敗にしない。

    Windows + OneDrive では同期プロセスがフォルダを掴んでいて
    shutil.rmtree が PermissionError(WinError 5) で落ちることがある。
    中身さえ空にできれば上書きコピーには支障がない。
    """
    if not d.exists():
        return
    for item in sorted(d.rglob("*"), reverse=True):
        try:
            item.unlink() if item.is_file() else item.rmdir()
        except OSError:
            pass
    try:
        d.rmdir()
    except OSError:
        pass


def random_slug(n: int) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))



def main(slug: str):
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    pub = cfg["publish"]

    pdir = ROOT / "prospects" / slug
    site = pdir / "site"
    info_path = pdir / "info.json"

    if not site.exists():
        sys.exit(f"エラー: {site} がありません。先に build_site.py を実行してください。")

    info = json.loads(info_path.read_text(encoding="utf-8"))

    # 既に公開済みなら同じスラッグを使い回す（URLが変わると相手が困る）
    public_slug = info.get("public_slug") or random_slug(pub.get("slug_length", 20))

    dest = ROOT / pub.get("base_path", "docs/p") / public_slug
    if dest.exists():
        clear_dir(dest)
    shutil.copytree(site, dest, dirs_exist_ok=True)

    # --- 検証: noindex が全ページに入っているか ---
    problems = []
    for html in dest.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        if 'name="robots"' not in text or "noindex" not in text:
            problems.append(f"{html.name}: noindex が無い（検索に載ってしまう）")
        if "が作成した試作サイト" not in text or "ミセバ" not in text:
            problems.append(f"{html.name}: ミセバの試作である旨の注記が無い")
        phone_digits = "".join(c for c in info.get("phone", "") if c.isdigit() or c == "+")
        if phone_digits:
            if 'href="tel:' + phone_digits + '"' not in text:
                problems.append(f"{html.name}: その店の電話番号への tel: リンクが無い")
        elif 'href="tel:"' in text:
            problems.append(f"{html.name}: 中身が空の tel: リンクがある（電話番号未取得の店）")
        left = re.findall(r"\{\{[A-Z_]+\}\}", text)
        if left:
            problems.append(f"{html.name}: 未置換のプレースホルダー {set(left)}")

    # --- robots.txt ---
    robots = ROOT / "docs" / "robots.txt"
    if not robots.exists() or "Disallow: /p/" not in robots.read_text(encoding="utf-8"):
        robots.parent.mkdir(parents=True, exist_ok=True)
        robots.write_text(ROBOTS, encoding="utf-8")
        print("  docs/robots.txt を作成しました")

    if problems:
        clear_dir(dest)
        print("公開を中止しました。次の問題を直してください:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    site_url = (pub.get("site_url") or "").rstrip("/")
    url = f"{site_url}/p/{public_slug}/" if site_url else ""
    info["public_slug"] = public_slug
    if url:
        info["public_url"] = url
    info["status"] = "published"
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"コピー完了: {dest.relative_to(ROOT)}")
    if url:
        print(f"公開URL: {url}")
    print()
    print("=== 公開のしかた（Netlify） ===")
    print("  1. https://app.netlify.com/drop を開く")
    print(f"  2. {ROOT / 'docs'} フォルダごとドラッグ＆ドロップする")
    print("  3. 発行されたURLを config.json の publish.site_url に入れる")
    print()
    print("  ※ GitHub には push しません。docs/p/ は .gitignore 済みです。")
    print("     公開リポジトリのファイルページからは店名が読めてしまうため、")
    print("     試作サイトを GitHub に置くのはやめました（LEGAL.md 2）。")
    if not site_url:
        print()
        print("  ⚠️  config.json の publish.site_url が空です。")
        print("     Netlify で発行されたURLを入れるまで、はがき・チラシのQRは作れません。")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 scripts/publish.py <slug>")
    main(sys.argv[1])
