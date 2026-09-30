# Website maintenance

> **Agent note:** `AGENTS.md` is the canonical operating and publishing guide for all agents. This file remains a human-oriented site overview. If the two differ, follow the user's current instruction first, then `AGENTS.md`, and update this guide to remove drift.

This site uses native Jekyll layouts and GitHub Pages. No remote theme, JavaScript framework, external fonts, or search service is required. Post bodies and permalinks are unchanged.

## Publishing

Continue adding Markdown files to `_posts/YYYY-MM-DD-slug.md` with `layout: post`, `title`, `date`, and `categories`. Do not change existing `categories`: Jekyll uses them in default post URLs.

Add an optional `domain` to explicitly select one of the seven editorial sections:

| domain | Section |
| --- | --- |
| ai-industry | 產業分析 |
| investing | 投資與交易 |
| eda | 電子設計自動化 |
| ic-design-platform | IC 設計平台 |
| architecture | 計算機架構 |
| networking | 網路與互連 |
| distributed-systems | 分散式系統 |

`domain` does not change the article URL. Existing posts are classified using `_includes/domain-key.html`; unmatched posts appear under 其他筆記. A post has one primary domain and any number of category labels. Unknown category labels remain visible, so daily publishing does not require a code change. Chinese display labels can be added to `_data/category_labels.yml`.

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

分類邊界：STA、SDC、timing closure 與 EDA 演算法歸 `eda`；多人協作、IP／SoC 整合、跨工具 R2G 流程與設計資料／執行治理歸 `ic-design-platform`。重新分類既有文章只修改 `domain`，保留 `categories` 與 URL。
