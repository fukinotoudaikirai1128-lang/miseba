---
name: publish-preview
description: 完成した試作サイトを Netlify に公開して、共有用のURLを発行する。「公開して」「アップして」と言われたとき、または daily-run から呼ばれたときに使う。
---

# publish-preview — Netlify に公開する

## 前提

- `prospects/<slug>/info.json` の `status` が `site_ready` であること
- `config.json` の `publish.site_url` に Netlify の公開URLが入っていること
  （まだなら https://app.netlify.com/drop に `docs` フォルダを上げて発行する）

## ★なぜ GitHub Pages を使わないのか★

**使ってはいけません。** 以前は GitHub Pages で公開していましたが、やめました。

GitHub Pages の無料プランは公開リポジトリでしか使えません。そして公開リポジトリは、
**ファイル本体のページ（`github.com/<user>/<repo>/blob/...`）が検索避けされていません**。
GitHub の `robots.txt` は `/*/tree/`（フォルダ一覧）は拒否していますが、
`/blob/` については一切記述がありません（実測で確認済み）。

つまり：

- 試作サイト側に入れた `noindex` は、**GitHub 上のコピーには効かない**
- 店名を含むHTMLが、検索エンジンから読める状態になる
- LEGAL.md §2 の「URLはランダム文字列にする（推測できない）」が**成立しない**

非公開リポジトリから Pages を出すには GitHub Pro（有料）が必要で、
しかもそれでも公開されるサイト自体は誰でも見られます。ミセバは無課金運用が前提なので、
この道は使えません。

**Netlify なら、ソースの一覧が公開されないので、本当の「限定公開」になります。**

---

## 手順

### 1. コピーと検証

```bash
python3 scripts/publish.py <slug>
```

このスクリプトが行うこと：

- `prospects/<slug>/site/` を `docs/p/<random-slug>/` にコピー
- 全HTMLに `noindex` が入っているか検証
- ミセバの試作である旨の注記があるか検証
- 電話番号がある店なら `tel:` リンクが正しいか、無い店なら空の `tel:` が無いか検証
- 未置換のプレースホルダーが無いか検証
- `docs/robots.txt` に `Disallow: /p/` があるか確認（無ければ作る）
- `info.json` に `public_slug` を書き込む

1つでも問題があれば、コピーを消して**公開を中止**します。

### 2. Netlify にアップロードする

**これはユーザーの作業です。** Claude はブラウザでのアップロードを代行しません。

1. https://app.netlify.com/drop を開く
2. `docs` フォルダごとドラッグ＆ドロップする
3. 発行されたURLを確認する

2回目以降は、Netlify のサイト画面（Deploys タブ）に同じように `docs` を投げれば更新されます。

### 3. URLを確認する

```
<publish.site_url>/p/<random-slug>/
```

実際にブラウザで開いて、表示されることを確認してから次に進む。

### 4. 記録する

`info.json` の `status` を `published` に、`public_url` に上のURLを書く。

---

## ★GitHub に push してはいけないもの★

- `prospects/`  — 店舗の連絡先・営業記録（個人情報）
- `docs/p/`     — 試作サイト本体（**店名が入る**）

どちらも `.gitignore` 済みです。`git add .` は使わないこと。
`git status` に上の2つが出てきたら、その時点で止めて `.gitignore` を直す。

GitHub は**バックアップと履歴のため**だけに使います。公開経路ではありません。
リポジトリは非公開にして構いません（Pages を使わないので支障ありません）。

---

## 取り下げるとき

相手から「消してほしい」と言われた場合は、**最優先で即対応する**。

1. `docs/p/<random-slug>/` をローカルから削除する
2. `docs` フォルダを Netlify に上げ直す（消したものが反映される）
3. URLを開いて 404 になることを確認する

その店の `info.json` に `"status": "removed"`, `"do_not_contact": true` を書き、
二度とアプローチしないようにする。

**その日のうちに消すこと**（LEGAL.md §2）。
