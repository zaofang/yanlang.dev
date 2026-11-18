// Terminals get index.txt at /, over plain http too; browsers on http are sent to https.
// Accept decides first; the user agent covers clients that send only */*.
const TERMINAL = /^(curl|wget|httpie|xh)\b/i;

function terminal(request) {
  const accept = request.headers.get("accept") ?? "";
  if (/\btext\/html\b/.test(accept)) return false;
  return /\btext\/plain\b/.test(accept) || TERMINAL.test(request.headers.get("user-agent") ?? "");
}

// /docs/spec/R345 and /docs/spec/4.2 are permanent addresses for a row and a section. Rows resolve
// through docs/rows.json, which the build writes from the spec, so they never go stale.
const SPEC_REF = /^\/docs\/spec\/(R\d+|\d+(?:\.\d+)+)$/;
let rowMap;

export async function specTarget(pathname, loadRows) {
  const ref = SPEC_REF.exec(pathname)?.[1];
  if (!ref) return null;
  if (ref[0] !== "R") return `/docs/spec/${ref.split(".")[0]}.html#${ref}`;
  rowMap ??= await loadRows();
  return rowMap[ref] ? `/${rowMap[ref]}` : null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const text = terminal(request);
    if (url.protocol === "http:" && !text) {
      url.protocol = "https:";
      return new Response(null, { status: 301, headers: { location: url.href, vary: "accept, user-agent" } });
    }
    const target = await specTarget(url.pathname, async () => {
      const res = await env.ASSETS.fetch(new URL("/docs/rows.json", url));
      return res.ok ? res.json() : {};
    });
    if (target) return Response.redirect(new URL(target, url).href, 302);
    if (url.pathname !== "/") return env.ASSETS.fetch(request);
    const res = await env.ASSETS.fetch(text ? new URL("/index.txt", url) : request);
    const out = new Response(res.body, res);
    if (text) out.headers.set("content-type", "text/plain; charset=utf-8");
    out.headers.set("vary", "accept, user-agent");
    return out;
  },
};
