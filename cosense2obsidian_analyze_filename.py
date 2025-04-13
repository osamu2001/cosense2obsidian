import json
import re

def is_safe_filename(title):
    forbidden = r'\\/:*?"<>|#\[\]'
    if any(c in forbidden for c in title):
        return False
    if title.strip(' .') != title or not title:
        return False
    return True

def analyze():
    with open("build/input.json", encoding="utf-8") as f:
        data = json.load(f)
    forbidden = r'\\:*?"<>|#\[\]'
    forbidden_set = set(forbidden)
    cause_counter = {}
    example_titles = []
    for page in data["pages"]:
        title = page["title"]
        causes = []
        # 禁止文字
        for c in title:
            if c in forbidden_set:
                causes.append(c)
        # 先頭・末尾の空白やドット
        if title and (title[0] in " ."):
            causes.append("先頭" + repr(title[0]))
        if title and (title[-1] in " ."):
            causes.append("末尾" + repr(title[-1]))
        # 空文字
        if not title:
            causes.append("空文字")
        if not is_safe_filename(title):
            for c in causes or ["その他"]:
                cause_counter[c] = cause_counter.get(c, 0) + 1
            if len(example_titles) < 20:
                example_titles.append(title)
    print("【id.mdで保存されたタイトルの不安全原因ランキング】")
    for k, v in sorted(cause_counter.items(), key=lambda x: -x[1]):
        print(f"{k}: {v}件")

if __name__ == "__main__":
    analyze()