import os
import json
import re
from pathlib import Path
from datetime import datetime

VAULT_DIR = "vault"
INPUT_JSON = "build/input.json"

def ensure_vault_dir():
    Path(VAULT_DIR).mkdir(parents=True, exist_ok=True)

def load_input_json():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def to_yaml_frontmatter(page):
    # 必要なメタ情報をYAML形式で返す
    lines = [
        "---",
        f'alias: ["{page["title"]}"]',
        f'created: {page["created"]}',
        f'updated: {page["updated"]}',
        f'id: {page["id"]}',
        f'views: {page.get("views", 0)}',
        "---",
        ""
    ]
    return "\n".join(lines)

def convert_links(line):
    # [ほげ] → [[ほげ]]
    line = re.sub(r'\[([^\[\]]+)\]', r'[[\1]]', line)
    # #ほげ → [[ほげ]]（単語境界で#の後に英数字・日本語・_が続くもの）
    # 既に[[ほげ]]になっているものは変換しない
    line = re.sub(r'(?<!\w)#([A-Za-z0-9_\u3040-\u30FF\u4E00-\u9FFF]+)', r'[[\1]]', line)
    return line

def write_markdown_file(page):
    md_path = os.path.join(VAULT_DIR, f'{page["id"]}.md')
    frontmatter = to_yaml_frontmatter(page)
    # 各行にリンク変換を適用
    converted_lines = [convert_links(line) for line in page["lines"]]
    body = "\n".join(converted_lines)
    content = frontmatter + body + "\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    # ファイルのタイムスタンプを設定
    try:
        os.utime(md_path, (page["created"], page["updated"]))
    except Exception as e:
        print(f"Failed to set utime for {md_path}: {e}")

def main():
    ensure_vault_dir()
    data = load_input_json()
    for page in data["pages"]:
        write_markdown_file(page)
    print(f"変換完了: {len(data['pages'])}件のノートを{VAULT_DIR}/に出力しました。")

if __name__ == "__main__":
    main()