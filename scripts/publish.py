#!/usr/bin/env python3
"""試作サイトを docs/p/<random-slug>/ にコピーして、GitHub Pages で公開できる状態にする。

  python3 scripts/publish.py <slug>

このスクリプトは git push まではしない（何を公開するか目視してから push するため）。
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
        shutil.rmtree(dest)
    shutil.copytree(site, dest)

    # --- 検証: noindex が全ページに入っているか ---
    problems = []
    for html in dest.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        if 'name="robots"' not in text or "noindex" not in text:
            problems.append(f"{html.name}: noindex が無い")
        if "ミセバ" not in text:
            problems.append(f"{html.name}: ミセバの注記が無い")
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
        shutil.rmtree(dest)
        print("公開を中止しました。次の問題を直してください:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    url = f"https://{pub['github_user']}.github.io/{pub['repo_name']}/p/{public_slug}/"
    info["public_slug"] = public_slug
    info["public_url"] = url
    info["status"] = "published"
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"コピー完了: {dest.relative_to(ROOT)}")
    print(f"公開予定URL: {url}")
    print()
    print("次のコマンドで公開してください（prospects/ は push されません）:")
    print(f"  git add docs/")
    print(f'  git commit -m "add preview: {public_slug}"')
    print(f"  git push")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 scripts/publish.py <slug>")
    main(sys.argv[1])
