// Public API origin only. Leave empty until a verified backend deployment exists.
// Examples: "https://api.example.com" or "http://localhost:8000" for local development.
// Never put API keys, database credentials or other secrets in browser-delivered files.
export const VELTRIX_CONFIG = Object.freeze({
  apiBaseUrl: "",
  requestTimeoutMs: 6500,
  quoteMaxAgeMs: 120000,
  quoteFutureSkewMs: 60000
});
