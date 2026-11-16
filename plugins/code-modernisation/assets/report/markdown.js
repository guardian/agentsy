/* Markdown presentation for saved reports. Raw records remain authoritative. */
(() => {
  "use strict";
  const slug = text => text.toLowerCase().replace(/[^\p{L}\p{N}_\s-]/gu, "").replace(/\s/g, "-") || "section";

  function safeMarkdownHref(value, sourcePath = "", prefix = "markdown") {
    if (typeof value !== "string" || !value || value.length > 2048 || value !== value.trim()) return null;
    let decoded = value;
    for (let count = 0; count < 5; count += 1) {
      let next;
      try { next = decodeURIComponent(decoded); } catch { return null; }
      if (next === decoded) break;
      decoded = next;
    }
    if (/[\u0000-\u001f\u007f\\]/u.test(decoded) || decoded !== decoded.trim() || decoded.startsWith("/")) return null;
    if (/^[a-z][a-z0-9+.-]*:/i.test(decoded)) {
      try {
        const url = new URL(value);
        return ["https:", "http:", "mailto:"].includes(url.protocol) ? value : null;
      } catch { return null; }
    }
    if (value.startsWith("#")) return "#" + prefix + "-" + slug(decoded.slice(1));
    // Parent-relative source links are intentional. They are followed only on
    // click; rendering never reads their targets or embeds remote resources.
    if (typeof sourcePath !== "string" || /[:\\\u0000-\u001f\u007f]/u.test(sourcePath) || sourcePath.startsWith("/")) return null;
    return sourcePath.slice(0, sourcePath.lastIndexOf("/") + 1) + value;
  }

  function createMarkdownRenderer(MarkdownIt) {
    const parser = new MarkdownIt({ html: false, linkify: false, typographer: false });
    parser.renderer.rules.image = (tokens, index) => parser.utils.escapeHtml(tokens[index].content || "[Image]");
    parser.renderer.rules.link_open = (tokens, index, options, env, self) => {
      const token = tokens[index];
      const href = safeMarkdownHref(token.attrGet("href"), env.sourcePath, env.fragmentPrefix);
      if (href === null) token.attrs = (token.attrs || []).filter(([key]) => key !== "href");
      else {
        token.attrSet("href", href);
        if (!href.startsWith("#")) {
          token.attrSet("target", "_blank");
          token.attrSet("rel", "noopener noreferrer");
        }
      }
      return self.renderToken(tokens, index, options);
    };
    parser.renderer.rules.heading_open = (tokens, index, options, env, self) => {
      const text = (tokens[index + 1].children || []).map(token =>
        ["softbreak", "hardbreak"].includes(token.type) ? " " : token.content).join("");
      const base = slug(text);
      let name = base, count = 0;
      while (env.headings.has(name)) name = base + "-" + (++count);
      env.headings.add(name);
      tokens[index].attrSet("id", env.prefix + "-" + name);
      return self.renderToken(tokens, index, options);
    };
    return (text, sourcePath = "", prefix = "markdown", inline = false, context = {}) => {
      const env = { sourcePath, prefix, fragmentPrefix: context.fragmentPrefix || prefix, headings: new Set() };
      // Excerpts may use reference definitions or headings elsewhere in the
      // original document. Parse only its saved text, never a linked resource.
      if (typeof context.referencesText === "string" && context.referencesText !== text) parser.parse(context.referencesText, env);
      return inline ? parser.renderInline(text, env) : parser.render(text, env);
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { safeMarkdownHref, createMarkdownRenderer };
  } else {
    window.renderReportMarkdown = createMarkdownRenderer(window.markdownit);
  }
})();
