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
# Posts created at or after this time need a `lede`, a dated precedent, a
# time-bound outlook, and no visible analysis-framework vocabulary.
TAKEAWAY_CUTOFF = dt.datetime(2026, 10, 4, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=8)))
LEDE_RANGE = (180, 450)
FRAMEWORK_TERMS = re.compile(
    r"最大受益者|受益者|第[一二三]階|[一二]階思考|反方論點|影響與槓桿|(?<!營運)(?<!財務)(?<!融資)槓桿|鑑往知來"
    r"|利害關係人|(?i:takeaways?)|預測與訊號|本文的?判斷|90\s*秒"
)
LIST_LABEL_RE = re.compile(r"^\s*(?:[-*]\s*|\d+\.\s*)?(?:\*\*)?對(?:使用者|用戶|客戶|競爭者|競爭對手|合作雙方|投資人)(?:\*\*)?\s*[：:]", re.M)
FUTURE_RE = re.compile(r"(?:未來|接下來|往後|之後)\s*[一二三四五六七八九十\d]+\s*(?:個月|年|季)")
IMPACT_EXEMPT_SERIES = {"tpu-technical", "distributed-systems", "k8s-hpc", "llm-lab"}
IMPACT_EXEMPT_DOMAINS = {"science-physics"}
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
    "distributed-systems", "platform-engineering", "ai-industry", "investing", "science-physics",
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


def cjk_len(text):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", text))


def check_takeaways(items):
    errs = []
    if not isinstance(items, list) or not 3 <= len(items) <= 6:
        return ["takeaways 必須是 3–6 條的清單"]
    total = 0
    for i, t in enumerate(items, 1):
        if not isinstance(t, dict) or not t.get("who") or not t.get("value"):
            errs.append(f"takeaways 第 {i} 條須有 who 與 value")
            continue
        n = len(str(t["value"]))
        total += n
        if not 40 <= n <= 160:
            errs.append(f"takeaways 第 {i} 條 value 須為 40–160 字的完整因果句（目前 {n} 字）：{t['who']}")
    if errs:
        return errs
    if not 250 <= total <= 700:
        errs.append(f"takeaways 總長須為 250–700 字，讓讀者約 90 秒讀完（目前 {total} 字）")
    return errs


def section(body, level, title, start=0, end=None):
    """Return text of the first heading of `level` whose title starts with `title`."""
    end = len(body) if end is None else end
    hashes = "#" * level
    m = re.compile(rf"^{hashes}\s+{re.escape(title)}[^\n]*$", re.M).search(body, start, end)
    if not m:
        return None, None, None
    nxt = re.compile(rf"^#{{1,{level}}}\s", re.M).search(body, m.end(), end)
    stop = nxt.start() if nxt else end
    return body[m.end():stop], m.start(), stop


def check_depth(body, created):
    errs = []
    main, _ = split_sections(body)
    year = (created or dt.datetime.now(NEW_POST_CUTOFF.tzinfo)).year
    paragraphs = re.split(r"\n\s*\n", main)
    precedent = any(
        LINK_RE.search(p) and any(int(y) < year for y in re.findall(r"((?:19|20)\d\d)\s*年", p))
        for p in paragraphs
    )
    if not precedent:
        errs.append("正文缺少有日期、附來源連結的前例（同一段需有早於發文年份的「YYYY 年」與外部連結）")
    future_year = any(int(y) > year for y in re.findall(r"((?:19|20)\d\d)\s*年", main))
    if not (future_year or FUTURE_RE.search(main)):
        errs.append("正文缺少附時間範圍的預判（例如「2027 年底前」「未來 12 個月」）")
    return errs


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
    takeaways = fm.get("takeaways")
    created = post_date(fm)
    new_format = created is None or created >= TAKEAWAY_CUTOFF

    for key in ("title", "date", "domain", "categories", "description"):
        if not fm.get(key):
            errs.append(f"front matter 缺少 {key}")
    lede = fm.get("lede")
    if new_format:
        if not lede:
            errs.append("front matter 缺少 lede（180–450 字導言散文，AGENTS.md 第 3 節）")
        elif not LEDE_RANGE[0] <= len(str(lede)) <= LEDE_RANGE[1]:
            errs.append(f"lede 須為 {LEDE_RANGE[0]}–{LEDE_RANGE[1]} 字（目前 {len(str(lede))} 字）")
    elif not (lede or takeaways or summary):
        errs.append("front matter 缺少 lede")
    if takeaways is not None and not new_format:
        errs.extend(check_takeaways(takeaways))
    domain = fm.get("domain")
    if domain and domain not in DOMAINS:
        errs.append(f"domain 不在九個公開分類內：{domain}")
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
    if lede:
        summary_text += " " + str(lede)
    if isinstance(takeaways, list):
        summary_text += " " + " ".join(f"{t.get('who', '')} {t.get('value', '')}" for t in takeaways if isinstance(t, dict))
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

    exempt = fm.get("series") in IMPACT_EXEMPT_SERIES or domain in IMPACT_EXEMPT_DOMAINS
    if new_format:
        public = "\n".join([title, desc, str(lede or ""), prose(body)])
        m = FRAMEWORK_TERMS.search(public)
        if m:
            errs.append(f"出現分析框架詞彙「{m.group(0)}」；把分析寫成具體內容，不外顯框架（AGENTS.md 第 5 節）")
        if LIST_LABEL_RE.search(body):
            errs.append("出現「對使用者／對競爭者：」式的逐一列舉；改寫成以公司或角色為主詞的敘述")
        if not exempt:
            errs.extend(check_depth(body, created))

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
