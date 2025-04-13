import os
import json
import re
import sys
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
        f'aliases: ["{page["title"]}"]',
        f'created: {page["created"]}',
        f'updated: {page["updated"]}',
        f'id: {page["id"]}',
        f'views: {page.get("views", 0)}',
        "---",
        ""
    ]
    return "\n".join(lines)

def convert_links(line):
    # Scrapbox装飾記法 [* 太字] [/ 斜体] [- 打ち消し] [/* 太字斜体] [-*/ 打ち消し斜体太字] などをMarkdownに変換
    def replace_decor(match):
        deco = match.group(1)
        text = match.group(2)
        md = text
        # 装飾の優先順: -（打ち消し）, *（太字）, /（斜体）
        if '-' in deco:
            md = f"~~{md}~~"
        if '*' in deco and '/' in deco:
            md = f"***{text}***"
        elif '*' in deco:
            md = f"**{text}**"
        elif '/' in deco:
            md = f"*{text}*"
        # 打ち消しと複合
        if '-' in deco and ('*' in deco or '/' in deco):
            md = f"~~{md}~~"
        return md

    # [* 太字] など
    line = re.sub(r'\[([*/\-]+)\s+([^\[\]]+?)\]', replace_decor, line)

    # scrapbox由来の [[...]] → **...**（ボールド化）
    line = re.sub(r'\[\[([^\[\]]+)\]\]', r'**\1**', line)

    # [タイトル] → [[id|タイトル]] or [[タイトル]]
    def replace_link(match):
        title = match.group(1)
        # タイトルがファイル名として安全か判定
        if title in title_to_id and not is_safe_filename(title):
            return f"[[{title_to_id[title]}|{title}]]"
        else:
            return f"[[{title}]]"
    line = re.sub(r'\[([^\[\]]+)\]', replace_link, line)

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
            f'aliases: ["{title}"]',
            f"created: {page['created']}",
            f"updated: {page['updated']}",
            f"id: {page['id']}",
            f"views: {page.get('views', 0)}",
            "---",
            ""
        ]
    md_path = os.path.join(VAULT_DIR, filename)
    lines_to_use = page["lines"]
    if lines_to_use and lines_to_use[0] == title:
        lines_to_use = lines_to_use[1:]
    body = "\n".join(convert_links(line) for line in lines_to_use)
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
    global title_to_id
    title_to_id = {page["title"]: page["id"] for page in data["pages"]}
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