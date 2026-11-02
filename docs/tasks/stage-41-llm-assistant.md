# Stage 41: LLM and GenAI: RAG, assistant, agents

Where: `services/assistant`, `ml/llm`. Prerequisites: stages 39 and 30.

## Foundation `[CORE]`

- [ ] **S41.T01** ADR 0079: hosted LLM API vs self-hosted (vLLM / Ollama); what may leave the boundary; cost, latency, residency
  Must know: LLM deployment options

- [ ] **S41.T02** Service skeleton `services/assistant`: FastAPI, JWKS auth, per-tenant and per-user rate limits, daily token budget from entitlements, SSE streaming, request log (prompt version, model id, tokens, cost, no PII)
  Must know: SSE, rate limits, token accounting

- [ ] **S41.T03** Provider adapter port (chat, embeddings, tool calls) with two implementations and a recorded-response fake; timeouts, retries, circuit breaker, budget; prompt and response caching
  Must know: ports and adapters, caching

- [ ] **S41.T04** Tokens lab: tokens per word for Uzbek, Russian, English; context window and truncation strategy; temperature and non-determinism; cost model in `docs/notes/llm.md`
  Must know: tokenisation, context windows, sampling

- [ ] **S41.T05** PII redaction before provider calls using stage 37 pseudonymisation; restoration only inside the tenant; test that no raw phone leaves the boundary
  Must know: PII redaction

- [ ] **S41.T06** Prompt management: versioned prompt files with tests; a prompt change runs the golden set before deploy
  Must know: prompt versioning

## RAG `[CORE]`

- [ ] **S41.T07** Document ingestion through the data platform into a `documents` table: structural chunking then size with overlap, measured chunk sizes; pgvector embeddings; metadata (`tenant_id`, source, version, timestamp)
  Must know: chunking, embeddings

- [ ] **S41.T08** Tenant-safe retrieval: every query filtered by `tenant_id` and user permissions; cross-tenant leakage test suite (blocker if missing)
  Must know: fail-closed retrieval

- [ ] **S41.T09** ADR 0080 and text-to-SQL: read-only tenant-scoped views over Gold, RLS role, statement timeout, table and function allow-list, SQL shown to the user, rows cited
  Must know: text-to-SQL guardrails, RLS

- [ ] **S41.T10** Grounding controls: answers cite chunks or query rows; "I don't have that information" path tested; no numbers outside query results
  Must know: hallucination controls

- [ ] **S41.T11** Prompt-injection test set (malicious product descriptions and documents); retrieved content treated as data; output filtered before any tool runs
  Must know: prompt injection defences

## Evaluation `[CORE]`

- [ ] **S41.T12** Golden sets per capability (50–100 items) from real reports; retrieval metrics (hit rate, MRR); exact match for numbers; LLM-as-a-judge rubric for prose with one human-agreement check
  Must know: LLM evaluation

- [ ] **S41.T13** Regression gate in CI (fake provider) and nightly (real provider); cost and latency per question tracked with quality
  Must know: evaluation gates

## Agents `[CORE]`

- [ ] **S41.T14** ADR 0081 and tool definitions over the core's internal API: read tools (stock, open POs, planning suggestions, customer history within permissions) and propose-only write tools (draft PO, draft transfer, draft campaign) with service token, `Idempotency-Key`, user permissions, landing in stage 30 approvals
  Must know: tool calling, internal API commands

- [ ] **S41.T15** Agent loop with limits: max steps and tokens, per-role tool allow-list, every call logged to Audit, dry-run plan mode
  Must know: agent loops, audit logging

- [ ] **S41.T16** Structured outputs: JSON schema tool arguments validated with Pydantic; invalid call → one re-prompt then stop
  Must know: structured outputs

- [ ] **S41.T17** Agent golden set ("draft POs for products below reorder point at location X" must equal stage 29 suggestions); success rate, steps, cost
  Must know: agent evaluation

- [ ] **S41.T18** Done tests: leakage suite passes on both providers; "why did revenue drop last Tuesday?" answered with a cited query matching the stage 16 dashboard; every agent draft waits for approval; golden-set dashboard and regression block
  Must know: end-to-end evaluation

## Extensions

- [ ] **S41.T19** `[EXT]` Hybrid retrieval with re-ranking; multilingual evaluation (Uzbek Latin/Cyrillic, Russian, English); back-office chat UI (HTMX + SSE); human feedback labels and monthly worst-answer review
  Must know: re-ranking, multilingual retrieval

- [ ] **S41.T20** `[OPT]` LoRA/PEFT fine-tune of a small open model for categorisation vs few-shot prompting; Telegram bot via stage 14; MCP server exposing the same tools
  Must know: LoRA, MCP
