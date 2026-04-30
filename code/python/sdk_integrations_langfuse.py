"""
SDK Integrations: Langfuse — display-only code snippets.

This file provides code examples for the Langfuse integration docs page.
It is NOT executed by validate_snippets.py because it requires the langfuse
optional dependency which is not installed in the docs CI environment.

Validation: syntax-checked only (compile(), not exec()).
"""

# -- Gate: skip execution when langfuse is not installed (CI) ----------------
# validate_snippets.py exec()s every file and maps EnvironmentError with
# "Missing required environment variable" to a clean SKIPPED status.
import importlib.util

if importlib.util.find_spec("langfuse") is None:
    raise EnvironmentError(
        "Missing required environment variable: LANGFUSE"
        " (optional dependency — install with: pip install 'galtea[langfuse]')"
    )

# -- Module-level stubs (not embedded; only here so Pylance is happy in
# sections that reference async retrieval/generation as if they exist) ------


async def retrieve_async(query: str) -> list[str]:
    return ["doc1", "doc2"]


async def generate_async(query: str, context: list[str]) -> str:
    return "response"


# -- Below: sections extracted by @embed in the MDX page --------------------

from galtea import Galtea

# @start initialize
import galtea

client = galtea.Galtea(api_key="YOUR_API_KEY")
# @end initialize

# @start instrument
# Before:
# from langfuse import observe

# After:
from galtea.integrations.langfuse import observe
# @end instrument

# @start agent_definition
from galtea.integrations.langfuse import observe


@observe(name="retrieve")
def retrieve(query: str) -> list[str]:
    # Your retrieval logic (vector DB, search, etc.)
    return ["relevant document 1", "relevant document 2"]


@observe(name="generate")
def generate(query: str, context: list[str]) -> str:
    # Your LLM call
    return "Generated response based on context"


@observe(name="my-agent")
def my_agent(user_input: str) -> str:
    context = retrieve(user_input)
    return generate(user_input, context)
# @end agent_definition

# @start option_a_kwarg
# The wrapper handles set_context/clear_context automatically:
result = my_agent("What is gestational diabetes?", inference_result_id="inferenceResult_abc123")
# @end option_a_kwarg

# @start option_b_manual
from galtea.utils.tracing import clear_context, set_context

token = set_context(inference_result_id="inferenceResult_abc123")
try:
    result = my_agent("What is gestational diabetes?")
finally:
    clear_context(token)
# @end option_b_manual

# @start sdk_methods
# With generate() — zero extra lines, SDK manages context internally:
result = client.inference_results.generate(agent=my_agent, session=session)

# With simulate() — same, each turn gets its own IR and traces:
result = client.simulator.simulate(session_id=session.id, agent=my_agent)
# @end sdk_methods

# @start observation_types
from galtea.integrations.langfuse import observe


@observe(name="my-retriever", as_type="retriever")
def search_docs(query: str) -> list[str]:
    return ["doc1", "doc2"]


@observe(name="my-llm-call", as_type="generation")
def call_llm(prompt: str) -> str:
    return "LLM response"


@observe(name="my-tool", as_type="tool")
def call_api(endpoint: str) -> dict:
    return {"status": "ok"}


@observe(name="my-agent", as_type="agent")
def agent(user_input: str) -> str:
    docs = search_docs(user_input)
    api_result = call_api("/check")
    return call_llm(f"Context: {docs}, API: {api_result}, Question: {user_input}")
# @end observation_types


# -- API reference sections ------------------------------------------------

# @start service_imports
from galtea.integrations.langfuse import CallbackHandler
from galtea.integrations.langfuse import observe
from galtea.integrations.langfuse import start_as_current_observation
# @end service_imports

# @start api_observe_example
from galtea.integrations.langfuse import observe


@observe(name="my-agent", as_type="agent")
def run_agent(user_input: str) -> str:
    context = retrieve(user_input)
    return generate(user_input, context)


# Without Galtea correlation (traces go to Langfuse only):
result = run_agent("What is gestational diabetes?")

# With Galtea correlation (traces go to both Langfuse and Galtea):
result = run_agent("What is gestational diabetes?", inference_result_id="inferenceResult_abc123")
# @end api_observe_example

# @start observe_async_example
import asyncio

from galtea.integrations.langfuse import observe


@observe(name="my-async-agent", as_type="agent")
async def run_async_agent(user_input: str) -> str:
    # Awaitable retrieval and generation steps inside the agent.
    context = await retrieve_async(user_input)
    return await generate_async(user_input, context)


# `@observe` detects the wrapped function is `async def` and returns an async
# wrapper that awaits the coroutine before clearing context. Call it like any
# other coroutine:
result = asyncio.run(
    run_async_agent("What is gestational diabetes?", inference_result_id="inferenceResult_abc123")
)
# @end observe_async_example

# @start api_start_observation_example
from galtea.integrations.langfuse import start_as_current_observation

# Without Galtea correlation:
with start_as_current_observation(name="process-query", as_type="span") as span:
    result = run_agent("user query")
    span.update(output=result)

# With Galtea correlation:
with start_as_current_observation(
    name="process-query",
    as_type="span",
    inference_result_id="inferenceResult_abc123",
) as span:
    result = run_agent("user query")
    span.update(output=result)
# @end api_start_observation_example

# @start api_start_observation_nested
from galtea.integrations.langfuse import start_as_current_observation

# Only the root call needs the Galtea wrapper.
# Child calls on yielded spans are native Langfuse.
with start_as_current_observation(
    name="pipeline",
    as_type="span",
    inference_result_id="inferenceResult_abc123",
) as root:
    with root.start_as_current_observation(name="retrieve", as_type="retriever") as ret:
        docs = ["doc1", "doc2"]
        ret.update(output=docs)

    with root.start_as_current_observation(name="generate", as_type="generation") as gen:
        response = "Generated response"
        gen.update(output=response, model="gpt-4")

    root.update(output=response)
# @end api_start_observation_nested

# @start context_manager_api
from galtea.integrations.langfuse import start_as_current_observation

# Create spans using context managers instead of decorators
with start_as_current_observation(
    name="process-query",
    as_type="span",
    inference_result_id="inferenceResult_abc123",
) as root_span:
    # All child spans (decorator or context manager) are children of root_span
    docs = search_docs("user query")

    with start_as_current_observation(name="generate-response", as_type="generation") as gen:
        response = "Generated response"
        gen.update(output=response, model="gpt-4")

    root_span.update(output=response)
# @end context_manager_api


# -- CallbackHandler sections ------------------------------------------------

# @start callback_handler_import
# Before:
# from langfuse.langchain import CallbackHandler

# After:
from galtea.integrations.langfuse import CallbackHandler
# @end callback_handler_import

# @start callback_handler_usage
from galtea.integrations.langfuse import CallbackHandler

# Without Galtea correlation (pure Langfuse passthrough):
handler = CallbackHandler()

# With Galtea correlation (traces go to both Langfuse and Galtea):
handler = CallbackHandler(inference_result_id="inferenceResult_abc123")
# @end callback_handler_usage

# @start callback_handler_full_example
from langfuse import get_client

from galtea import Galtea
from galtea.integrations.langfuse import CallbackHandler

# Initialize both — order doesn't matter
galtea_client = Galtea(api_key="YOUR_API_KEY")
langfuse = get_client()

# Create handler with Galtea correlation
handler = CallbackHandler(inference_result_id="inferenceResult_abc123")

# Use with any LangChain chain, agent, or LLM
# chain.invoke({"input": "What is gestational diabetes?"}, config={"callbacks": [handler]})
# @end callback_handler_full_example

# @start callback_handler_singleton
from galtea.integrations.langfuse import CallbackHandler

handler = CallbackHandler()  # at app init — no inference_result_id yet

# Per request:
handler.set_inference_result_id("inferenceResult_abc123")
# chain.invoke({"input": "query"}, config={"callbacks": [handler]})
# Context is automatically cleared when the chain finishes.
# @end callback_handler_singleton

# @start api_callback_handler_example
from galtea.integrations.langfuse import CallbackHandler

# Without Galtea correlation (traces go to Langfuse only):
handler = CallbackHandler()
# chain.invoke({"input": "query"}, config={"callbacks": [handler]})

# With Galtea correlation (traces go to both Langfuse and Galtea):
handler = CallbackHandler(inference_result_id="inferenceResult_abc123")
# chain.invoke({"input": "query"}, config={"callbacks": [handler]})
# @end api_callback_handler_example
