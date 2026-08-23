# ミセバ

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



Googleマップで見つけた「ホームページを持っていない小規模事業者」に、
**先に試作サイトを作って見せてから提案する**個人事業のワークスペース。

Claude Code でこのフォルダを開いて使います。

> 📖 **毎日の具体的な手順は [DAILY.md](./DAILY.md) を見てください。**
> ⚖️ **営業してよい相手・手段の判断は [brand/LEGAL.md](./brand/LEGAL.md) にまとまっています。**

---

## 使い方

Claude Code でこのフォルダを開いて、こう言うだけです。

```
今日の仕事始めて
```

`daily-run` スキルが動いて、次を順に実行します。

```
0. あなたがGoogleマップでHPの無い店を探す（★手作業・5分★）
        ↓
1. find-prospects   貼られた情報を選別・裏取り・登録
        ↓
2. new-preview      1店ずつ試作サイトを作る（STEP1〜5）
        ↓
3. publish-preview  GitHub Pages に公開してURLを発行（pushまで自動）
        ↓
4. send-outreach    はがきHTMLを作る → あなたが印刷して投函（★手作業★）
```

**Claudeにできないのは「Googleマップを見る」と「はがきを投函する」の2つだけ**です。

**1店ずつ完結させます。** 複数店を同時に処理すると店名や住所が混ざる事故が起きるためです。

個別に呼ぶこともできます。

| やりたいこと | 言い方 |
|---|---|
| 見込み客だけ探す | 「見込み客探して」 |
| 特定の店のサイトを作る | 「〇〇のサイト作って」 |
| 公開だけする | 「公開して」 |
| 営業メッセージだけ | 「営業して」 |

---

## この仕組みの設計方針

動画で紹介されていたClaude Codeの使い方（段階実行 / CLAUDE.md / SKILL.md /
フォルダ分離）を、営業用途に合わせて組み込んでいます。

| 動画の教え | ミセバでの実装 |
|---|---|
| 段階的に指示を出す | `new-preview` を STEP1〜5 に分割。飛ばさないルールを明記 |
| フォルダを分ける | `prospects/<slug>/` で1店1フォルダ。他店のフォルダを読まないルール |
| セッションを新しくする | 1店終わるごとに保存し、重くなったら区切るよう `daily-run` に明記 |
| モデルはOpus | Claude Code側で設定してください |
| CLAUDE.md（メモリ） | デザインルール・絶対制約・コーディング規約を集約 |
| SKILL.md（スキル） | 5つのスキルに分割（探す/作る/公開/送る/通し実行） |
| Unsplashの画像 | 業種ごとに画像URLを `scripts/build_site.py` に登録済み |
| 最終SEOチェック | STEP5 のチェックリスト＋`publish.py` が機械的に検証 |

### 動画と変えた点

**試作サイトは1ページだけにしました。** 動画は4ページ構成（TOP+3固定ページ）でしたが、
これは自分のデモサイトを作る前提の構成です。ミセバの用途は**初対面の相手に送る営業ツール**なので、

- 相手は4ページ読む関係性ではない。1画面で伝わる方が返信率が高い
- ページが増えるほど、事実の捏造が混入するリスクが増える
- 作る時間が増えるのに成約率は上がらない

複数ページに拡張するのは**契約が決まってから**です（構成は `CLAUDE.md` §4 に用意済み）。

---

## フォルダ構成

```
CLAUDE.md              ★共通ルール（Claude Codeが毎回読む）
config.json            設定（エリア・キーワード・上限・価格）
brand/BRAND.md         屋号「ミセバ」の定義・名乗り方・トーン

.claude/skills/
  find-prospects/      見込み客を探す
  new-preview/         試作サイトを5段階で作る
  publish-preview/     GitHub Pages に公開
  send-outreach/       営業メッセージを送る
  daily-run/           上記を通しで実行

templates/
  base/index.html      サイトの雛形（直接編集しない）
  outreach.md          営業文面のテンプレート

scripts/
  build_site.py        info.json → サイト生成（STEP1〜3を機械化）
  publish.py           docs/ にコピー＋noindex等を機械的に検証
  preview.py           ローカルサーバーで目視確認

prospects/<slug>/      ★.gitignore済み（個人情報のため push しない）
  info.json            店舗情報
  site/index.html      生成したサイト
  outreach.md          送信記録

docs/p/<random>/       ★公開用。GitHub Pages がここを配信
```

---

## セットアップ

**詳しい手順は [SETUP.md](./SETUP.md) にあります。** ここは要約です。

`config.json` は**記入済み**で配布しています（`saku` / `fukinotoudaikirai1128-lang` / `miseba`）。
変えるとすれば `search.area`（探すエリア）だけです。

1. GitHubで `miseba` リポジトリを作る（**Public**）
2. GitHub Desktop でクローン → 空フォルダにこの一式をコピー → Commit → Push
3. リポジトリの **Settings → Pages → `Deploy from a branch` → `main` / `/docs`**
4. 確認

```bash
python3 scripts/check_setup.py                 # 設定が正しいか一括点検
python3 scripts/build_site.py sample-roofing   # サンプルでサイト生成
python3 scripts/preview.py sample-roofing      # ブラウザで確認
```

公開URL：`https://fukinotoudaikirai1128-lang.github.io/miseba/`

---

## 費用

**ほぼ0円。かかるのは切手代だけです。**

| 項目 | 費用 |
|---|---|
| 見込み客探し | 0円（Places APIは使わない。あなたがGoogleマップを見る） |
| サイト生成 | 0円（Claudeの既存契約の範囲内） |
| ホスティング | 0円（GitHub Pages） |
| 画像 | 0円（Unsplash・商用利用可） |
| **はがき** | **85円／通**（＋官製はがき代・印刷代） |

1日3件なら **255円**。電話に切り替えれば0円ですが、断られやすくなります。

### 使えない連絡手段

| 手段 | 理由 |
|---|---|
| メール | 特定電子メール法。相手にサイトが無い＝オプトイン規制の例外が使えない |
| Googleマップのメッセージ | **2024年7月31日にGoogleが機能を終了**。存在しない |
| SNSのDM | 各サービスの規約でスパム扱い |

詳細は [brand/LEGAL.md](./brand/LEGAL.md)。

---

## 安全装置

勝手に緩めないでください。事故を防ぐためのものです。

| 装置 | 内容 |
|---|---|
| 事実の捏造禁止 | 創業年・実績・資格・料金は `info.json` に無ければ書かない |
| **除外業種の強制** | 株式会社／FC／士業／医療／接骨院・薬局は対象外（`LEGAL.md` §2） |
| 公開前の機械検証 | `publish.py` が noindex / 注記 / プレースホルダー残りを検査し、1つでも欠けたら公開を中止 |
| **push時の漏洩チェック** | `publish.py --push` は `docs/` だけを add。`prospects/` が混ざったら中止 |
| `prospects/` を push しない | `.gitignore` 済み。個人情報保護 |
| 1日の送信上限 | 10件（`config.json`） |
| 重複送信の禁止 | `sent_at` があれば送らない |
| 断られた相手 | `do_not_contact: true` で二度と送らない |
| **その場で契約しない** | 電話・訪問とも。必ず書面で（`LEGAL.md` §3） |
| 苦情が来たら | その場で全送信を停止して報告 |

---

## まだやっていないこと（TODO）

- [x] ミセバ自身のホームページ（`docs/index.html`）
- [x] 連絡手段の確定（はがき）
- [x] 価格の確定（初期5万円／月5,000円）
- [ ] **開業届**を税務署へ（無料。屋号「ミセバ」を登録できる）
- [ ] **商標の簡易確認**（[J-PlatPat](https://www.j-platpat.inpit.go.jp/) で「ミセバ」を検索。無料）
- [ ] `search.area` を自分の生活圏に変更
- [ ] 見積書・簡易契約書のひな形
