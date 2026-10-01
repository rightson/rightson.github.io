# Website maintenance

> **Agent note:** `AGENTS.md` is the canonical operating and publishing guide for all agents. This file remains a human-oriented site overview. If the two differ, follow the user's current instruction first, then `AGENTS.md`, and update this guide to remove drift.

This site uses native Jekyll layouts and GitHub Pages. No remote theme, JavaScript framework, external fonts, or search service is required. Post bodies and permalinks are unchanged.

## Publishing

Continue adding Markdown files to `_posts/YYYY-MM-DD-slug.md` with `layout: post`, `title`, `date`, and `categories`. Do not change existing `categories`: Jekyll uses them in default post URLs.

Set one primary `domain` according to the article's main question. The seven public sections are:

| domain | Section |
| --- | --- |
| ic-design-platform | IC 設計平台 |
| ai-frontier | AI 技術與工程 |
| architecture | 運算架構 |
| networking | 網路系統 |
| distributed-systems | 分散式與系統工程 |
| ai-industry | 產業與供應鏈 |
| investing | 投資與交易 |

Five scheduler groups retain fourteen research series. Series, companies and technical names are secondary metadata, not additional navigation sections. Read `.github/ARTICLE_TAXONOMY.md` and `_data/research_series.yml` for defaults and boundaries. EDA and legacy `timing` now belong to `ic-design-platform`. Existing article `domain` may be corrected after user approval; preserve filename, date, categories, permalink and series numbering. New articles use one category equal to their domain.

```yaml
---
layout: post
title: "文章標題"
date: 2026-09-22 12:00:00 +0800
domain: ai-industry
categories: ai-supply-chain research
---
```

## Features

- Homepage: newest-first articles and seven persistent research sections.
- `/categories/`: static section archives, usable without JavaScript.
- `/search/`: client-side full-text search with AND matching across space-separated keywords, domain and category filters, and shareable URLs.
- `/search.json`: automatically generated from published posts at build time.
- Article byline: `Scott Yo-Ru Chen · AI-assisted` appears below the title beside the publication date for all existing and future posts. Author and AI assistance labels are configured in `_config.yml` and rendered by `_includes/post-byline.html`; do not duplicate the byline in post bodies or front matter.
- Article pages: generated H2/H3 outline, estimated bilingual reading time, responsive tables, and previous/next links.
- Browser-native text scaling, visible keyboard focus, skip navigation, and reduced-motion support.

Search downloads the full index once. Consider a dedicated search index if the archive becomes large. Post content is never sent to an external search service.

## Validation

Build with `bundle exec jekyll build`. Verify `/`, `/categories/`, `/search/`, an existing article, and `/feed.xml`. Test a keyword found only in article content, combined filters, zero results, mobile overflow, keyboard navigation, and an index-load failure.

分類邊界以 `.github/ARTICLE_TAXONOMY.md` 為準：企業競爭與供需歸產業；價格、估值與交易歸投資。通用 Agent 歸 AI；晶片設計流程導入與驗收歸 IC 設計平台。

## Research series and recurring work

The seven public domains follow `.github/ARTICLE_TAXONOMY.md`. Approved series, topic ownership, cadence and fresh-session migration requirements are documented in `.github/RESEARCH_SCHEDULES.md`; complete recurring prompts are in `.github/RESEARCH_AUTOMATIONS.json`. Each run reads the latest `AGENTS.md` before researching or writing. Repository specifications do not create, enable or disable scheduler tasks; runtime status requires separate verification. Existing curriculum progress, post dates, categories and permalinks are preserved.
