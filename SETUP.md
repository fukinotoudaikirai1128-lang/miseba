# セットアップ手順

> ## ⚠️ この文書の一部は古くなっています（2026-08-21 更新）
>
> **GitHub Pages での公開はやめました。** 公開リポジトリのファイルページ
> （`github.com/.../blob/...`）は検索避けされておらず、店名を含むHTMLが
> 検索エンジンから読めてしまうためです。試作サイトに入れた `noindex` は
> GitHub 上のコピーには効きません。
>
> **いまの公開方法：** https://app.netlify.com/drop に `docs` フォルダを
> ドラッグ＆ドロップする。詳しくは `.claude/skills/publish-preview/SKILL.md` を見てください。
>
> **リポジトリは非公開にして構いません。** Pages を使わないので支障ありません。
> 以下に出てくる「Public にする」「GitHub Pages を有効にする」手順は読み飛ばしてください。
> `docs/p/` と `prospects/` は `.gitignore` 済みで、GitHub には上がりません。



所要時間およそ15分。費用は0円です。

**終わったかどうかは、最後に `python3 scripts/check_setup.py` を実行すれば分かります。**
足りないものを全部教えてくれるので、途中で不安になったらいつでも実行してください。

---

## ⚠️ 最初に知っておくこと

GitHub Pages の無料プランは**公開（Public）リポジトリでしか使えません**。
つまり、このリポジトリに入れたファイルは**誰でも見られます**。

そのため、この仕組みでは次のように分けています。

| フォルダ | GitHubに上がるか | 中身 |
|---|---|---|
| `docs/` | **上がる（公開される）** | 試作サイトのHTML |
| `prospects/` | **上がらない** | 店名・電話番号・営業記録 |

`prospects/` は `.gitignore` で除外済みです。**この設定は絶対に消さないでください。**
消すと、あなたが誰に営業しているかが全世界に公開されます。

> より隠したい場合：**Cloudflare Pages に GitHub連携**すると、
> プライベートリポジトリのまま公開できます（これも無料）。最後の「補足」を参照。

---

## STEP 1 — zipを展開する

ダウンロードした `miseba.zip` を、分かりやすい場所に展開します。

| OS | 置き場所の例 |
|---|---|
| Mac | `書類/miseba` |
| Windows | `ドキュメント\miseba` |

展開すると、中に `CLAUDE.md` や `config.json` があるはずです。
**`miseba` フォルダの中にもう1つ `miseba` フォルダができていないか**確認してください。
なっていたら、内側のフォルダを外に出してください。

正しい状態：

```
miseba/
├── CLAUDE.md          ← これが直下にある
├── config.json
├── README.md
├── SETUP.md
├── .claude/
├── docs/
├── scripts/
└── templates/
```

---

## STEP 2 — GitHubでリポジトリを作る

1. https://github.com/new を開く
2. 次のように入力する

| 項目 | 入力内容 |
|---|---|
| **Repository name** | `miseba`（好きな名前でOK。英数字とハイフンのみ） |
| **Description** | 空でOK |
| **Public / Private** | **Public を選ぶ** ← 無料でPagesを使うために必須 |
| **Add a README file** | **チェックを外す** ← 入れると後で衝突します |
| **Add .gitignore** | **None のまま** ← 入れると既存の設定と衝突します |
| **Choose a license** | **None のまま** |

3. 緑の **Create repository** を押す

作成後の画面に出る `https://github.com/あなたの名前/miseba.git` という
URLを**コピーしておいてください**。次で使います。

---

## STEP 3 — ファイルをGitHubに上げる

**空のリポジトリを先にパソコンへ持ってきて、そこに中身を入れる**という順番でやります。
この順番だと、リモートの設定を手で書く必要がありません。

### 3-1. GitHub Desktop を入れる

1. https://desktop.github.com/ から **Download now** → インストール
2. 起動して GitHubアカウントでサインイン
3. 「Configure Git」画面が出たら、**そのまま Finish**
   （ここのメールはコミットの署名用。サイトに載る連絡先とは別物なので変更不要）

### 3-2. 空のリポジトリをパソコンに持ってくる（クローン）

1. 「Let's get started!」画面の左側 **Your repositories** に
   `あなたの名前/miseba` が出ているのでクリック
2. 保存先を確認して **Clone**
   （既定では `ドキュメント\GitHub\miseba`）

これで空の `miseba` フォルダがパソコンにできます。
GitHub Desktop に「**No local changes**」と出れば正常です。

### 3-3. zipの中身を、その空フォルダに入れる

1. GitHub Desktop の **Show in Explorer**（Macは Show in Finder）を押す
   → 空の `miseba` フォルダが開く
2. 別の窓で、ダウンロードした `miseba.zip` を展開したフォルダを開く
3. **隠しファイルを表示する**（`.claude` と `.gitignore` を見えるようにするため）
   - Windows：エクスプローラー上部の **表示 → 表示 → 隠しファイル** にチェック
   - Mac：`Cmd + Shift + .`
4. 展開したフォルダの**中に入って**、`Ctrl+A`（Macは `Cmd+A`）で全選択 → コピー
5. 1で開いた空のフォルダに貼り付け

入るのはこの10個です。

| 名前 | 中身 |
|---|---|
| `CLAUDE.md` | Claude Codeが毎回読むルールブック |
| `config.json` | あなたの設定（名前・メール・GitHub情報） |
| `README.md` | プロジェクト全体の説明 |
| `SETUP.md` | この手順書 |
| `.claude`（隠し） | 5つのスキル定義 |
| `.gitignore`（隠し） | **公開してはいけないものの除外リスト** |
| `brand` | ミセバのブランド定義 |
| `docs` | **GitHub Pagesで公開される部分**（ミセバのサイト） |
| `scripts` | サイト生成・公開・点検のプログラム |
| `templates` | 試作サイトのひな形 |

### 3-4. コミットしてプッシュ

GitHub Desktop に戻ると、Changesタブにファイルが一覧で出ます。

1. **確認：一覧に `prospects/` が出ていないこと**
   （出ていたら STEP5 のトラブル対応へ）
2. 左下の **Summary** に `first commit` と入力
3. **Commit to main** を押す
4. ボタンが **Push origin** に変わるので、それを押す

---

### 参考：コマンドラインでやる場合

```bash
git clone https://github.com/あなたの名前/miseba.git
# ここで zip の中身を miseba/ にコピー
cd miseba
git add .
git status          # ← prospects/ が出ていないことを必ず確認
git commit -m "first commit"
git push
```

---

## STEP 4 — GitHub Pages を有効にする

1. GitHubのリポジトリページを開く
2. 上部のタブから **Settings**（歯車マーク）をクリック
3. 左サイドバーを下にスクロールして **Pages** をクリック
4. **Build and deployment** の欄で次のように設定

| 項目 | 選ぶもの |
|---|---|
| **Source** | `Deploy from a branch` |
| **Branch** | `main` |
| フォルダ（Branchの右の欄） | **`/docs`** ← `/(root)` ではない |

5. **Save** を押す

### 確認

1〜2分待ってから、Pagesの設定画面を再読み込みしてください。
上部に緑色で次のように出れば成功です。

```
✅ Your site is live at https://あなたの名前.github.io/miseba/
```

そのURLを開いて、**ミセバの紹介ページ**が表示されたらPages設定は完了です。

### 出てこないときのチェック

| 症状 | 原因と対処 |
|---|---|
| Branchの欄に `/docs` が選べない | `docs` フォルダがpushされていない。`docs/index.html` があるか確認 |
| 404が出る | 反映に最大10分かかることがある。少し待つ |
| Pagesの項目が見当たらない | リポジトリが Private になっている。Settings一番下で Public に変更 |

---

## STEP 5 — config.json を確認する

**この配布版は、すでに記入済みです。** 中身を確認するだけでOKです。

| 項目 | 設定済みの値 | 意味 |
|---|---|---|
| `contact_name` | `saku` | 営業メッセージで名乗る名前 |
| `contact_email` | `onikudaisuki1388@gmail.com` | 相手からの返信先 |
| `github_user` | `fukinotoudaikirai1128-lang` | GitHubのユーザー名 |
| `repo_name` | `miseba` | リポジトリ名 |
| `search.area` | `東京都杉並区` | **見込み客を探すエリア** |

### 唯一、変えた方がいい項目

`search.area` は初期値のままです。**自分の生活圏に変えてください。**
土地勘のあるエリアの方が、相手と話が合いますし、いざ会うことになっても動きやすいです。

```json
  "search": {
    "area": "東京都〇〇区",       ← ここを自分のエリアに
```

`keywords`（探す業種）も好みで変えられます。

```json
    "keywords": ["屋根修理", "水道業者", "工務店", "電気工事", "外壁塗装"],
```

### 書き換えるときの注意

- **`"` （ダブルクォート）を消さない**。値だけを書き換える
- 行末の **`,`（カンマ）を消さない**
- 日本語をそのまま入れてOK

保存したら、次で確認します。

---

## STEP 6 — 確認する

`miseba` フォルダでターミナルを開いて実行します。

```bash
python3 scripts/check_setup.py
```

こう出れば完了です。

```
✨ セットアップは完了しています。
   Claude Code でこのフォルダを開いて「今日の仕事始めて」と言ってみてください。
```

`❌` が出た項目は、右側に直し方が書いてあるのでその通りにしてください。

---

## トラブル対応

### ★最重要★ prospects/ をGitHubに上げてしまった

`check_setup.py` が次を出したら、**すぐに**対応してください。

```
❌ prospects/ がGitに含まれていない（個人情報保護）
```

対処：

```bash
git rm -r --cached prospects/
echo "prospects/" >> .gitignore
git add .gitignore
git commit -m "remove prospects from tracking"
git push
```

ただし、**一度pushしたものは履歴に残ります。**
既に実際の見込み客の情報を上げてしまった場合は、
リポジトリを一度削除して作り直すのが確実です（サンプルデータだけなら問題ありません）。

### `python3` が見つからない

- Mac：`python3 --version` で確認。無ければ https://www.python.org/downloads/
- Windows：`python scripts/check_setup.py` と、`3` を付けずに試す

### `git` が見つからない

https://git-scm.com/downloads からインストール。
または方法A（GitHub Desktop）を使えばgitコマンドは不要です。

---

## 補足：もっと隠したい場合（Cloudflare Pages）

GitHub Pages だとリポジトリを Public にする必要がありますが、
**Cloudflare Pages を GitHub連携で使う**と、Privateリポジトリのまま公開できます。
こちらも無料・カード登録不要です。

1. https://dash.cloudflare.com/ でアカウント作成（無料）
2. **Workers & Pages → Create → Pages → Connect to Git**
3. GitHubを連携して `miseba` リポジトリを選ぶ
4. ビルド設定：
   - Framework preset: `None`
   - Build command: 空
   - Build output directory: `docs`
5. Save and Deploy

公開URLが `https://miseba-xxx.pages.dev/` の形で発行されるので、
`config.json` の `publish.provider` を `cloudflare_pages` に変え、
発行されたURLを控えておいてください。

この場合、STEP2でリポジトリを **Private** にして構いません。
