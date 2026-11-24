// Toast notifications: a short message in a live region at the bottom of the page.
// It stays for six seconds and can be closed at any time.
let region;

function ensureRegion() {
  if (region) return region;
  region = document.createElement("div");
  region.className = "toast-region";
  region.setAttribute("role", "status");
  region.setAttribute("aria-live", "polite");
  document.body.append(region);
  return region;
}

export function showToast(message, { duration = 6000 } = {}) {
  const host = ensureRegion();
  const toast = document.createElement("div");
  toast.className = "toast";
  const text = document.createElement("p");
  text.textContent = message;
  const close = document.createElement("button");
  close.type = "button";
  close.className = "toast-close";
  close.textContent = "Dismiss";
  toast.append(text, close);
  host.append(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  const remove = () => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 250);
  };
  close.addEventListener("click", remove);
  setTimeout(remove, duration);
}
