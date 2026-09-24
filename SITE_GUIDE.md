# Website maintenance

> **Agent note:** `AGENTS.md` is the canonical operating and publishing guide for all agents. This file remains a human-oriented site overview. If the two differ, follow the user's current instruction first, then `AGENTS.md`, and update this guide to remove drift.

This site uses native Jekyll layouts and GitHub Pages. No remote theme, JavaScript framework, external fonts, or search service is required. Post bodies and permalinks are unchanged.

## Publishing

Continue adding Markdown files to `_posts/YYYY-MM-DD-slug.md` with `layout: post`, `title`, `date`, and `categories`. Do not change existing `categories`: Jekyll uses them in default post URLs.

Add an optional `domain` to explicitly select one of the four editorial sections:

| domain | Section |
| --- | --- |
| ai-industry | AI 技術與產業 |
| investing | 投資與交易 |
| networking | 網路與互連 |
| eda | 設計與運算平台 |

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

- Homepage: newest-first articles and four persistent research sections.
- `/categories/`: static section archives, usable without JavaScript.
- `/search/`: client-side full-text search with AND matching across space-separated keywords, domain and category filters, and shareable URLs.
- `/search.json`: automatically generated from published posts at build time.
- Article pages: generated H2/H3 outline, estimated bilingual reading time, responsive tables, and previous/next links.
- Browser-native text scaling, visible keyboard focus, skip navigation, and reduced-motion support.

Search downloads the full index once. Consider a dedicated search index if the archive becomes large. Post content is never sent to an external search service.

## Validation

Build with `bundle exec jekyll build`. Verify `/`, `/categories/`, `/search/`, an existing article, and `/feed.xml`. Test a keyword found only in article content, combined filters, zero results, mobile overflow, keyboard navigation, and an index-load failure.
