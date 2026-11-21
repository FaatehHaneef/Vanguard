// Records low-level input events for the leakage checker (docs/leakage-spec.md, H1).
// Added to every document before the page's own scripts run. Each event is sent to
// the executor at once through an exposed binding, so events survive navigation.
// isTrusted is true only for input the browser itself produced (Playwright's real
// keyboard and mouse), never for events a page script dispatched.
(() => {
  const REFS = Symbol.for("vanguard.refs");
  const send = window.__vanguardRecord;
  if (typeof send !== "function") return;

  function describe(target) {
    const refs = window[REFS] || [];
    for (let node = target; node && node.nodeType === 1; node = node.parentElement) {
      const index = refs.indexOf(node);
      if (index >= 0) return `e${index + 1}`;
    }
    return target && target.nodeName ? target.nodeName.toLowerCase() : null;
  }

  for (const type of ["pointerdown", "mousedown", "wheel", "keydown", "focusin"]) {
    window.addEventListener(
      type,
      (event) => {
        try {
          send({
            type,
            trusted: event.isTrusted,
            target: type === "keydown" ? event.key : describe(event.target),
          });
        } catch {
          // Recording must never break the page.
        }
      },
      { capture: true, passive: true },
    );
  }
})();
