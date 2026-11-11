# Self-hosted, Cloudflare-free two-provider gateway
This is an independent Node.js HTTP server. No Cloudflare, paid SDK, database, or orchestration service. Requires Node.js 20+.
## Local tests
`node --test ai-gateway/self-hosted/server.test.js` — tests are offline and use mock model responses.
## Running (after billing verification)
Set environment secrets `GATEWAY_TOKEN`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`. Only after verifying ALL provider accounts cannot bill you, set `ENABLED=true` and `ZERO_COST_VERIFIED=true`. Then run `node ai-gateway/self-hosted/server.js`. Default binds to 127.0.0.1:8787; do not expose HTTP directly to the internet.
## HTTPS and Custom GPT
A Custom GPT Action requires a publicly reachable HTTPS API. This local server does not supply that. Use a separately configured, trusted HTTPS reverse proxy and access controls before internet exposure; this may have costs. GitHub alone cannot host an always-on authenticated API. Do not add public API credentials to a GitHub Pages frontend.
## Hard limits
The process uses MAX_REQUESTS_PER_PROCESS (default 10) as a cap; it is NOT a provider billing limit and resets on restart. Each accepted request calls both providers once, with no retries or paid fallback. Free-tier billing status must be checked in the provider dashboards. Never run this on a billing-enabled account unless spending is otherwise guaranteed blocked.
## Privacy
Only send non-sensitive prompts with explicit user permission; both providers receive the prompt. Do not send private repository source, passwords, medical records, financial details, or employee information.
## Status
Deployed on Render Free at https://three-model-gateway.onrender.com. The service name is retained for URL compatibility. The root page provides an authenticated review form; provider API keys never leave the server. Custom GPT Actions require separate configuration using openapi.yaml and the gateway token; ordinary ChatGPT messages are not automatically routed.
