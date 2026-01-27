"""
SDK API: Trace Examples
Demonstrates trace decorator, start_trace, and context management patterns.
These examples are referenced from the trace documentation pages.
"""

from datetime import datetime

from galtea import (
    Agent,
    AgentInput,
    AgentResponse,
    Galtea,
    TraceType,
    clear_context,
    set_context,
    start_trace,
    trace,
)

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Trace Examples Demo " + run_identifier,
        "description": "Demo product for trace API examples",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for trace examples",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")


# =============================================================================
# TRACE SERVICE OVERVIEW EXAMPLE
# Demonstrates @trace decorator usage with set_context/clear_context
# =============================================================================


# @start trace_overview
@trace(type=TraceType.TOOL)
def fetch_user_data(user_id: str) -> dict:
    return {"name": "John Doe", "email": "john@example.com"}


@trace(type=TraceType.GENERATION)
def generate_response(prompt: str) -> str:
    return "Generated response..."


class MyOverviewAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        user = fetch_user_data("user_123")
        response = generate_response("Hello")
        return AgentResponse(content=response)


# Use generate() for automatic trace context management
inference_result = galtea.inference_results.generate(
    agent=MyOverviewAgent(),
    session=session,
    user_input="Show me user data",
)
# @end trace_overview


# =============================================================================
# START_TRACE EXAMPLES
# Demonstrates start_trace() context manager for fine-grained control
# =============================================================================

# Create a new session for start_trace examples
session_start_trace = galtea.sessions.create(version_id=version_id, is_production=True)
if session_start_trace is None:
    raise ValueError("session_start_trace is None")


# @start start_trace_rag_pipeline
def rag_pipeline(query: str, inference_result_id: str) -> str:
    token = set_context(inference_result_id=inference_result_id)

    try:
        # Retrieval step
        with start_trace(
            "retrieve_documents",
            type="RETRIEVER",
            description="Searches vector store for relevant documents",
            input={"query": query},
        ) as span:
            # Simulated vector store search
            docs = [
                {"id": "doc1", "content": "Paris is the capital of France."},
                {"id": "doc2", "content": "France is in Western Europe."},
            ]
            span.update(output={"doc_count": len(docs), "docs": docs})

        # Generation step
        with start_trace(
            "generate_response",
            type="GENERATION",
            description="Generates final response using retrieved context",
            input={"query": query},
        ) as span:
            # Simulated LLM response
            response_content = "Based on the documents, Paris is the capital of France."
            span.update(
                output={"response": response_content},
                metadata={"tokens_used": 42, "model": "gpt-4"},
            )

        return response_content
    finally:
        clear_context(token)


# Create an inference result to associate traces with
inference_result_for_rag = galtea.inference_results.create(
    session_id=session_start_trace.id,
    input="What is the capital of France?",
)
if inference_result_for_rag is None:
    raise ValueError("inference_result_for_rag is None")

result = rag_pipeline("What is the capital of France?", inference_result_for_rag.id)
# @end start_trace_rag_pipeline


# @start start_trace_nested
def process_with_nested_traces(inference_result_id: str) -> dict:
    token = set_context(inference_result_id=inference_result_id)

    try:
        with start_trace(
            "parent_operation", type="CHAIN", input={"task": "process_all"}
        ) as parent:
            # First child
            with start_trace("child_step_1", type="TOOL") as span:
                step1_result = {"processed": True, "items": 5}
                span.update(output=step1_result)

            # Second child
            with start_trace("child_step_2", type="TOOL") as span:
                step2_result = {"validated": True, "errors": 0}
                span.update(output=step2_result)

            parent.update(output={"total_steps": 2, "status": "completed"})

        return {"step1": step1_result, "step2": step2_result}
    finally:
        clear_context(token)


# Create another inference result for nested trace example
inference_result_for_nested = galtea.inference_results.create(
    session_id=session_start_trace.id,
    input="Process all items",
)
if inference_result_for_nested is None:
    raise ValueError("inference_result_for_nested is None")

nested_result = process_with_nested_traces(inference_result_for_nested.id)
# @end start_trace_nested


# =============================================================================
# TRACE DECORATOR FEATURE EXAMPLES
# Demonstrates various @trace decorator features
# =============================================================================

# Create a new session for decorator examples
session_decorator = galtea.sessions.create(version_id=version_id, is_production=True)
if session_decorator is None:
    raise ValueError("session_decorator is None")


# @start trace_decorator_exception
@trace(type=TraceType.TOOL)
def risky_operation() -> str:
    # Exceptions are always recorded in traces for debugging
    # even with log_args=False and log_results=False
    return "Success"


class RiskyAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        result = risky_operation()
        return AgentResponse(content=result)


# The trace will include error details if an exception occurs
inference_result_risky = galtea.inference_results.generate(
    agent=RiskyAgent(),
    session=session_decorator,
    user_input="test",
)
# @end trace_decorator_exception


# @start trace_decorator_serialization
@trace(type=TraceType.TOOL)
def process_data(user_id: str, config: dict) -> dict:
    # Function arguments are automatically serialized to JSON
    # Non-serializable objects are converted to string representation
    return {"status": "processed", "user_id": user_id}


class DataAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        result = process_data("user_123", {"setting": "value"})
        return AgentResponse(content=str(result))


session_serialization = galtea.sessions.create(
    version_id=version_id, is_production=True
)
if session_serialization is None:
    raise ValueError("session_serialization is None")

inference_result_data = galtea.inference_results.generate(
    agent=DataAgent(),
    session=session_serialization,
    user_input="process",
)
# @end trace_decorator_serialization


# @start trace_decorator_context_propagation
@trace(type=TraceType.AGENT)
def agent_workflow() -> str:
    # This trace is automatically linked to the inference result
    # when set_context() has been called with inference_result_id
    return "workflow completed"


# Create an inference result for context propagation example
session_context = galtea.sessions.create(version_id=version_id, is_production=True)
if session_context is None:
    raise ValueError("session_context is None")

inference_result_context = galtea.inference_results.create(
    session_id=session_context.id,
    input="Run workflow",
)
if inference_result_context is None:
    raise ValueError("inference_result_context is None")

# Set context before running traced functions
token = set_context(inference_result_id=inference_result_context.id)

try:
    result = agent_workflow()
finally:
    clear_context(token)
# @end trace_decorator_context_propagation


# =============================================================================
# CLEANUP
# =============================================================================

galtea.products.delete(product_id=product_id)
