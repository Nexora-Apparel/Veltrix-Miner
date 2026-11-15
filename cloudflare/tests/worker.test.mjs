import test from "node:test";
import assert from "node:assert/strict";
import worker from "../worker.mjs";

function request(path, options = {}) {
  return new Request(`https://veltrix-miner.example${path}`, options);
}

test("liveness works without database configuration", async () => {
  const response = await worker.fetch(request("/api/v1/health/live"), {});
  assert.equal(response.status, 200);
  assert.equal((await response.json()).status, "alive");
});

test("readiness is not ready when D1 is not configured", async () => {
  const response = await worker.fetch(request("/api/v1/health/ready"), {});
  assert.equal(response.status, 503);
  assert.equal((await response.json()).detail.database, "not_configured");
});

test("readiness verifies D1 with a bounded read-only query", async () => {
  let statement = "";
  const env = {
    DB: {
      prepare(sql) {
        statement = sql;
        return { first: async () => ({ version: "0001_initial" }) };
      },
    },
  };
  const response = await worker.fetch(request("/api/v1/health/ready"), env);
  assert.equal(response.status, 200);
  assert.match(statement, /FROM schema_migrations/);
  assert.equal((await response.json()).database, "connected");
});

test("readiness reports D1 failures without leaking provider details", async () => {
  const env = { DB: { prepare: () => ({ first: async () => { throw new Error("private"); } }) } };
  const response = await worker.fetch(request("/api/v1/health/ready"), env);
  assert.equal(response.status, 503);
  assert.equal((await response.text()).includes("private"), false);
});

test("market endpoint returns the existing normalized quote contract", async (t) => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    assert.match(String(url), /api\.coingecko\.com/);
    return Response.json({
      bitcoin: { usd: 65000.12, usd_market_cap: 1e12, usd_24h_vol: 2e10, usd_24h_change: 1.25 },
    });
  };
  t.after(() => { globalThis.fetch = originalFetch; });

  const response = await worker.fetch(request("/api/v1/market/quotes?assets=btc"), {});
  assert.equal(response.status, 200);
  const [quote] = await response.json();
  assert.equal(quote.asset_id, "btc");
  assert.equal(quote.currency, "usd");
  assert.equal(quote.price, "65000.12");
  assert.equal(quote.source, "coingecko");
  assert.ok(quote.retrieved_at);
});

test("market endpoint rejects unsupported or duplicate assets", async () => {
  const unsupported = await worker.fetch(request("/api/v1/market/quotes?assets=btc,nope"), {});
  const duplicate = await worker.fetch(request("/api/v1/market/quotes?assets=btc,btc"), {});
  assert.equal(unsupported.status, 400);
  assert.equal(duplicate.status, 400);
});

test("market endpoint fails closed when provider data is incomplete", async (t) => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => Response.json({});
  t.after(() => { globalThis.fetch = originalFetch; });
  const response = await worker.fetch(request("/api/v1/market/quotes?assets=btc"), {});
  assert.equal(response.status, 503);
});

test("CORS permits only the exact configured origin", async () => {
  const env = { WEB_ORIGIN: "https://console.example" };
  const allowed = await worker.fetch(request("/api/v1/health/live", {
    headers: { Origin: "https://console.example" },
  }), env);
  const denied = await worker.fetch(request("/api/v1/health/live", {
    headers: { Origin: "https://attacker.example" },
  }), env);
  assert.equal(allowed.headers.get("access-control-allow-origin"), "https://console.example");
  assert.equal(denied.headers.get("access-control-allow-origin"), null);
});

test("non-API requests are delegated to static assets", async () => {
  let forwarded = false;
  const env = { ASSETS: { fetch: async (req) => {
    forwarded = req.url.endsWith("/");
    return new Response("static shell");
  } } };
  const response = await worker.fetch(request("/"), env);
  assert.equal(forwarded, true);
  assert.equal(await response.text(), "static shell");
});
