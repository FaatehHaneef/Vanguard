// Riverside: the menu drawer, tabs and dismissible notes. No timers, no random content.
(function () {
  // Menu drawer (small screens): opens from the right, keeps focus inside, Escape closes.
  var button = document.querySelector(".menu-button");
  var drawer = document.getElementById("drawer");
  var backdrop = document.querySelector(".drawer-backdrop");
  if (button && drawer && backdrop) {
    var focusable = function () {
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
      focusable()[0].focus();
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
      if (event.key === "Escape") close();
      if (event.key !== "Tab") return;
      var items = focusable();
      var first = items[0];
      var last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  // Tabs: arrow keys move between tabs, as in the ARIA authoring practices.
  document.querySelectorAll("[data-tabs]").forEach(function (tabs) {
    var list = tabs.querySelectorAll('[role="tab"]');
    var select = function (tab, focus) {
      list.forEach(function (other) {
        var chosen = other === tab;
        other.setAttribute("aria-selected", chosen ? "true" : "false");
        other.tabIndex = chosen ? 0 : -1;
        document.getElementById(other.getAttribute("aria-controls")).hidden = !chosen;
      });
      if (focus) tab.focus();
    };
    list.forEach(function (tab, index) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (event) {
        var next = null;
        if (event.key === "ArrowRight") next = list[(index + 1) % list.length];
        if (event.key === "ArrowLeft") next = list[(index - 1 + list.length) % list.length];
        if (event.key === "Home") next = list[0];
        if (event.key === "End") next = list[list.length - 1];
        if (next) {
          event.preventDefault();
          select(next, true);
        }
      });
    });
  });

  // Notes that stay until dismissed.
  document.querySelectorAll(".toast .close").forEach(function (close) {
    close.addEventListener("click", function () {
      close.closest(".toast").hidden = true;
    });
  });
})();
