# Examples

Minimal agent scaffolds used by AgentFailBench. Prefer one custom tool-calling
loop first; add LangGraph / AutoGen / etc. later without coupling the benchmark
core to a single framework.

| Directory | Purpose |
|---|---|
| `api_agent/` | REST API customer-support style tasks |
| `database_agent/` | SQL investigation tasks |
| `retrieval_agent/` | Document retrieval and synthesis |
| `physical_simulation/` | Small Phase-two transfer environment |
