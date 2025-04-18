# cosense2obsidian

## 概要

Scrapboxプロジェクトの全ページデータをダウンロードし、Obsidian用ノートに変換するツールです。

## 必要なもの

- Scrapboxの全ページデータを取得するための環境変数
  - `SCRAPBOX_PROJECT`  
    - 対象Scrapboxプロジェクト名（例: `https://scrapbox.io/help-jp/` の「help-jp」の部分を指定）
  - `SCRAPBOX_SESSION_ID`  
    - Scrapboxの全ページデータをダウンロードするために必要
    - **取得方法:**
      1. ChromeでScrapboxにログイン
      2. F12でデベロッパーツールを開く
      3. [Application]タブ → [Cookies] → `connect.sid` の値をコピー
      4. これを `SCRAPBOX_SESSION_ID` に設定

## セットアップ・使い方

### 方法1: 環境変数を設定して自動ダウンロード

1. **環境変数を設定**

```bash
export SCRAPBOX_PROJECT=your_project
export SCRAPBOX_SESSION_ID=xxxx
```

2. **makeコマンドを実行**

```bash
make
```

- 変換後のノートは `vault/` ディレクトリに出力されます。

### 方法2: ページデータを手動でダウンロードして配置

1. ブラウザで `https://scrapbox.io/projects/プロジェクト名/settings/page-data` にアクセスし、ページデータ（JSONファイル）をダウンロード
2. ダウンロードしたファイルを `build/input.json` として配置
3. `make` または `python3 cosense2obsidian.py` を実行

- どちらの方法でも `vault/` にノートが出力されます。

## トラブルシューティング

- **input.jsonがダウンロードできない場合**
  - エラー例:  
    `Error: SCRAPBOX_PROJECTとSCRAPBOX_SESSION_IDの環境変数を設定してください。`
  - 主な原因: `SCRAPBOX_SESSION_ID` が正しく設定されていない、または期限切れ・誤った値になっている可能性が高い
  - 対策:
    - Chromeのデベロッパーツールで `connect.sid` を再取得し、正しい値を環境変数に設定し直す
    - Scrapboxに再ログインしてから取得し直すと確実

## ディレクトリ構成

```
cosense2obsidian.py                # メインスクリプト
cosense2obsidian_analyze_filename.py  # タイトル安全性チェック用スクリプト
Makefile                           # makeコマンドで一括実行
build/                             # 入力データ配置用
vault/                             # 変換後のObsidianノート
```

## ファイル名に使えないタイトルの対応について

- タイトルにファイル名として使用できない文字（例: \ : * ? " < > | # [ ] など）、または先頭・末尾のスペースやドット、空文字が含まれている場合、そのページはid.mdというファイル名で出力され、元のタイトルはfrontmatterのaliasesとして記録されます。
- ただしタイトルに「/」が含まれている場合は、これをディレクトリ区切りとして扱います。
- Obsidian上ではaliasesにより元タイトルでの検索・リンクが可能です。
- TCP/IPとかがフォルダ分けされてしまうのは仕様です。

### 今後の課題
- 禁止文字を含むタイトルのより柔軟な変換や、ユーザーによるカスタマイズ対応などを検討中です。
- ご意見・ご要望があればIssue等でお知らせください。

## 備考

- Python標準ライブラリのみで動作します。追加のパッケージインストールは不要です。
- `build/` 配下のファイルは何度でも再生成できるため、不要になった場合は削除して問題ありません。