# Langfuse CallbackHandler Integration Guide

If you use Langfuse's `CallbackHandler` for LangChain tracing, this guide explains how to send those same traces to Galtea with minimal changes to your code.

## What Does NOT Change

The Galtea integration is **transparent to Langfuse**. It does not inject trace IDs, modify attributes, or change any Langfuse behavior.

| Concern | Impact |
|---|---|
| **Trace IDs** | Langfuse generates its own trace IDs as usual. Galtea does NOT override them. |
| **Dashboard & URLs** | Your Langfuse dashboard, trace URLs, alerts, and filters are completely unaffected. |
| **CallbackHandler behavior** | All LangChain callback methods work identically — chains, LLMs, tools, retrievers. |
| **Handler lifecycle** | You can keep your existing initialization pattern (singleton or per-request). |
| **Performance** | Negligible overhead — one attribute stamp per span at creation time. |

## When Does Galtea Export Data?

Galtea **only** exports trace data when an `inference_result_id` is linked. Without it, Galtea does nothing — no data is sent, no spans are modified.

| Scenario | Galtea exports? |
|---|---|
| `CallbackHandler` without `inference_result_id` | **No** |
| `CallbackHandler` with `inference_result_id` (constructor or `set_inference_result_id`) | **Yes** |
| SDK `generate()` / `simulate()` | **Yes** (SDK manages context internally) |

## How Your Endpoint Is Called

Galtea calls your endpoint and injects the `X-Galtea-Inference-Id` HTTP header on every request. This header carries the `inference_result_id` that links the execution to a Galtea inference result.

```
POST /your-endpoint HTTP/1.1
X-Galtea-Inference-Id: ir_abc123
Content-Type: application/json

{ "input": "Hello" }
```

Your request body is untouched. If the header is absent (non-Galtea traffic), the wrapper is a no-op: no data is sent, nothing breaks.

## What You Change in Your Code

### Step 1: Install and initialize the Galtea client

```bash
pip install 'galtea[langfuse-langchain]'
```

This installs `galtea` with both `langfuse` and `langchain` as version-compatible dependencies. If you already have both installed, `pip install galtea` is enough.

```python
import galtea

client = galtea.Galtea(api_key="gsk_...")
```

Initialization order with Langfuse doesn't matter — both libraries detect each other automatically.

### Step 2: Swap the import and pass the inference result ID

One import change and one line to read the header. Your existing handler initialization stays the same.

```python
# Before:
from langfuse import get_client
from langfuse.langchain import CallbackHandler

langfuse = get_client()
langfuse_handler = CallbackHandler()

# Per request — call your agent:
result = chain.invoke({"input": "Hello"}, config={"callbacks": [langfuse_handler]})


# After:
from langfuse import get_client
from galtea.integrations.langfuse import CallbackHandler  # swap this import

langfuse = get_client()
langfuse_handler = CallbackHandler()  # unchanged

# Per request — read the header, set the ID and call your agent:
inference_result_id = request.headers.get("X-Galtea-Inference-Id")
langfuse_handler.set_inference_result_id(inference_result_id)
result = chain.invoke({"input": "Hello"}, config={"callbacks": [langfuse_handler]})
# Context is automatically cleared when the chain finishes.
```

That's it. Three lines changed: the import, reading the header, and one `set_inference_result_id` call per request.

### How it works under the hood

The Galtea `CallbackHandler` wraps the Langfuse `CallbackHandler` and automatically manages trace context around LangChain callback lifecycles:

1. On the first `on_*_start` callback (chain, LLM, tool, etc.), Galtea calls `set_context(inference_result_id)`.
2. Nested callbacks (tool calls, LLM calls inside a chain) are tracked via a depth counter — context stays active.
3. On the last `on_*_end` or `on_*_error` callback, Galtea calls `clear_context()` and flushes traces to the Galtea API.

No context managers or manual cleanup needed.

### Alternative: per-request handler

If you prefer to create a new handler per request instead of reusing a singleton, you can pass the ID directly in the constructor:

```python
from galtea.integrations.langfuse import CallbackHandler

# Per request:
inference_result_id = request.headers.get("X-Galtea-Inference-Id")
handler = CallbackHandler(inference_result_id=inference_result_id)
result = chain.invoke({"input": "Hello"}, config={"callbacks": [handler]})
```

### What You Do NOT Need to Change

- `get_client()` — your Langfuse client initialization
- `chain.invoke()`, `chain.batch()`, `chain.stream()` — LangChain invocation calls
- `config={"callbacks": [handler]}` — how you pass the handler to LangChain
- `propagate_attributes(user_id=..., session_id=..., tags=...)` — pure Langfuse, no wrapper needed
- Any Langfuse dashboard configuration, alerts, or integrations

## Version Compatibility

- **Langfuse**: v3.0.0 or later (capped at `<5.0.0`). v2.x is not supported — it does not use OTel internally.
- **LangChain**: v0.1.0 or later (capped at `<2.0.0`). The exact minimum depends on your Langfuse version — Langfuse v3.8+ and v4 require LangChain v1.0+.

## FAQ

**Q: Will adding Galtea slow down my LangChain chains?**

No. Galtea only batches and exports spans when `inference_result_id` is set — otherwise it's a no-op.

**Q: Can I remove Galtea later without affecting Langfuse?**

Yes. Swap the import back (`from langfuse.langchain import CallbackHandler`), remove the `set_inference_result_id` call, and remove the `galtea.Galtea(api_key=...)` initialization. Langfuse continues working exactly as before.

**Q: Is the CallbackHandler thread-safe?**

Langfuse's underlying `CallbackHandler` is not thread-safe — it stores per-run state in shared mutable dicts without locks. If your web server handles concurrent requests on multiple threads, create a new `CallbackHandler` per request instead of reusing a singleton.

**Q: Can I mix CallbackHandler with @observe?**

Yes. All three Galtea wrappers (`@observe`, `start_as_current_observation`, `CallbackHandler`) can be used together. For example, an `@observe`-decorated function can pass a `CallbackHandler` to LangChain inside it — the parent-child trace hierarchy is preserved automatically.
