// Deployment-specific public API origin. Leave empty until a verified API deployment exists.
// Examples: "https://api.example.com" or "/". Never place secrets in this file.
window.VELTRIX_CONFIG = Object.freeze({
  apiBaseUrl: "",
  requestTimeoutMs: 6500,
  quoteMaxAgeMs: 120000,
  quoteFutureSkewMs: 60000
});
