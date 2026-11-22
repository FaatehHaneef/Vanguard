(function () {
  var grid = document.querySelector(".map-grid");
  if (!grid) return;
  var input = document.getElementById("pin");
  var status = document.getElementById("pin-status");
  var cells = grid.querySelectorAll(".map-cell");
  cells.forEach(function (cell) {
    cell.addEventListener("click", function () {
      cells.forEach(function (other) { other.classList.remove("pinned"); });
      cell.classList.add("pinned");
      input.value = cell.dataset.square;
      status.textContent = "Pin placed in square " + cell.dataset.square + ".";
    });
  });
})();
