import os
import json
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

def write_markdown_file(page):
    md_path = os.path.join(VAULT_DIR, f'{page["id"]}.md')
    frontmatter = to_yaml_frontmatter(page)
    body = "\n".join(page["lines"])
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