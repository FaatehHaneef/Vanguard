// The slide-in menu: opens from the Menu button, closes with Close, the backdrop or
// Escape, keeps focus inside while open and returns it to the Menu button.
const drawer = document.getElementById("drawer");
const backdrop = document.querySelector(".drawer-backdrop");
const opener = document.querySelector("[data-drawer-open]");

function focusables() {
  return [...drawer.querySelectorAll("a[href], button")];
}

function open() {
  drawer.hidden = false;
  backdrop.hidden = false;
  requestAnimationFrame(() => {
    drawer.classList.add("open");
    backdrop.classList.add("open");
  });
  opener.setAttribute("aria-expanded", "true");
  focusables()[0].focus();
  document.addEventListener("keydown", onKey);
}

function close() {
  drawer.classList.remove("open");
  backdrop.classList.remove("open");
  opener.setAttribute("aria-expanded", "false");
  document.removeEventListener("keydown", onKey);
  setTimeout(() => {
    drawer.hidden = true;
    backdrop.hidden = true;
  }, 250);
  opener.focus();
}

function onKey(event) {
  if (event.key === "Escape") {
    close();
    return;
  }
  if (event.key !== "Tab") return;
  const items = focusables();
  const first = items[0];
  const last = items[items.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

opener?.addEventListener("click", open);
document.querySelectorAll("[data-drawer-close]").forEach((el) => el.addEventListener("click", close));
