# Langfuse Integration Guide

In order to evaluate your AI agent, Galtea can take advantage of the rich information that comes from traces. If you already have Langfuse setup, Galtea has a very simple way of gathering those traces, in a non-intrusive way with minor changes to your application. Here we explain, how to send your Langfuse traces to Galtea.

The integration requires two things: Galtea passes an `inference_result_id` to your endpoint on every call within the header, and you forward that ID to the Galtea SDK wrapper in your code. That link is all Galtea needs to collect your traces and associate them with the right inference made for the evaluation in question.

The changes to your code are minimal: one import swap and one line to read the ID from the request header.

## What Does NOT Change in Langfuse

The Galtea integration is **transparent to Langfuse**. It does not inject trace IDs, modify attributes, or change any Langfuse behavior.

| Concern | Impact |
|---|---|
| **Trace IDs** | Langfuse generates its own trace IDs as usual. Galtea does NOT override them. |
| **Dashboard & URLs** | Your Langfuse dashboard, trace URLs, alerts, and filters are completely unaffected. |
| **Attributes & metadata** | No Galtea-specific attributes are added to Langfuse traces. |
| **Session IDs & tags** | `propagate_attributes(session_id=..., tags=...)` works exactly as before. |
| **Performance** | Negligible overhead — one attribute stamp per span at creation time. |
| **Existing code** | Functions decorated with `@observe` or using `CallbackHandler` continue to work identically in Langfuse. |

## When Does Galtea Export Data?

Galtea **only** exports trace data when an `inference_result_id` is explicitly linked. Without it, Galtea does nothing — no data is sent, no spans are modified, no logs are written.

| Scenario | Galtea exports? |
|---|---|
| Normal `@observe` call (no `inference_result_id`) | **No** |
| `@observe` called with `inference_result_id` kwarg | **Yes** |
| `CallbackHandler` with `inference_result_id` | **Yes** |
| `CallbackHandler` without `inference_result_id` | **No** |
| SDK `generate()` / `simulate()` | **Yes** (SDK manages context internally) |
| Manual `set_context(inference_result_id=...)` | **Yes** (while context is active) |

## How Your Endpoint Is Called

Galtea calls your endpoint and injects the `X-Galtea-Inference-Id` HTTP header on every request. This header carries the `inference_result_id` that links the execution to a Galtea inference result.

```
POST /your-endpoint HTTP/1.1
X-Galtea-Inference-Id: ir_abc123
Content-Type: application/json

{ "input": "Hello" }
```

Your request body is untouched — nothing is added to it. If the header is absent (non-Galtea traffic), the SDK wrapper is a no-op: no data is sent, nothing breaks.

> **Note:** Galtea uses inference results as the unit of evaluation — each one represents a single input/output pair that can be scored by metrics. By linking traces to an inference result, Galtea knows which execution traces belong to which response, enabling trace-aware evaluations and hence full visibility into how your agent arrived at each answer.

## What You Change in Your Code

### Step 1: Install and initialize the Galtea client

```
pip install galtea
```

The `[langfuse]` extra (`pip install 'galtea[langfuse]'`) is only needed if you don't already have `langfuse` installed — it simply adds `langfuse` as a dependency. Since you already have Langfuse installed, `pip install galtea` is enough. If you use the LangChain `CallbackHandler`, install with `pip install 'galtea[langfuse-langchain]'` to include `langchain` as well.

```python
import galtea

client = galtea.Galtea(api_key="gsk_...")
```

Initialization order with Langfuse doesn't matter — both libraries detect each other automatically.

### Step 2: Read the header and swap the import

Two changes: swap the Langfuse import for the Galtea wrapper and pass the ID; reading the header is just where the ID comes from. The wrapper handles everything else.

**@observe (decorator)**

```python
# Before:
from langfuse import observe

@observe(name="my-agent")
def my_agent(user_input: str) -> str:
    context = retrieve(user_input)
    return generate(user_input, context)

result = my_agent("Hello")

# After:
from galtea.integrations.langfuse import observe  # swap import

@observe(name="my-agent")
def my_agent(user_input: str) -> str:
    context = retrieve(user_input)
    return generate(user_input, context)

inference_result_id = request.headers.get("X-Galtea-Inference-Id")  # read header
result = my_agent("Hello", inference_result_id=inference_result_id)  # pass the ID
```

The `inference_result_id` kwarg is consumed by the wrapper — it does not reach your function's parameters. The wrapper sets up the Galtea trace context before the function runs and flushes it when it returns.

**start_as_current_observation (context manager)**

Only the **root** call needs the Galtea wrapper. Child observations on yielded spans stay native Langfuse — no change needed there.

```python
# Before:
from langfuse import get_client
langfuse = get_client()

with langfuse.start_as_current_observation(name="my-op", as_type="span") as root:
    with root.start_as_current_observation(name="child", as_type="generation") as gen:
        gen.update(output=result)

# After:
from galtea.integrations.langfuse import start_as_current_observation  # swap import

inference_result_id = request.headers.get("X-Galtea-Inference-Id")  # read header

with start_as_current_observation(
    name="my-op",
    as_type="span",
    inference_result_id=inference_result_id,  # pass the ID at the root
) as root:
    with root.start_as_current_observation(name="child", as_type="generation") as gen:  # unchanged
        gen.update(output=result)
```

The `langfuse.` client prefix is no longer needed for the root call — the wrapper calls `get_client()` internally. But keeping the client does not introduce any issues, since it is singleton and refers to the same object.

**CallbackHandler (LangChain)**

Swap the import and call `set_inference_result_id` before each invocation. Your existing handler initialization stays the same:

```python
# Before:
from langfuse.langchain import CallbackHandler

handler = CallbackHandler()  # at app init

# Per request:
result = chain.invoke({"input": "Hello"}, config={"callbacks": [handler]})

# After:
from galtea.integrations.langfuse import CallbackHandler  # swap import

handler = CallbackHandler()  # at app init (unchanged)

# Per request:
inference_result_id = request.headers.get("X-Galtea-Inference-Id")  # read header
handler.set_inference_result_id(inference_result_id)  # set ID for this request
result = chain.invoke({"input": "Hello"}, config={"callbacks": [handler]})
# Context is automatically cleared when the chain finishes.
```

Alternatively, you can create a handler per request with the ID in the constructor:

```python
inference_result_id = request.headers.get("X-Galtea-Inference-Id")
handler = CallbackHandler(inference_result_id=inference_result_id)
result = chain.invoke({"input": "Hello"}, config={"callbacks": [handler]})
```

> **Note:** When using Galtea's SDK methods (`generate()`, `simulate()`), this step is not needed — the SDK manages `inference_result_id` internally.

### What You Do NOT Need to Change

- `span.update(output=...)`, `span.score(...)` — native Langfuse span methods
- `root.start_as_current_observation(...)` — child observations on yielded spans
- `propagate_attributes(user_id=..., session_id=..., tags=...)` — pure Langfuse, no wrapper needed
- Any Langfuse dashboard configuration, alerts, or integrations

## Version Compatibility

Requires **Langfuse v3.0.0 or later** (capped at `<5.0.0`). v2.x is not supported — it does not use OTel internally.

## FAQ

**Q: Will adding Galtea slow down my Langfuse traces?**

No. Galtea only batches and exports spans when `inference_result_id` is set — otherwise it's a no-op.

**Q: Can I remove Galtea later without affecting Langfuse?**

Yes. Swap the imports back (`from langfuse import observe`) and remove the `galtea.Galtea(api_key=...)` initialization. Langfuse continues working exactly as before.

**Q: Does Galtea see my Langfuse API keys?**

No. Galtea only receives trace data (name, type, input, output, timing, hierarchy). It does not access your Langfuse credentials or cloud configuration.

**Q: What if Langfuse adds new observation types?**

Unknown types are automatically mapped to `SPAN` in Galtea. Your traces are never dropped.
