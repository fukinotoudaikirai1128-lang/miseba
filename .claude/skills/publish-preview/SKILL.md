---
name: publish-preview
description: 完成した試作サイトを GitHub Pages に公開して、共有用のURLを発行する。「公開して」「アップして」と言われたとき、または daily-run から呼ばれたときに使う。
---

# publish-preview — GitHub Pages に公開する

## 前提

- `prospects/<slug>/info.json` の `status` が `site_ready` であること
- リポジトリが GitHub に連携済みで、GitHub Pages が `docs/` を配信する設定になっていること
  （リポジトリの Settings → Pages → Source: `Deploy from a branch` → `main` / `/docs`）

## ★公開範囲についての注意★

GitHub Pages の無料プランは、**公開リポジトリでのみ**使えます。つまり：

- `docs/` に置いたHTMLは**誰でも見られる状態**になる
- URLはランダムなスラッグなので推測はされにくいが、**リポジトリのファイル一覧からは辿れる**
- したがって `prospects/`（店舗の連絡先・営業記録）は `.gitignore` で除外し、
  **公開用HTMLだけを `docs/` に置く**

より隠したい場合の選択肢（どちらも無料）：
1. **Cloudflare Pages に GitHub連携**する → プライベートリポジトリのまま公開できる
2. プレビュー用に**別アカウントの中立な名前のリポジトリ**を使う

---

## 手順

### 1. スラッグを発行する

推測されにくいランダムな公開スラッグを作る（店名は使わない）。

```bash
python3 scripts/publish.py <slug>
```

このスクリプトが行うこと：
- `prospects/<slug>/site/` を `docs/p/<random-slug>/` にコピー
- `docs/p/<random-slug>/` 内の全HTMLに `noindex` が入っているか検証
- `docs/robots.txt` に `Disallow: /p/` があるか確認（無ければ作る）
- `info.json` に `public_url` と `public_slug` を書き込む

### 2. 検証する

コピー後、必ず確認する。

- [ ] 全ページに `<meta name="robots" content="noindex, nofollow">` があるか
- [ ] `docs/robots.txt` に `Disallow: /p/` があるか
- [ ] `prospects/` の中身が `git status` に出てきていないか（出てきたら `.gitignore` を直す）

### 3. push する

```bash
git add docs/
git commit -m "add preview: <public-slug>"
git push
```

**`git add .` は使わない。** `docs/` だけを明示的に add すること。
`prospects/` を誤って push すると個人情報が公開される。

### 4. URLを確認する

push から反映まで1〜2分かかる。

```
https://<ユーザー名>.github.io/<リポジトリ名>/p/<random-slug>/
```

実際にブラウザで開いて、表示されることを確認してから次に進む。

### 5. 記録する

`info.json` の `status` を `published` に更新する。

---

## 取り下げるとき

相手から「消してほしい」と言われた場合は、**最優先で即対応する**。

```bash
git rm -r docs/p/<random-slug>/
git commit -m "remove preview on request"
git push
```

その店の `info.json` に `"status": "removed"`, `"do_not_contact": true` を書き、
二度とアプローチしないようにする。
