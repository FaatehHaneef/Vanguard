// Weekly calendar for the chosen doctor.
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const TIMES = ["09:00", "09:30", "10:00", "10:30", "11:00", "14:00", "14:30", "15:00"];
const WORKDAYS = {
  malik: ["Monday", "Tuesday", "Thursday"],
  rehman: ["Monday", "Wednesday", "Friday"],
  ahmed: ["Tuesday", "Thursday"],
};
const TAKEN = {
  malik: { Monday: ["09:00"], Tuesday: ["09:00", "09:30"], Thursday: ["10:00"] },
  rehman: { Monday: ["09:00", "09:30"], Wednesday: ["11:00"], Friday: [] },
  ahmed: { Tuesday: ["14:00"], Thursday: ["09:00", "09:30", "10:00"] },
};

const week = document.getElementById("week");
const doctor = document.getElementById("doctor");
const chosenText = document.getElementById("chosen");
const problem = document.getElementById("problem");
let chosen = null;

function draw() {
  week.innerHTML = "";
  chosen = null;
  chosenText.textContent = "";
  const who = doctor.value;
  for (const day of DAYS) {
    const column = document.createElement("div");
    column.className = "day";
    const heading = document.createElement("h3");
    heading.textContent = day;
    column.appendChild(heading);
    if (!WORKDAYS[who].includes(day)) {
      const off = document.createElement("p");
      off.className = "room";
      off.textContent = "No clinic";
      column.appendChild(off);
    } else {
      for (const time of TIMES) {
        const slot = document.createElement("div");
        const taken = (TAKEN[who][day] || []).includes(time);
        slot.className = `slot ${taken ? "full" : "open"}`;
        slot.textContent = time;
        if (!taken) {
          slot.addEventListener("click", () => {
            document.querySelectorAll(".slot.chosen").forEach((el) => el.classList.remove("chosen"));
            slot.classList.add("chosen");
            chosen = { day, time };
            chosenText.textContent = `Selected: ${day} at ${time}`;
          });
        }
        column.appendChild(slot);
      }
    }
    week.appendChild(column);
  }
}

doctor.addEventListener("change", draw);

document.getElementById("continue").addEventListener("click", () => {
  if (!chosen) {
    problem.hidden = false;
    problem.textContent = "Please choose a time first.";
    return;
  }
  const name = doctor.options[doctor.selectedIndex].text;
  sessionStorage.setItem(
    "willowbrook.booking",
    JSON.stringify({ doctor: name, day: chosen.day, time: chosen.time }),
  );
  location.href = "/details.html";
});

draw();
