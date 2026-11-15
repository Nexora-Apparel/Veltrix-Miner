const ASSETS = {
  btc: "bitcoin",
  xmr: "monero",
  ltc: "litecoin",
  doge: "dogecoin",
};

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...JSON_HEADERS, ...headers },
  });
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin");
  const configured = typeof env.WEB_ORIGIN === "string" ? env.WEB_ORIGIN.trim() : "";
  if (!origin || !configured || origin !== configured) return {};
  return {
    "access-control-allow-origin": configured,
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-allow-headers": "Accept",
    "access-control-max-age": "300",
    "vary": "Origin",
  };
}

function decimalString(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? String(value) : null;
}

async function marketQuotes(request, env) {
  const url = new URL(request.url);
  const requested = (url.searchParams.get("assets") || "btc,xmr,ltc,doge")
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);

  if (
    requested.length < 1 ||
    requested.length > 4 ||
    new Set(requested).size !== requested.length ||
    requested.some((asset) => !Object.hasOwn(ASSETS, asset))
  ) {
    return json({ detail: "Request between one and four unique supported assets" }, 400);
  }

  const ids = requested.map((ticker) => ASSETS[ticker]);
  const upstreamUrl = new URL("https://api.coingecko.com/api/v3/simple/price");
  upstreamUrl.search = new URLSearchParams({
    ids: ids.join(","),
    vs_currencies: "usd",
    include_market_cap: "true",
    include_24hr_vol: "true",
    include_24hr_change: "true",
  }).toString();

  const headers = {};
  if (env.COINGECKO_DEMO_API_KEY) {
    headers["x-cg-demo-api-key"] = env.COINGECKO_DEMO_API_KEY;
  }

  let payload;
  try {
    const upstream = await fetch(upstreamUrl, {
      method: "GET",
      headers,
      signal: AbortSignal.timeout(6000),
    });
    if (!upstream.ok) return json({ detail: "Market data temporarily unavailable" }, 503);
    payload = await upstream.json();
  } catch {
    return json({ detail: "Market data temporarily unavailable" }, 503);
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return json({ detail: "Market data temporarily unavailable" }, 503);
  }

  const retrievedAt = new Date().toISOString();
  const quotes = [];
  for (let index = 0; index < requested.length; index += 1) {
    const ticker = requested[index];
    const row = payload[ids[index]];
    const price = decimalString(row?.usd);
    if (!row || !price || !Number.isFinite(Number(price)) || Number(price) <= 0) {
      return json({ detail: "Market data temporarily unavailable" }, 503);
    }
    quotes.push({
      asset_id: ticker,
      currency: "usd",
      price,
      market_cap: decimalString(row.usd_market_cap),
      volume_24h: decimalString(row.usd_24h_vol),
      change_24h_pct: decimalString(row.usd_24h_change),
      source: "coingecko",
      retrieved_at: retrievedAt,
    });
  }
  return json(quotes);
}

async function handleApi(request, env) {
  const path = new URL(request.url).pathname;
  const headers = corsHeaders(request, env);

  if (request.method === "OPTIONS") {
    if (!headers["access-control-allow-origin"]) {
      return new Response(null, { status: 403, headers: { vary: "Origin" } });
    }
    return new Response(null, { status: 204, headers });
  }
  if (request.method !== "GET") {
    return json({ detail: "Method not allowed" }, 405, { allow: "GET, OPTIONS", ...headers });
  }

  if (path === "/api/v1/health/live") {
    return json({
      status: "alive",
      service: "VELTRIX MINER API",
      version: "0.2.0",
    }, 200, headers);
  }

  if (path === "/api/v1/health/ready") {
    if (!env.DB) {
      return json({
        detail: {
          status: "not_ready",
          service: "VELTRIX MINER API",
          version: "0.2.0",
          database: "not_configured",
        },
      }, 503, headers);
    }
    try {
      const migration = await env.DB.prepare(\n        "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1"\n      ).first();\n      if (!migration?.version) throw new Error("D1 schema is not migrated");
      return json({
        status: "ready",
        service: "VELTRIX MINER API",
        version: "0.2.0",
        database: "connected",
      }, 200, headers);
    } catch {
      return json({
        detail: {
          status: "not_ready",
          service: "VELTRIX MINER API",
          version: "0.2.0",
          database: "unavailable",
        },
      }, 503, headers);
    }
  }

  if (path === "/api/v1/market/quotes") {
    const response = await marketQuotes(request, env);
    const merged = new Headers(response.headers);
    for (const [key, value] of Object.entries(headers)) merged.set(key, value);
    return new Response(response.body, { status: response.status, headers: merged });
  }

  return json({ detail: "Not found" }, 404, headers);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) return handleApi(request, env);
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD" } });
    }
    return env.ASSETS.fetch(request);
  },
};

export { handleApi, marketQuotes };
