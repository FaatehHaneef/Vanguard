// Builds the full-view observation (perception alternative "b": a DOM summary).
// Runs in the page through Playwright's evaluate(). It never changes the DOM it
// describes, except for one short-lived clone used to measure focus visibility.
// Element refs are kept in a page-global array under a registered symbol, so the
// page's own code cannot collide with them by accident.
(() => {
  const REFS = Symbol.for("vanguard.refs");
  const HUD = "[data-vanguard-hud]";
  const INTERACTIVE =
    "a[href], button, input:not([type=hidden]), select, textarea, summary, " +
    "[contenteditable=''], [contenteditable='true'], [tabindex]:not([tabindex='-1']), " +
    "[role=button], " +
    "[role=link], [role=checkbox], [role=radio], [role=switch], [role=tab], " +
    "[role=menuitem], [role=option], [role=combobox], [role=textbox], iframe";
  // Styles that can show focus. If none changes when an element has focus, focus is
  // invisible to a sighted user (the same measurement as Sentinel's focus-visible check).
  const FOCUS_STYLES = [
    "outlineStyle",
    "outlineWidth",
    "outlineColor",
    "boxShadow",
    "borderTopColor",
    "borderBottomColor",
    "borderLeftColor",
    "borderRightColor",
    "backgroundColor",
    "color",
    "textDecorationLine",
  ];
  const MAX_NAME = 80;
  const MAX_LINE = 240;

  const clean = (text) => (text || "").replace(/\s+/g, " ").trim();
  const cut = (text, max) => (text.length > max ? text.slice(0, max - 1) + "…" : text);

  function visible(el) {
    if (el.closest(HUD)) return false;
    const style = getComputedStyle(el);
    if (style.visibility === "hidden" || style.display === "none") return false;
    if (Number(style.opacity) === 0) return false;
    const box = el.getBoundingClientRect();
    return box.width > 0 && box.height > 0;
  }

  // A sighted user sees something that looks clickable: the pointer cursor starts here.
  function looksClickable(el) {
    if (getComputedStyle(el).cursor !== "pointer") return false;
    const parent = el.parentElement;
    return !parent || getComputedStyle(parent).cursor !== "pointer";
  }

  function role(el) {
    const explicit = el.getAttribute("role");
    if (explicit) return explicit;
    const tag = el.tagName.toLowerCase();
    if (tag === "a") return "link";
    if (tag === "button" || tag === "summary") return "button";
    if (tag === "select") return "combobox";
    if (tag === "textarea") return "textbox";
    if (tag === "iframe") return "frame";
    if (tag === "input") {
      const type = (el.getAttribute("type") || "text").toLowerCase();
      if (["button", "submit", "reset", "image"].includes(type)) return "button";
      if (type === "checkbox" || type === "radio") return type;
      return "textbox";
    }
    if (el.isContentEditable) return "textbox";
    return "clickable";
  }

  function name(el) {
    const label = el.getAttribute("aria-label");
    if (label) return clean(label);
    const ids = el.getAttribute("aria-labelledby");
    if (ids) {
      const text = ids
        .split(/\s+/)
        .map((id) => document.getElementById(id)?.textContent || "")
        .join(" ");
      if (clean(text)) return clean(text);
    }
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT") {
      const own = el.labels && el.labels[0] ? clean(el.labels[0].innerText) : "";
      return own;
    }
    if (el.tagName === "IFRAME") return clean(el.getAttribute("title") || "embedded content");
    let text = clean(el.innerText);
    const pictured = el.querySelector("svg, img");
    if (pictured) {
      const alt = clean(pictured.getAttribute("alt") || "");
      text = clean(`${alt || "icon"} ${text}`);
    }
    return text || clean(el.getAttribute("title") || "");
  }

  function describe(el, ref) {
    const parts = [`[${ref}]`, role(el)];
    const label = name(el);
    if (label) parts.push(JSON.stringify(cut(label, MAX_NAME)));
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      const type = el.getAttribute("type");
      if (type === "checkbox" || type === "radio") parts.push(el.checked ? "checked" : "unchecked");
      else {
        if (el.placeholder) parts.push(`placeholder=${JSON.stringify(cut(el.placeholder, 60))}`);
        if (el.value && type !== "password") parts.push(`value=${JSON.stringify(cut(el.value, 60))}`);
      }
    }
    if (el.tagName === "SELECT" && el.selectedOptions[0]) {
      parts.push(`value=${JSON.stringify(cut(clean(el.selectedOptions[0].text), 60))}`);
    }
    if (el.disabled || el.getAttribute("aria-disabled") === "true") parts.push("disabled");
    if (el.tagName === "A") {
      const href = el.href;
      if (href) {
        const url = new URL(href);
        parts.push("->", url.origin === location.origin ? url.pathname + url.search : href);
      }
    }
    return parts.join(" ");
  }

  function isBlock(el) {
    const display = getComputedStyle(el).display;
    return !display.startsWith("inline") && display !== "contents";
  }

  function focusShows(el) {
    // Compare the focused element with an unfocused copy in the same place.
    const parent = el.parentNode;
    if (!parent) return false;
    const copy = el.cloneNode(false);
    copy.removeAttribute("autofocus");
    parent.insertBefore(copy, el.nextSibling);
    try {
      const focused = getComputedStyle(el);
      const resting = getComputedStyle(copy);
      return FOCUS_STYLES.some((key) => focused[key] !== resting[key]);
    } finally {
      copy.remove();
    }
  }

  const refs = [];
  const lines = [];
  // One box per line, in document coordinates, for the magnifier's window (L3).
  const boxes = [];
  const docBox = (el) => {
    const r = el.getBoundingClientRect();
    return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height };
  };
  const textBox = (node) => {
    const range = document.createRange();
    range.selectNodeContents(node);
    return docBox(range);
  };
  const union = (a, b) => {
    const x = Math.min(a.x, b.x);
    const y = Math.min(a.y, b.y);
    return {
      x,
      y,
      width: Math.max(a.x + a.width, b.x + b.width) - x,
      height: Math.max(a.y + a.height, b.y + b.height) - y,
    };
  };
  const links = [];
  let lastBlock = null;

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const el = node;
          if (["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].includes(el.tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
          if (el.matches(HUD)) return NodeFilter.FILTER_REJECT;
          const style = getComputedStyle(el);
          if (style.display === "none") return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    },
  );

  let skipInside = null; // text inside a described element is already in its name
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (skipInside && !skipInside.contains(node)) skipInside = null;
    if (skipInside) continue;

    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node;
      if ((el.matches(INTERACTIVE) || looksClickable(el)) && visible(el)) {
        refs.push(el);
        const ref = `e${refs.length}`;
        lines.push(describe(el, ref));
        boxes.push(docBox(el));
        lastBlock = null;
        if (el.tagName === "A" && el.href) links.push(el.href);
        if (el.tagName !== "SELECT") skipInside = el;
      }
      continue;
    }

    const text = clean(node.textContent);
    const parent = node.parentElement;
    if (!text || !parent || !visible(parent)) continue;
    let block = parent;
    while (block !== document.body && !isBlock(block)) block = block.parentElement;
    const heading = block.closest("h1, h2, h3, h4, h5, h6");
    if (block === lastBlock && lines.length) {
      lines[lines.length - 1] = cut(`${lines[lines.length - 1]} ${text}`, MAX_LINE);
      boxes[boxes.length - 1] = union(boxes[boxes.length - 1], textBox(node));
    } else {
      const prefix = heading ? "#".repeat(Number(heading.tagName[1])) + " " : "";
      lines.push(cut(prefix + text, MAX_LINE));
      boxes.push(textBox(node));
      lastBlock = block;
    }
  }

  window[REFS] = refs;

  let focus = null;
  let active = document.activeElement;
  if (active && active !== document.body && active !== document.documentElement) {
    let index = refs.indexOf(active);
    if (index < 0) {
      refs.push(active);
      index = refs.length - 1;
    }
    focus = {
      ref: `e${index + 1}`,
      box: docBox(active),
      visible: active.tagName === "IFRAME" ? false : focusShows(active),
      inFrame: active.tagName === "IFRAME",
    };
  }

  return {
    title: document.title,
    url: location.href,
    lines,
    boxes,
    page: { width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight },
    viewport: { width: innerWidth, height: innerHeight },
    links: Array.from(new Set(links)),
    focus,
    count: refs.length,
  };
})();
