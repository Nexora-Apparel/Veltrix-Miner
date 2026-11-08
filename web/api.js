import { VELTRIX_CONFIG } from "./config.js";

export class ApiError extends Error {
  constructor(code, message, status = null) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

const ASSETS = ["btc", "xmr", "ltc", "doge"];
const DECIMAL = /^\d+(?:\.\d+)?$/;

function apiRoot() {
  const configured = VELTRIX_CONFIG.apiBaseUrl.trim();
  if (!configured) throw new ApiError("UNCONFIGURED", "API base URL has not been configured.");
  let url;
  try {
    url = new URL(configured, window.location.origin);
  } catch {
    throw new ApiError("CONFIG_ERROR", "API base URL is invalid.");
  }
  if (url.username || url.password || url.search || url.hash) {
    throw new ApiError("CONFIG_ERROR", "API base URL must not contain credentials, query parameters or fragments.");
  }
  const localHost = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
  if (url.protocol !== "https:" && !(url.protocol === "http:" && localHost)) {
    throw new ApiError("CONFIG_ERROR", "Remote API connections must use HTTPS.");
  }
  return url;
}

function endpoint(path) {
  const root = apiRoot();
  const prefix = root.pathname.endsWith("/") ? root.pathname : root.pathname + "/";
  root.pathname = prefix;
  return new URL(path.replace(/^\//, ""), root);
}

async function getJson(path) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), VELTRIX_CONFIG.requestTimeoutMs);
  try {
    const response = await fetch(endpoint(path), {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "omit",
      redirect: "error",
      signal: controller.signal
    });
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.toLowerCase().includes("application/json")) {
      throw new ApiError("INVALID_CONTENT_TYPE", "API did not return JSON.", response.status);
    }
    let payload;
    try {
      payload = await response.json();
    } catch {
      throw new ApiError("INVALID_JSON", "API returned malformed JSON.", response.status);
    }
    if (!response.ok) {
      const detail = typeof payload?.detail === "object" ? payload.detail : null;
      throw new ApiError(
        response.status === 503 ? "UNAVAILABLE" : "HTTP_ERROR",
        detail?.database ? `Service not ready: database ${detail.database}.` : `API request failed (HTTP ${response.status}).`,
        response.status
      );
    }
    return payload;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error?.name === "AbortError") throw new ApiError("TIMEOUT", "API request timed out.");
    if (error instanceof TypeError) throw new ApiError("NETWORK_ERROR", "API could not be reached. Check the API origin and CORS configuration.");
    throw new ApiError("REQUEST_ERROR", "API request failed.");
  } finally {
    window.clearTimeout(timeout);
  }
}

function validateQuote(row, nowMs) {
  if (!row || typeof row !== "object") throw new ApiError("INVALID_SCHEMA", "Quote record is not an object.");
  if (!ASSETS.includes(row.asset_id) || row.currency !== "usd") throw new ApiError("INVALID_SCHEMA", "Quote asset or currency is not supported.");
  if (typeof row.price !== "string" || !DECIMAL.test(row.price) || Number(row.price) <= 0) {
    throw new ApiError("INVALID_SCHEMA", `Invalid price for ${row.asset_id.toUpperCase()}.`);
  }
  if (row.source !== "coingecko" || typeof row.retrieved_at !== "string") {
    throw new ApiError("INVALID_SCHEMA", "Quote provenance or timestamp is missing.");
  }
  const timestamp = Date.parse(row.retrieved_at);
  if (!Number.isFinite(timestamp)) throw new ApiError("INVALID_TIMESTAMP", "Quote timestamp is invalid.");
  if (timestamp > nowMs + VELTRIX_CONFIG.quoteFutureSkewMs) {
    throw new ApiError("INVALID_TIMESTAMP", "Quote timestamp is unexpectedly in the future.");
  }
  if (nowMs - timestamp > VELTRIX_CONFIG.quoteMaxAgeMs) {
    throw new ApiError("STALE", `${row.asset_id.toUpperCase()} quote is older than the allowed freshness window.`);
  }
  for (const field of ["market_cap", "volume_24h", "change_24h_pct"]) {
    if (row[field] !== null && row[field] !== undefined &&
        (typeof row[field] !== "string" || !/^-?\d+(?:\.\d+)?$/.test(row[field]))) {
      throw new ApiError("INVALID_SCHEMA", `Invalid ${field} for ${row.asset_id.toUpperCase()}.`);
    }
  }
  return Object.freeze({
    assetId: row.asset_id,
    price: row.price,
    marketCap: row.market_cap ?? null,
    volume24h: row.volume_24h ?? null,
    change24hPct: row.change_24h_pct ?? null,
    source: row.source,
    retrievedAt: new Date(timestamp).toISOString(),
    ageMs: Math.max(0, nowMs - timestamp)
  });
}

export async function fetchLiveness() {
  const payload = await getJson("api/v1/health/live");
  if (payload?.status !== "alive" || typeof payload.service !== "string" || typeof payload.version !== "string") {
    throw new ApiError("INVALID_SCHEMA", "Liveness response did not match the expected contract.");
  }
  return Object.freeze({ status: payload.status, service: payload.service, version: payload.version, receivedAt: new Date().toISOString() });
}

export async function fetchReadiness() {
  const payload = await getJson("api/v1/health/ready");
  if (payload?.status !== "ready" || payload.database !== "connected") {
    throw new ApiError("NOT_READY", "API is responding but its database is not ready.");
  }
  return Object.freeze({ status: payload.status, database: payload.database, receivedAt: new Date().toISOString() });
}

export async function fetchMarketQuotes() {
  const payload = await getJson(`api/v1/market/quotes?assets=${ASSETS.join(",")}`);
  if (!Array.isArray(payload)) throw new ApiError("INVALID_SCHEMA", "Market response must be an array.");
  const nowMs = Date.now();
  const quotes = payload.map((row) => validateQuote(row, nowMs));
  const byAsset = new Map(quotes.map((quote) => [quote.assetId, quote]));
  if (byAsset.size !== ASSETS.length || ASSETS.some((asset) => !byAsset.has(asset))) {
    throw new ApiError("INCOMPLETE_DATA", "Market response did not contain all requested assets.");
  }
  return ASSETS.map((asset) => byAsset.get(asset));
}

export async function fetchControlPlaneSnapshot() {
  if (!VELTRIX_CONFIG.apiBaseUrl.trim()) {
    throw new ApiError("UNCONFIGURED", "Set apiBaseUrl in web/config.js after a verified backend deployment exists.");
  }
  const [liveness, readiness, quotes] = await Promise.allSettled([
    fetchLiveness(), fetchReadiness(), fetchMarketQuotes()
  ]);
  return Object.freeze({ liveness, readiness, quotes, checkedAt: new Date().toISOString() });
}
