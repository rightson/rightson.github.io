(() => {
  "use strict";
  const article = document.querySelector("[data-article]");
  if (article) {
    const text = article.textContent;
    const cjk = (text.match(/[\u3400-\u9fff]/g) || []).length;
    const words = (text.replace(/[\u3400-\u9fff]/g, " ").match(/\S+/g) || [])
      .length;
    document.querySelector("[data-reading-time]").textContent =
      `約 ${Math.max(1, Math.ceil(cjk / 400 + words / 220))} 分鐘閱讀`;
    const toc = document.querySelector("[data-toc]");
    const headings = [...article.querySelectorAll("h2, h3")];
    const used = new Set(
      [...document.querySelectorAll("[id]")].map((node) => node.id),
    );
    headings.forEach((heading, i) => {
      if (!heading.id) {
        let id = `section-${i + 1}`;
        while (used.has(id)) id += "-";
        heading.id = id;
        used.add(id);
      }
      const li = document.createElement("li");
      li.classList.toggle("subheading", heading.tagName === "H3");
      const link = document.createElement("a");
      link.href = `#${encodeURIComponent(heading.id)}`;
      link.textContent = heading.textContent;
      li.append(link);
      toc.querySelector("ol").append(li);
    });
    toc.hidden = headings.length === 0;
    if (window.matchMedia("(max-width: 900px)").matches)
      toc.querySelector("details").open = false;
    article.querySelectorAll("table").forEach((table) => {
      const wrapper = document.createElement("div");
      wrapper.className = "table-scroll";
      wrapper.tabIndex = 0;
      wrapper.setAttribute("role", "region");
      wrapper.setAttribute("aria-label", "文章表格，可左右捲動");
      table.before(wrapper);
      wrapper.append(table);
    });
  }
  const search = document.querySelector("[data-search]");
  if (!search) return;
  const input = document.querySelector("#search-input");
  const category = document.querySelector("#category-filter");
  const domain = document.querySelector("#domain-filter");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  let posts = [];
  let loaded = false;
  const normalize = (value) => value.normalize("NFKC").toLocaleLowerCase();
  function readURL() {
    const params = new URLSearchParams(location.search);
    input.value = params.get("q") || "";
    category.value = params.get("category") || "";
    domain.value = params.get("domain") || "";
  }
  function render(sync = true) {
    if (!loaded) return;
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    const matches = posts.filter(
      (post) =>
        (!category.value || post.categories.includes(category.value)) &&
        (!domain.value || post.domain === domain.value) &&
        terms.every((term) => post.searchText.includes(term)),
    );
    if (sync) {
      const params = new URLSearchParams();
      if (input.value.trim()) params.set("q", input.value.trim());
      if (category.value) params.set("category", category.value);
      if (domain.value) params.set("domain", domain.value);
      history.replaceState(
        null,
        "",
        location.pathname + (params.size ? `?${params}` : ""),
      );
    }
    status.textContent = matches.length
      ? `找到 ${matches.length} 篇文章 · 依日期由新到舊`
      : "沒有符合的文章。試試較短的關鍵字，或清除篩選條件。";
    results.replaceChildren();
    matches.forEach((post) => {
      const card = document.createElement("article");
      card.className = "post-card";
      const date = document.createElement("div");
      date.className = "card-meta";
      date.textContent = `${post.date} · ${post.categories.join(" / ")}`;
      const heading = document.createElement("h2");
      const link = document.createElement("a");
      link.href = post.url;
      link.textContent = post.title;
      heading.append(link);
      const excerpt = document.createElement("p");
      const position = terms.length
        ? normalize(post.content).indexOf(terms[0])
        : -1;
      excerpt.textContent =
        position >= 0
          ? `${position > 45 ? "…" : ""}${post.content.slice(Math.max(0, position - 45), position + 155)}…`
          : post.excerpt;
      card.append(date, heading, excerpt);
      results.append(card);
    });
  }
  readURL();
  document.querySelector("#search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    render();
  });
  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(render, 120);
  });
  category.addEventListener("change", () => render());
  domain.addEventListener("change", () => render());
  document.querySelector("#clear-search").addEventListener("click", () => {
    input.value = "";
    category.value = "";
    domain.value = "";
    render();
    input.focus();
  });
  window.addEventListener("popstate", () => {
    readURL();
    render(false);
  });
  fetch(search.dataset.index)
    .then((response) => {
      if (!response.ok) throw new Error("Index unavailable");
      return response.json();
    })
    .then((data) => {
      posts = data.map((post) => ({
        ...post,
        searchText: normalize(
          [post.title, ...post.categories, post.content].join(" "),
        ),
      }));
      loaded = true;
      render(false);
    })
    .catch(() => {
      status.textContent =
        "文章索引暫時無法載入，請重新整理，或改用分類頁瀏覽。";
      const link = document.createElement("a");
      link.href = new URL(
        "categories/",
        new URL(search.dataset.index, location.href),
      ).href;
      link.textContent = "前往文章分類 →";
      results.append(link);
    });
})();
