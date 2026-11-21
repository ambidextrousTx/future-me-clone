// frontend/src/router.js
const DEFAULT_VIEW = "compose";

export function initRouter() {
  const views = document.querySelectorAll("section[data-view]");
  const links = document.querySelectorAll("nav a[data-view]");
  const names = [...views].map((v) => v.dataset.view);

  function show() {
    const requested = location.hash.slice(1);
    const current = names.includes(requested) ? requested : DEFAULT_VIEW;

    views.forEach((v) => (v.hidden = v.dataset.view !== current));
    links.forEach((a) => {
      if (a.dataset.view === current) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  window.addEventListener("hashchange", show);
  show();
}
