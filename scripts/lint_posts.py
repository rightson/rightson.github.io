#!/usr/bin/env python3
"""Blocking lint for new posts (AGENTS.md §3–§9, §11).

Only posts whose front-matter `date` is at or after NEW_POST_CUTOFF are
checked; older posts are exempt until they are deliberately rewritten.

Usage:
  python3 scripts/lint_posts.py                  # lint every new post in _posts/
  python3 scripts/lint_posts.py _posts/x.md ...  # lint given files (cutoff still applies)
  python3 scripts/lint_posts.py --all            # ignore cutoff (report only on old posts)
  python3 scripts/lint_posts.py --block          # CI: move failing new posts to _blocked/
                                                 # (with a .lint.txt report) so they are not published

Exit status: 0 = clean, 1 = at least one violation.
"""
import datetime as dt
import os
import re
import sys

import yaml

NEW_POST_CUTOFF = dt.datetime(2026, 10, 2, 13, 0, tzinfo=dt.timezone(dt.timedelta(hours=8)))
POSTS_DIR = "_posts"
BLOCKED_DIR = "_blocked"
EVIDENCE_HEADING = "證據範圍"
TAIL_HEADINGS = ("證據範圍", "References", "參考資料", "來源", "Sources")

# Per-10,000-character limits, measured on the article body outside the
# evidence-scope and reference sections.
HEDGE_LIMIT = 12.0
FRAME_LIMIT = 15.0
FRAME_LIMIT_BY_DOMAIN = {"ic-design-platform": 25.0, "distributed-systems": 25.0}
HEDGE_RE = re.compile(r"不能|不代表|不等於|並非|而非|不可|不宜|未必")
FRAME_RE = re.compile(r"驗收|邊界|證據|恢復|契約|閘門|可採信")

DOMAINS = {
    "ic-design-platform", "ai-frontier", "architecture", "networking",
    "distributed-systems", "platform-engineering", "ai-industry", "investing",
}

# Sentence skeletons already overused on the site (title, description, opening).
TEMPLATE_PATTERNS = [
    (r"不是[^。，；]{0,30}[，,]?而是", "「不是 A，而是 B」句型"),
    (r"而不只是", "「而不只是」句型"),
    (r"真正的(突破|核心|關鍵|難點|效率|問題|價值)", "「真正的 X」句型"),
    (r"(分水嶺|拐點)", "「分水嶺／拐點」句型"),
    (r"(價值|可靠性|可信度|可信|意義|收益|關鍵)[^，。；]{0,10}(取決於|在於|來自於?|前提是)", "「X 的價值取決於／在於」句型"),
    (r"值得(回頭)?(研究|放在|注意|追蹤|用來)", "「值得…」開頭句型"),
    (r"最值得(注意|警戒|關注)", "「最值得注意」句型"),
]

# Wording that exposes internal process, private research frameworks or an
# authorial stance. Matched anywhere in the body, title, description and summary.
BANNED_TERMS = [
    (r"作者(設計|推論|分析|整理|提出|參考|依據|判斷|觀點|認為)", "標註作者立場（改用「推論」「參考設計」「假設算例」）"),
    (r"(最近|過去)\s*\d+\s*(?:[–\-～至]\s*\d+\s*)?小時|近\s*(?:24|48|72)\s*(?:[–\-～至]\s*\d+\s*)?小時", "排程搜尋窗口外漏（改寫具體日期）"),
    (r"中譯|節錄與補充|補充整理|最初的.{0,6}觀察來自", "素材取得過程外漏"),
    (r"(?i)regime reversal|good-news failure|estimate peak|margin inflection|early positioning|thesis breakdown|earnings inflection", "內部研究框架術語（改用一般讀者懂的中文描述）"),
    (r"(?i)(capital|research|fundamentals?|flow|price|revision)\s*[↑↓→]", "內部框架符號（例如 Capital ↑）"),
    (r"本篇如何|本文將(介紹|說明|帶)|寫作框架|第一性原理|Golden Circle", "幕後寫作方法外漏"),
]

BANNED_LINKS = [
    (r"openapi\.twse\.com\.tw", "TWSE OpenAPI 全市場 JSON（改連可定位的網頁）"),
    (r"response=json", "原始 JSON 端點（改連可定位的網頁）"),
    (r"facebook\.com", "Facebook 連結（改連原始來源）"),
]

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)|href=\"(https?://[^\"]+)\"")
INTERNAL_RE = re.compile(r"\]\((/(?!images/|assets/)[^)\s]+)\)|href=\"(/(?!images/|assets/)[^\"]+)\"|\{%\s*post_url\s")


def parse(path):
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return {"__yaml_error__": str(exc)}, text[m.end():]
    return fm, text[m.end():]


def post_date(fm):
    d = fm.get("date")
    if isinstance(d, dt.datetime):
        return d if d.tzinfo else d.replace(tzinfo=NEW_POST_CUTOFF.tzinfo)
    if isinstance(d, dt.date):
        return dt.datetime(d.year, d.month, d.day, tzinfo=NEW_POST_CUTOFF.tzinfo)
    if isinstance(d, str):
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M %z", "%Y-%m-%d"):
            try:
                v = dt.datetime.strptime(d.strip(), fmt)
                return v if v.tzinfo else v.replace(tzinfo=NEW_POST_CUTOFF.tzinfo)
            except ValueError:
                pass
    return None


def split_sections(body):
    """Return (main_text, tail_text) where tail = evidence-scope + references."""
    lines = body.split("\n")
    for i, line in enumerate(lines):
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h and any(h.group(1).startswith(t) for t in TAIL_HEADINGS):
            return "\n".join(lines[:i]), "\n".join(lines[i:])
    return body, ""


def prose(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<figure.*?</figure>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    return text


def density(regex, text, size):
    return len(regex.findall(text)) * 10000 / max(size, 1)


def first_paragraph(body):
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if b and not b.startswith(("<", "#", "|", "!", "-", ">")):
            return prose(b)
    return ""


def lint(path):
    errs = []
    fm, body = parse(path)
    if fm is None:
        return ["缺少 front matter"]
    if "__yaml_error__" in fm:
        return ["front matter YAML 錯誤：" + fm["__yaml_error__"]]

    title = str(fm.get("title", ""))
    desc = str(fm.get("description", ""))
    summary = fm.get("summary")

    for key in ("title", "date", "domain", "categories", "description", "summary"):
        if not fm.get(key):
            errs.append(f"front matter 缺少 {key}")
    domain = fm.get("domain")
    if domain and domain not in DOMAINS:
        errs.append(f"domain 不在八個公開分類內：{domain}")
    cats = fm.get("categories")
    if domain and cats and str(cats).strip() != str(domain):
        errs.append("新文章 categories 必須與 domain 相同")
    if summary is not None:
        if not isinstance(summary, list) or not 3 <= len(summary) <= 5:
            errs.append("summary 必須是 3–5 條的清單")
        else:
            for s in summary:
                if not isinstance(s, str) or not 8 <= len(s) <= 80:
                    errs.append(f"summary 每條須為 8–80 字的判斷句：{s!r}")

    if re.search(r"[：:]", title):
        errs.append("標題不得使用冒號；直接寫成一句結論或問題")

    opening = first_paragraph(body)
    for field, text in (("標題", title), ("description", desc), ("開頭段", opening)):
        for pat, label in TEMPLATE_PATTERNS:
            if re.search(pat, text):
                errs.append(f"{field}使用模板化{label}")

    summary_text = " ".join(summary) if isinstance(summary, list) else ""
    whole = "\n".join([title, desc, summary_text, prose(body)])
    for pat, label in BANNED_TERMS:
        m = re.search(pat, whole)
        if m:
            errs.append(f"{label}：「{m.group(0)}」")
    for pat, label in BANNED_LINKS:
        if re.search(pat, body):
            errs.append(label)

    if not re.search(rf"^##\s+{EVIDENCE_HEADING}\s*$", body, re.M):
        errs.append(f"缺少「## {EVIDENCE_HEADING}」段落（保留條件集中於此）")

    main, _ = split_sections(body)
    main_prose = prose(main)
    size = len(re.findall(r"[一-鿿A-Za-z0-9]", main_prose))
    hd = density(HEDGE_RE, main_prose, size)
    if hd > HEDGE_LIMIT:
        errs.append(f"正文否定／保留語密度 {hd:.1f}／萬字，上限 {HEDGE_LIMIT}；把限制移到「{EVIDENCE_HEADING}」，正文直接下判斷")
    fd = density(FRAME_RE, main_prose, size)
    flimit = FRAME_LIMIT_BY_DOMAIN.get(domain, FRAME_LIMIT)
    if fd > flimit:
        errs.append(f"框架詞（驗收／邊界／證據／恢復／契約）密度 {fd:.1f}／萬字，上限 {flimit}；結論須回到本分類的核心問題（AGENTS.md §5）")

    if not INTERNAL_RE.search(body):
        errs.append("沒有任何站內文章連結；至少連一篇相關既有文章")
    if not LINK_RE.search(body):
        errs.append("沒有任何外部來源連結")
    return errs


def main(argv):
    block = "--block" in argv
    ignore_cutoff = "--all" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        files = sorted(os.path.join(POSTS_DIR, f) for f in os.listdir(POSTS_DIR) if f.endswith((".md", ".markdown")))
    failed = {}
    checked = 0
    for path in files:
        fm, _ = parse(path)
        d = post_date(fm) if isinstance(fm, dict) else None
        if not ignore_cutoff and (d is None or d < NEW_POST_CUTOFF):
            continue
        checked += 1
        errs = lint(path)
        if errs:
            failed[path] = errs
            print(f"✗ {path}")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ {path}")
    print(f"\n檢查 {checked} 篇新文章，{len(failed)} 篇未通過。")
    if not block:
        return 1 if failed else 0

    os.makedirs(BLOCKED_DIR, exist_ok=True)
    for path, errs in failed.items():
        name = os.path.basename(path)
        os.replace(path, os.path.join(BLOCKED_DIR, name))
        with open(os.path.join(BLOCKED_DIR, name + ".lint.txt"), "w", encoding="utf-8") as f:
            f.write(f"{path} 未通過 scripts/lint_posts.py，已移出 _posts/，不會發布。\n")
            f.write("修正後移回 _posts/（保留原檔名與 date）並重新提交。\n\n")
            f.write("\n".join(f"- {e}" for e in errs) + "\n")
        print(f"已移至 {BLOCKED_DIR}/：{name}")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path and failed:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("## 未發布：以下新文章未通過 lint，已移至 `_blocked/`\n\n")
            for path, errs in failed.items():
                f.write(f"### `{path}`\n" + "\n".join(f"- {e}" for e in errs) + "\n\n")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"failed={len(failed)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
