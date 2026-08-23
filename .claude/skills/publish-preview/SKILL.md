---
name: publish-preview
description: 依頼を受けたお店の試作サイトを GitHub Pages に公開して、共有用のURLを発行する。「公開して」「アップして」と言われたときに使う。
---

# publish-preview — GitHub Pages に公開する

## ★大前提★ 同意のない店のページを公開しない

**2026-08-21 に運用が変わりました。** 以前は、見つけた店の試作サイトを勝手に作って
公開していました。**もうやりません。**

いまの流れはこうです。

```
チラシを投函（QRはミセバのサイトだけを指す）
      ↓
興味を持った人が LINE で連絡してくる
      ↓
やりとりして「作ってほしい」と言われる  ← ★ここで初めて同意が得られる★
      ↓
new-preview で試作を作る
      ↓
publish-preview で公開する  ← このスキル
```

**公開してよいのは、相手から「作ってほしい」と言われたお店だけです。**

同意があるので、限定公開にする必要はありません。リポジトリは公開で構いませんし、
GitHub Pages をそのまま使えます。LEGAL.md §2 が心配していた
「勝手に作って公開する」ことに伴う危険（不正競争防止法・混同惹起）は、
同意を得た時点で発生しません。

逆に言えば、**同意がないうちに `docs/` に置いてはいけません。**
そこだけが守るべき一線です。

---

## 前提

- 相手から依頼の意思表示があること（★最重要★）
- `prospects/<slug>/info.json` の `status` が `site_ready` であること
- `config.json` の `publish.site_url` に GitHub Pages のURLが入っていること
- リポジトリの Settings → Pages で `main` / `/docs` が公開元になっていること

---

## 手順

### 1. コピーと検証

```bash
python3 scripts/publish.py <slug>
```

このスクリプトが行うこと：

- `prospects/<slug>/site/` を `docs/p/<ランダム20文字>/` にコピー
- 全HTMLに `noindex` が入っているか検証
- ミセバの試作である旨の注記があるか検証
- 電話番号がある店なら `tel:` リンクが正しいか、無い店なら空の `tel:` が無いか検証
- 未置換のプレースホルダーが無いか検証
- `docs/robots.txt` に `Disallow: /p/` があるか確認（無ければ作る）
- `info.json` に `public_slug` と `public_url` を書き込む

1つでも問題があれば、コピーを消して**公開を中止**します。

### 2. push する

```bash
git add docs/
git commit -m "add preview: <public-slug>"
git push
```

**`git add .` は使わない。** `docs/` だけを明示的に add すること。
`prospects/`（店舗の連絡先・営業記録）は `.gitignore` 済みですが、
`git status` に出てきたらその時点で止めて `.gitignore` を直す。

### 3. URLを確認する

push から反映まで1〜2分かかります。

```
<publish.site_url>/p/<ランダム20文字>/
```

実際にブラウザで開いて、表示されることを確認してから相手に渡す。

### 4. 記録する

`info.json` の `status` を `published` に更新する。

---

## 取り下げるとき

相手から「消してほしい」と言われた場合は、**最優先で即対応する**。

```bash
git rm -r docs/p/<ランダム20文字>/
git commit -m "remove preview on request"
git push
```

その店の `info.json` に `"status": "removed"`, `"do_not_contact": true` を書き、
二度とアプローチしないようにする。

**その日のうちに消すこと**（LEGAL.md §2）。

---

## 補足：GitHub の公開範囲について

リポジトリを公開にすると、`docs/` の中身は GitHub のファイルページからも読めます。
GitHub の `robots.txt` はフォルダ一覧（`/*/tree/`）は検索避けしていますが、
**ファイル本体（`/blob/`）は検索避けしていません**。

同意を得た店のサイトなら、もともと公開するものなので問題ありません。
**同意のない店のページを置いてはいけない理由が、ここにもあります。**
