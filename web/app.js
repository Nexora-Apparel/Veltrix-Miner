import { ApiError, fetchControlPlaneSnapshot } from "./api.js";

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

  function setState(id, label, tone = "unknown") {
    const element = document.getElementById(id);
    if (!element) return;
    element.textContent = label;
    element.className = `state ${tone}`;
  }

  function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function errorState(error) {
    if (error?.code === "UNCONFIGURED") return ["UNCONFIGURED", "unconfigured"];
    if (error?.code === "STALE") return ["STALE", "stale"];
    if (["NOT_READY", "UNAVAILABLE"].includes(error?.code)) return ["UNAVAILABLE", "warning"];
    return ["ERROR", "error"];
  }

  function updateServiceFailure(error) {
    const [label, tone] = errorState(error);
    setState("api-service-state", label, tone);
    setValue("api-service-value", "—");
    setValue("api-service-detail", error?.message || "API service state is unknown.");
  }

  function updateDatabaseFailure(error) {
    const [label, tone] = errorState(error);
    setState("database-state", label, tone);
    setValue("database-value", "—");
    setValue("database-detail", error?.message || "Database readiness is unknown.");
  }

  function updateQuoteFailure(error) {
    const [label, tone] = errorState(error);
    for (const asset of ["btc", "xmr", "ltc", "doge"]) {
      setValue(`quote-${asset}`, "—");
      setState(`quote-${asset}-state`, label, tone);
      setValue(`quote-${asset}-detail`, error?.message || "Quote could not be verified.");
    }
  }

  function renderQuotes(quotes) {
    for (const quote of quotes) {
      const asset = quote.assetId;
      setValue(`quote-${asset}`, `$${quote.price}`);
      setState(`quote-${asset}-state`, "VERIFIED", "verified");
      setValue(
        `quote-${asset}-detail`,
        `CoinGecko · ${new Date(quote.retrievedAt).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit", second:"2-digit"})} · USD`
      );
    }
  }

  function renderSnapshot(snapshot) {
    if (snapshot.liveness.status === "fulfilled") {
      const service = snapshot.liveness.value;
      setState("api-service-state", "VERIFIED", "verified");
      setValue("api-service-value", "ONLINE");
      setValue("api-service-detail", `${service.service} v${service.version} · checked ${new Date(service.receivedAt).toLocaleTimeString()}`);
    } else {
      updateServiceFailure(snapshot.liveness.reason);
    }

    if (snapshot.readiness.status === "fulfilled") {
      setState("database-state", "VERIFIED", "verified");
      setValue("database-value", "CONNECTED");
      setValue("database-detail", `Database SELECT 1 passed · checked ${new Date(snapshot.readiness.value.receivedAt).toLocaleTimeString()}`);
    } else {
      updateDatabaseFailure(snapshot.readiness.reason);
    }

    if (snapshot.quotes.status === "fulfilled") renderQuotes(snapshot.quotes.value);
    else updateQuoteFailure(snapshot.quotes.reason);
    updated.textContent = `API CHECKED · ${new Date(snapshot.checkedAt).toLocaleTimeString()}`;
  }

  async function refreshData() {
    refresh.disabled = true;
    refresh.setAttribute("aria-busy", "true");
    refresh.querySelector("span").textContent = "Checking…";
    try {
      const snapshot = await fetchControlPlaneSnapshot();
      renderSnapshot(snapshot);
    } catch (error) {
      const safeError = error instanceof ApiError ? error : new ApiError("REQUEST_ERROR", "Unexpected API integration error.");
      updateServiceFailure(safeError);
      updateDatabaseFailure(safeError);
      updateQuoteFailure(safeError);
      updated.textContent = `CHECK FAILED · ${new Date().toLocaleTimeString()}`;
    } finally {
      refresh.disabled = false;
      refresh.removeAttribute("aria-busy");
      refresh.querySelector("span").textContent = "Refresh data";
    }
  }

  links.forEach((link) => link.addEventListener("click", (event) => {
    event.preventDefault();
    activate(link.dataset.view);
  }));
  refresh.addEventListener("click", refreshData);

  const initial = window.location.hash.replace("#", "");
  activate(links.some((link) => link.dataset.view === initial) ? initial : "overview");
  updated.textContent = "NO API CHECK PERFORMED";
})();