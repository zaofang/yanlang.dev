// Progressive enhancement for the docs: table filters and the search box. Pages read fine without it.
const norm = (s) => s.toLowerCase().trim();

for (const input of document.querySelectorAll("input[data-filter]")) {
  const rows = document.querySelectorAll("table[data-rows] tbody tr");
  const apply = () => {
    const q = norm(input.value);
    for (const tr of rows) tr.hidden = q !== "" && !tr.dataset.q.includes(q);
  };
  input.addEventListener("input", apply);
  if (location.hash.startsWith("#R") && input.dataset.filter === "rows") {
    document.getElementById(location.hash.slice(1))?.scrollIntoView();
  }
}

const search = document.querySelector("input[data-search]");
if (search) {
  const hits = document.querySelector("[data-hits]");
  let index = null;
  const load = () => (index ??= fetch(new URL("search.json", location.href)).then((r) => r.json()));
  search.addEventListener("input", async () => {
    const q = norm(search.value);
    hits.replaceChildren();
    if (!q) return;
    const entries = await load();
    // Exact ids first (R345, E301, 0084, 4.2), then substring matches in titles.
    const exact = entries.filter(([, id]) => norm(id) === q || norm(id) === q.replace(/^rfc\s*/, ""));
    const rest = entries.filter((e) => !exact.includes(e) && norm(e[1] + " " + e[2]).includes(q));
    for (const [kind, id, title, url] of [...exact, ...rest].slice(0, 30)) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = new URL(`../${url}`, location.href).href;
      a.textContent = `${kind} ${id}: ${title}`;
      li.append(a);
      hits.append(li);
    }
  });
}

document.addEventListener("keydown", (e) => {
  const field = document.querySelector("input[data-search], input[data-filter]");
  if (e.key === "/" && field && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
    e.preventDefault();
    field.focus();
  }
});
