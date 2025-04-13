import os
import json
import re
import unicodedata
from pathlib import Path
from datetime import datetime

VAULT_DIR = "vault"
INPUT_JSON = "build/input.json"
MAX_FILENAME_LEN = 100  # ファイル名の最大長（拡張子除く）

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
    # #ほげ → [[ほげ]]
    line = re.sub(r'(?<!\w)#([A-Za-z0-9_\u3040-\u30FF\u4E00-\u9FFF]+)', r'[[\1]]', line)
    return line

def is_safe_filename(title):
    forbidden = r'\\/:*?"<>|#\[\]'
    if any(c in forbidden for c in title):
        return False
    if title.strip(' .') != title or not title:
        return False
    return True

def write_markdown_file(page):
    title = page["title"]
    page_id = page["id"]
    if is_safe_filename(title):
        filename = f"{title}.md"
        # frontmatter（aliasなし）
        lines = [
            "---",
            f"created: {page['created']}",
            f"updated: {page['updated']}",
            f"id: {page['id']}",
            f"views: {page.get('views', 0)}",
            "---",
            ""
        ]
    else:
        filename = f"{page_id}.md"
        # frontmatter（aliasあり）
        lines = [
            "---",
            f'alias: ["{title}"]',
            f"created: {page['created']}",
            f"updated: {page['updated']}",
            f"id: {page['id']}",
            f"views: {page.get('views', 0)}",
            "---",
            ""
        ]
    md_path = os.path.join(VAULT_DIR, filename)
    body = "\n".join(convert_links(line) for line in page["lines"])
    content = "\n".join(lines) + body + "\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    # ファイルのタイムスタンプを設定
    try:
        os.utime(md_path, (page["created"], page["updated"]))
    except Exception as e:
        print(f"Failed to set utime for {md_path}: {e}")
    return filename

def main():
    ensure_vault_dir()
    data = load_input_json()
    title_count = 0
    id_count = 0
    for page in data["pages"]:
        filename = write_markdown_file(page)
        if filename.endswith(f"{page['id']}.md"):
            id_count += 1
        else:
            title_count += 1
    print(f"変換完了: {len(data['pages'])}件のノートを{VAULT_DIR}/に出力しました。")
    print(f"タイトル.mdで保存: {title_count}件")
    print(f"id.mdで保存: {id_count}件")

if __name__ == "__main__":
    main()