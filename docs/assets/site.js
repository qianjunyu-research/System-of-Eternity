const yearTarget = document.querySelector("[data-current-year]");
if (yearTarget) {
  yearTarget.textContent = new Date().getFullYear();
}

const links = document.querySelectorAll("a[href^='http']");
for (const link of links) {
  link.rel = "noopener noreferrer";
  link.target = "_blank";
}
