#!/usr/bin/env python3
"""セットアップが正しく終わっているかを確認する。

  python3 scripts/check_setup.py

「設定できてるか分からない」ときに実行すると、何が足りないかを教えてくれる。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OK = "  ✅"
NG = "  ❌"
WARN = "  ⚠️ "

problems = []
warnings = []


def check(label: str, ok: bool, fix: str = "", warn_only: bool = False):
    if ok:
        print(f"{OK} {label}")
    elif warn_only:
        print(f"{WARN}{label}")
        if fix:
            warnings.append(f"{label} → {fix}")
    else:
        print(f"{NG} {label}")
        if fix:
            problems.append(f"{label} → {fix}")
    return ok


def git(*args) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=15)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "git が見つかりません"
    except Exception as e:
        return 1, str(e)


print("\n=== ミセバ セットアップ確認 ===\n")

# ---------------------------------------------------------------- config.json
print("【1】config.json")
cfg = None
if check("config.json が存在する", (ROOT / "config.json").exists(),
         "zipを展開したフォルダで実行してください"):
    try:
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        check("config.json が正しいJSON形式", True)
    except json.JSONDecodeError as e:
        check("config.json が正しいJSON形式", False,
              f"{e} — カンマや引用符の書き忘れを確認してください")

if cfg:
    pub = cfg.get("publish", {})
    brand = cfg.get("brand", {})

    def filled(v) -> bool:
        s = str(v or "")
        return bool(s) and "（" not in s and "(" not in s

    check("publish.github_user が埋まっている", filled(pub.get("github_user")),
          "GitHubのユーザー名を入れてください")
    check("publish.repo_name が埋まっている", filled(pub.get("repo_name")),
          "リポジトリ名を入れてください")
    check("brand.contact_name が埋まっている", filled(brand.get("contact_name")),
          "営業メッセージで名乗る名前を入れてください")
    check("brand.contact_email が埋まっている", filled(brand.get("contact_email")),
          "連絡先メールアドレスを入れてください（後回しでも可）", warn_only=True)
    check("search.area が埋まっている", filled(cfg.get("search", {}).get("area")),
          "探すエリアを入れてください（例: 東京都杉並区）")

    if filled(pub.get("github_user")) and filled(pub.get("repo_name")):
        url = f"https://{pub['github_user']}.github.io/{pub['repo_name']}/"
        print(f"     → 公開URLはこうなります: {url}")

# ---------------------------------------------------------------- ファイル構成
print("\n【2】ファイル構成")
check("CLAUDE.md がある", (ROOT / "CLAUDE.md").exists())
check(".claude/skills/ にスキルが5つある",
      len(list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))) == 5,
      "zipの展開が不完全かもしれません")
check("docs/ フォルダがある", (ROOT / "docs").exists(),
      "GitHub Pages の公開元になるので必須です")
check("docs/index.html がある", (ROOT / "docs" / "index.html").exists(),
      "Pagesの動作確認に使います")
check("docs/robots.txt がある", (ROOT / "docs" / "robots.txt").exists(),
      "python3 scripts/publish.py を一度実行すると作られます", warn_only=True)
check(".gitignore がある", (ROOT / ".gitignore").exists(),
      "見込み客の情報が公開されるおそれがあります")

if (ROOT / ".gitignore").exists():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    check(".gitignore が prospects/ を除外している", "prospects/" in gi,
          "★重要★ .gitignore に prospects/ の行を追加してください")

# ---------------------------------------------------------------- git
print("\n【3】GitHub との連携")
code, _ = git("rev-parse", "--is-inside-work-tree")
is_repo = code == 0
if check("gitリポジトリになっている", is_repo,
         "このフォルダで `git init` を実行してください"):

    code, out = git("remote", "-v")
    has_remote = code == 0 and "github.com" in out
    check("GitHubのリモートが設定されている", has_remote,
          "`git remote add origin https://github.com/ユーザー名/リポジトリ名.git`")
    if has_remote:
        first = out.split("\n")[0]
        print(f"     → {first}")

    # ★最重要★ prospects/ がGitの管理下に入っていないか
    code, out = git("ls-files", "prospects")
    tracked = bool(out.strip())
    check("prospects/ がGitに含まれていない（個人情報保護）", not tracked,
          "★至急★ `git rm -r --cached prospects/` を実行してください")
    if tracked:
        print("     → 含まれているファイル:")
        for line in out.strip().split("\n")[:5]:
            print(f"        {line}")

    code, out = git("status", "--porcelain")
    if out.strip():
        n = len(out.strip().split("\n"))
        check(f"未コミットの変更が {n} 件あります", True, warn_only=True)

# ---------------------------------------------------------------- 結果
print("\n" + "=" * 42)
if problems:
    print(f"\n直すべき項目が {len(problems)} 件あります:\n")
    for i, p in enumerate(problems, 1):
        print(f"  {i}. {p}")
    print()
    sys.exit(1)

if warnings:
    print(f"\n参考（急ぎではありません）:\n")
    for w in warnings:
        print(f"  ・{w}")

print("\n✨ セットアップは完了しています。")
print("   Claude Code でこのフォルダを開いて「今日の仕事始めて」と言ってみてください。\n")
