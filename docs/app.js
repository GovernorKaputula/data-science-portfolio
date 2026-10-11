"use strict";
document.querySelectorAll(".filter").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    let count = 0;
    document.querySelectorAll(".project-card").forEach(card => {
      const visible = button.dataset.filter === "all" || card.dataset.category === button.dataset.filter;
      card.hidden = !visible;
      count += Number(visible);
    });
    document.querySelector(".result-count").textContent = `${String(count).padStart(2, "0")} ${count === 1 ? "study" : "studies"}`;
  });
});
const budget = document.querySelector("#budget");
if (budget) {
  const outcomes = JSON.parse(document.querySelector("#budget-data").textContent);
  const update = () => {
    const row = outcomes[Number(budget.value)];
    document.querySelector("#budget-value").textContent = `${row.budget_pct}% of contacts`;
    document.querySelector("#budget-precision").textContent = `${(row.precision * 100).toFixed(1)}%`;
    document.querySelector("#budget-recall").textContent = `${(row.recall * 100).toFixed(1)}%`;
    document.querySelector("#budget-lift").textContent = `${row.lift.toFixed(2)}×`;
    budget.setAttribute("aria-valuetext", `${row.budget_pct} percent of contacts`);
    document.querySelector("#budget-detail").textContent = `${row.contacts.toLocaleString()} contacts selected; ${row.responses.toLocaleString()} observed responses. Retrospective ranking on the same holdout.`;
  };
  budget.addEventListener("input", update);
  update();
}
