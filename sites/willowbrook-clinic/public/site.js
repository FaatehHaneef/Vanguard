// Willowbrook: the menu drawer on narrow screens. Focus moves in and stays inside;
// Escape or Close returns it to the menu button.
(function () {
  var button = document.querySelector(".menu-button");
  var drawer = document.getElementById("drawer");
  var backdrop = document.querySelector(".drawer-backdrop");
  if (!button || !drawer || !backdrop) return;
  var items = function () {
    return drawer.querySelectorAll("a, button");
  };
  var open = function () {
    drawer.hidden = false;
    backdrop.hidden = false;
    requestAnimationFrame(function () {
      drawer.classList.add("open");
      backdrop.classList.add("open");
    });
    button.setAttribute("aria-expanded", "true");
    items()[0].focus();
  };
  var close = function () {
    drawer.classList.remove("open");
    backdrop.classList.remove("open");
    drawer.hidden = true;
    backdrop.hidden = true;
    button.setAttribute("aria-expanded", "false");
    button.focus();
  };
  button.addEventListener("click", open);
  backdrop.addEventListener("click", close);
  drawer.querySelector(".drawer-close").addEventListener("click", close);
  drawer.addEventListener("keydown", function (event) {
    if (event.key === "Escape") return close();
    if (event.key !== "Tab") return;
    var list = items();
    if (event.shiftKey && document.activeElement === list[0]) {
      event.preventDefault();
      list[list.length - 1].focus();
    } else if (!event.shiftKey && document.activeElement === list[list.length - 1]) {
      event.preventDefault();
      list[0].focus();
    }
  });
})();
