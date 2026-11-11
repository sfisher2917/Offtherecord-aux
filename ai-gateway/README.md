# Secure three-model gateway (DRAFT — DO NOT DEPLOY YET)
Cloudflare Workers Free plan only. Never enable on a paid plan or billing-linked model account.
This gateway sends a non-confidential 1–1000-character prompt in parallel to Groq, Gemini and OpenRouter, then returns three independent results. ChatGPT performs the final synthesis; the gateway does not itself produce a consensus.
## Security
Requires a long random GATEWAY_TOKEN using Authorization: Bearer; secrets remain in Cloudflare Worker secrets. ENABLED and ZERO_COST_VERIFIED must both equal 'true'; unset by default. No GitHub Actions, trading, repository write access or auto-merge. No paid fallback. Requests are rejected if any provider key is absent. HTTP failures return no paid retry. Logs should not contain prompts or provider keys.
## Deployment checklist
1. Verify Cloudflare account is on Workers Free, not Paid; verify Gemini, Groq and OpenRouter projects have no paid billing, and free model availability. Verify free quotas and terms. Provider-side account restrictions cannot be checked by this code.
2. In Cloudflare Workers, create a new Worker, paste worker.js and deploy only on Workers Free.
3. Configure encrypted secrets GATEWAY_TOKEN, GROQ_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY. Never commit credentials.
4. Set text variables ENABLED=true and ZERO_COST_VERIFIED=true only after checks; otherwise endpoint fails closed.
5. Copy openapi.yaml into a private GPT Action, replace the server URL, choose API Key authentication with Bearer and enter GATEWAY_TOKEN.
6. Add GPT instructions: Ask permission before sharing prompts with third parties; invoke reviewWithThreeModels for eligible non-sensitive questions; verify outputs and report disagreements; if disabled or any provider fails, clearly disclose it and answer using ChatGPT rather than pretending consensus.
7. Test with a harmless prompt and inspect status codes. Do not paste private documents, API keys, financial or medical information into the prompt.
## Important
A Custom GPT cannot intercept all ordinary ChatGPT conversations. Custom GPT retirement/migration to Plugins has been announced; consider a plugin implementation before relying on this long-term.
Cloudflare free quotas are not the same as a guaranteed $0 bill. No system can independently guarantee provider billing account status. Do not enable until verified.
