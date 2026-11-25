// Confirmation toasts: each message slides in at the bottom right and leaves after 3 s.
document.querySelectorAll("[data-toast]").forEach(function (toast) {
  setTimeout(function () {
    toast.classList.add("leaving");
    setTimeout(function () { toast.remove(); }, 250);
  }, 3000);
});
