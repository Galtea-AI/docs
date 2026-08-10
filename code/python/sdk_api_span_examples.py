"""
SDK API: Span Examples
Demonstrates traced decorator, start_span, and context management patterns.
These examples are referenced from the span documentation pages.
"""

from datetime import datetime

from galtea import (
    AgentInput,
    AgentResponse,
    Galtea,
    SpanType,
    clear_context,
    set_context,
    start_span,
    traced,
)

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(galtea, name="Span Examples Demo " + run_identifier)

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for span examples",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")


# =============================================================================
# SPAN SERVICE OVERVIEW EXAMPLE
# Demonstrates @traced decorator usage with set_context/clear_context
# =============================================================================


# @start span_overview
@traced(type=SpanType.TOOL)
def fetch_user_data(user_id: str) -> dict:
    return {"name": "John Doe", "email": "john@example.com"}


@traced(type=SpanType.GENERATION)
def generate_response(prompt: str) -> str:
    return "Generated response..."


def my_overview_agent(input_data: AgentInput) -> AgentResponse:
    user = fetch_user_data("user_123")
    response = generate_response("Hello")
    return AgentResponse(content=response)


# Use generate() for automatic span context management
inference_result = galtea.inference_results.generate(
    agent=my_overview_agent,
    session=session,
    input="Show me user data",
)
# @end span_overview


# =============================================================================
# START_SPAN EXAMPLES
# Demonstrates start_span() context manager for fine-grained control
# =============================================================================

# Create a new session for start_span examples
session_start_span = galtea.sessions.create(version_id=version_id, is_production=True)
if session_start_span is None:
    raise ValueError("session_start_span is None")


# @start start_span_rag_pipeline
def rag_pipeline(query: str, inference_result_id: str) -> str:
    token = set_context(inference_result_id=inference_result_id)

    try:
        # Retrieval step
        with start_span(
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
        with start_span(
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


# Create an inference result to associate spans with
inference_result_for_rag = galtea.inference_results.create(
    session_id=session_start_span.id,
    input="What is the capital of France?",
)
if inference_result_for_rag is None:
    raise ValueError("inference_result_for_rag is None")

result = rag_pipeline("What is the capital of France?", inference_result_for_rag.id)
# @end start_span_rag_pipeline


# @start start_span_nested
def process_with_nested_spans(inference_result_id: str) -> dict:
    token = set_context(inference_result_id=inference_result_id)

    try:
        with start_span("parent_operation", type="CHAIN", input={"task": "process_all"}) as parent:
            # First child
            with start_span("child_step_1", type="TOOL") as span:
                step1_result = {"processed": True, "items": 5}
                span.update(output=step1_result)

            # Second child
            with start_span("child_step_2", type="TOOL") as span:
                step2_result = {"validated": True, "errors": 0}
                span.update(output=step2_result)

            parent.update(output={"total_steps": 2, "status": "completed"})

        return {"step1": step1_result, "step2": step2_result}
    finally:
        clear_context(token)


# Create another inference result for nested span example
inference_result_for_nested = galtea.inference_results.create(
    session_id=session_start_span.id,
    input="Process all items",
)
if inference_result_for_nested is None:
    raise ValueError("inference_result_for_nested is None")

nested_result = process_with_nested_spans(inference_result_for_nested.id)
# @end start_span_nested


# =============================================================================
# SPAN DECORATOR FEATURE EXAMPLES
# Demonstrates various @traced decorator features
# =============================================================================

# Create a new session for decorator examples
session_decorator = galtea.sessions.create(version_id=version_id, is_production=True)
if session_decorator is None:
    raise ValueError("session_decorator is None")


# @start span_decorator_exception
@traced(type=SpanType.TOOL)
def risky_operation() -> str:
    # Exceptions are always recorded in spans for debugging
    # even with log_args=False and log_results=False
    return "Success"


def risky_agent(input_data: AgentInput) -> AgentResponse:
    result = risky_operation()
    return AgentResponse(content=result)


# The span will include error details if an exception occurs
inference_result_risky = galtea.inference_results.generate(
    agent=risky_agent,
    session=session_decorator,
    input="test",
)
# @end span_decorator_exception


# @start span_decorator_serialization
@traced(type=SpanType.TOOL)
def process_data(user_id: str, config: dict) -> dict:
    # Function arguments are automatically serialized to JSON
    # Non-serializable objects are converted to string representation
    return {"status": "processed", "user_id": user_id}


def data_agent(input_data: AgentInput) -> AgentResponse:
    result = process_data("user_123", {"setting": "value"})
    return AgentResponse(content=str(result))


session_serialization = galtea.sessions.create(version_id=version_id, is_production=True)
if session_serialization is None:
    raise ValueError("session_serialization is None")

inference_result_data = galtea.inference_results.generate(
    agent=data_agent,
    session=session_serialization,
    input="process",
)
# @end span_decorator_serialization


# @start span_decorator_context_propagation
@traced(type=SpanType.AGENT)
def agent_workflow() -> str:
    # This span is automatically linked to the inference result
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
# @end span_decorator_context_propagation


# =============================================================================
# CLEANUP
# =============================================================================

galtea.products.delete(product_id=product_id)
