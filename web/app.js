(() => {
  "use strict";
  const links = Array.from(document.querySelectorAll("[data-view]"));
  const views = Array.from(document.querySelectorAll(".view"));
  const title = document.getElementById("page-title");
  const updated = document.getElementById("last-updated");
  const refresh = document.getElementById("refresh-button");

  function activate(viewName) {
    const selected = links.find((link) => link.dataset.view === viewName) || links[0];
    const name = selected.dataset.view;
    links.forEach((link) => {
      const active = link === selected;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    views.forEach((view) => view.classList.toggle("active-view", view.id === `view-${name}`));
    title.textContent = selected.textContent.trim();
    if (window.location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
  }

  links.forEach((link) => link.addEventListener("click", (event) => {
    event.preventDefault();
    activate(link.dataset.view);
  }));

  function stampViewLoad() {
    const now = new Date();
    updated.textContent = `VIEW REFRESHED · ${now.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}`;
  }

  refresh.addEventListener("click", stampViewLoad);
  const initial = window.location.hash.replace("#", "");
  activate(links.some((link) => link.dataset.view === initial) ? initial : "overview");
  stampViewLoad();
})();