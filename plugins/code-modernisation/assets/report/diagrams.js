/* Adapted from Anthropic's code-modernization report renderer under Apache-2.0.
 * Modified for offline rendering in this Copilot port; see LICENSE and NOTICE
 * at the plugin root, also included in generated reports.
 * Diagram text is data. Rendering cannot load external resources (report CSP),
 * and the final drawing is an SVG image, not active markup in the report. */
(() => {
  "use strict";
  const LIMIT = 65536;
  function prepareDiagram(source) {
    if (typeof source !== "string" || !source.trim()) throw new Error("No diagram source recorded");
    if (source.length > LIMIT) throw new Error("Diagram exceeds the display limit");
    // Saved content must not override the renderer's security or resource settings.
    const prepared = source.replace(/\r\n?/g, "\n")
      .replace(/%%\{[\s\S]*?\}%%/g, "")
      .replace(/^\s*---[ \t]*\n[\s\S]*?\n[ \t]*---[ \t]*(?:\n|$)/, "");
    // Mermaid also accepts an unterminated directive at EOF. Keep that source
    // readable instead of letting its partial configuration change the drawing.
    if (prepared.includes("%%{")) throw new Error("Incomplete diagram configuration directive");
    if (/^\s*---[ \t]*\n/.test(prepared)) throw new Error("Multiple diagram configuration blocks");
    return prepared;
  }
  if (typeof module === "object" && module.exports) {
    module.exports = { prepareDiagram };
    return;
  }
  let ready = false, sequence = 0, queue = Promise.resolve();
  const internalUrls = text => text.replace(/url\(([^)]*)\)/gi, (whole, value) =>
    value.trim().replace(/^["']|["']$/g, "").startsWith("#") ? whole : "none");
  function imageFromSvg(markup) {
    const svg = new DOMParser().parseFromString("<!doctype html><body>" + markup, "text/html").body.querySelector("svg");
    if (!svg) throw new Error("The renderer did not produce a drawing");
    for (const node of [svg, ...svg.querySelectorAll("*")]) {
      if (/^(script|foreignObject|iframe|object|embed|link|meta|base|img|image|video|audio|source|track|picture|form|input|button|textarea|select)$/i.test(node.localName)) {
        node.remove();
        continue;
      }
      if (node.localName === "style") node.textContent = internalUrls(node.textContent.replace(/@import[^;]*;?/gi, ""));
      for (const attribute of [...node.attributes]) {
        if (/^on/i.test(attribute.name) || /^(src|srcset|action|formaction|poster)$/i.test(attribute.name)
            || (/href$/i.test(attribute.name) && !attribute.value.startsWith("#"))) {
          node.removeAttribute(attribute.name);
        } else if (/url\(/i.test(attribute.value)) {
          node.setAttribute(attribute.name, internalUrls(attribute.value));
        }
      }
    }
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const bounds = (svg.getAttribute("viewBox") || "").split(/[ ,]+/).map(Number);
    if (bounds.length === 4 && bounds.every(Number.isFinite) && bounds[2] > 0 && bounds[3] > 0) {
      svg.setAttribute("width", String(Math.ceil(bounds[2])));
      svg.setAttribute("height", String(Math.ceil(bounds[3])));
    }
    const image = document.createElement("img");
    image.className = "diagram-image";
    image.alt = "Diagram from the saved source; the source text is available below.";
    image.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new XMLSerializer().serializeToString(svg));
    return image;
  }
  async function draw(host, source) {
    let id;
    do { id = "report-diagram-render-" + (++sequence); } while (document.getElementById(id));
    try {
      const input = prepareDiagram(source);
      if (typeof mermaid === "undefined") throw new Error("The diagram renderer is unavailable");
      if (!ready) {
        mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "default",
          htmlLabels: false, flowchart: { htmlLabels: false }, maxTextSize: LIMIT,
          secure: ["securityLevel", "startOnLoad", "maxTextSize", "maxEdges", "suppressErrorRendering", "htmlLabels", "flowchart"],
          suppressErrorRendering: true, fontFamily: "system-ui, sans-serif" });
        ready = true;
      }
      await mermaid.parse(input);
      const result = await mermaid.render(id, input);
      const image = imageFromSvg(result.svg);
      await image.decode();
      host.replaceChildren(image);
      host.dataset.diagramState = "rendered";
      return true;
    } catch (error) {
      const note = document.createElement("p");
      note.className = "small muted";
      note.textContent = "This diagram could not be drawn. Its saved source is shown below.";
      const code = document.createElement("pre");
      code.textContent = typeof source === "string" ? source : "No readable diagram source.";
      host.replaceChildren(note, code);
      host.dataset.diagramState = "source";
      return false;
    } finally {
      for (const temporaryId of [id, "d" + id]) document.getElementById(temporaryId)?.remove();
    }
  }
  window.renderReportDiagram = (host, source) => {
    const result = queue.then(() => draw(host, source));
    queue = result.catch(() => {});
    return result;
  };
})();
