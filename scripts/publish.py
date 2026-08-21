#!/usr/bin/env python3
"""試作サイトを docs/p/<random-slug>/ にコピーして、GitHub Pages で公開する。

  python3 scripts/publish.py <slug>           コピーと検証だけ（pushしない）
  python3 scripts/publish.py <slug> --push    検証を通ったら git push まで行う

--push は `git add docs/` しかしないので、prospects/（個人情報）は絶対に上がりません。
"""
import json
import re
import secrets
import shutil
import string
import subprocess
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


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=check)


def push(public_slug: str) -> bool:
    """docs/ だけを add して push する。prospects/ が紛れ込んだら中止する。"""
    try:
        git("rev-parse", "--git-dir")
    except Exception:
        print("⚠️  ここはGitリポジトリではないので push できません。")
        return False

    git("add", "docs/")

    staged = git("diff", "--cached", "--name-only").stdout.split()
    leaked = [f for f in staged if f.startswith("prospects/")]
    if leaked:
        git("reset")
        print("❌ ★至急★ prospects/ がステージに入っていたので中止しました:")
        for f in leaked:
            print(f"     {f}")
        print("   .gitignore に prospects/ があるか確認してください。")
        return False

    if not staged:
        print("  （docs/ に変更なし。pushはスキップ）")
        return True

    print(f"  公開するファイル: {len(staged)}件（すべて docs/ 配下）")
    git("commit", "-m", f"add preview: {public_slug}")
    r = git("push", check=False)
    if r.returncode != 0:
        print("⚠️  push に失敗しました:")
        print((r.stderr or r.stdout).strip()[:500])
        print("   GitHub Desktop から手動で Push してください。")
        return False
    print("✅ push しました。1〜2分でページが見られるようになります。")
    return True


def main(slug: str, do_push: bool = False):
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

    url = f"https://{pub['github_user']}.github.io/{pub['repo_name']}/p/{public_slug}/"
    info["public_slug"] = public_slug
    info["public_url"] = url
    info["status"] = "published"
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"コピー完了: {dest.relative_to(ROOT)}")
    print(f"公開予定URL: {url}")
    print()

    if do_push:
        push(public_slug)
    else:
        print("次のコマンドで公開してください（prospects/ は push されません）:")
        print("  git add docs/")
        print(f'  git commit -m "add preview: {public_slug}"')
        print("  git push")
        print()
        print("  ※ --push を付ければ、この3行を自動で実行します")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 scripts/publish.py <slug> [--push]")
    main(sys.argv[1], do_push="--push" in sys.argv)
