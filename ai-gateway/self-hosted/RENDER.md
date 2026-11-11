# Render Free deployment — Cloudflare-free
Source: `ai-gateway/self-hosted/`. Render supplies managed HTTPS, but the Node.js gateway and AI orchestration remain ours.
## Deployment
1. Connect the GitHub repository to a Render account **without a payment method**. Verify that the account is on the Free plan and no paid services or overage billing are enabled.
2. Use Render's Blueprint feature with the repository's root `render.yaml` (after the PR is approved and merged). Confirm the web service shows **Free** and auto-deploy is disabled.
3. Enter GATEWAY_TOKEN, GROQ_API_KEY and OPENROUTER_API_KEY as private environment variables in Render. Never paste them into GitHub source or chat.
4. Leave ENABLED=false and ZERO_COST_VERIFIED=false until provider free-tier eligibility, billing controls, and usage limits have been verified.
5. Visit `https://<your-service>.onrender.com/health` and verify a 200 JSON response. The service must refuse `/review` requests while disabled.
6. Once all safeguards are verified, explicitly authorize activation, set both flags to true, and test `/review` with a non-sensitive prompt. Ensure both providers respond successfully.
7. Replace the placeholder HTTPS server URL in `ai-gateway/self-hosted/openapi.yaml` with the verified live URL, then configure a dedicated Custom GPT Action with the bearer token. Ordinary ChatGPT conversations are not automatically connected.
## Caveats
Render Free sleeps after 15 minutes of inactivity and can cold-start slowly, potentially exceeding ChatGPT Action timeouts. Free compute has 750 hours/workspace/month, but bandwidth/build minutes also have allowances. Without a payment method, Render says it suspends free services/builds instead of charging for overages. Provider API free-tier limits must be verified separately. Process request caps reset when a container restarts and are not reliable billing caps.
Do not expose private company documents, employee data, financial information, or secrets to all two AI providers.
