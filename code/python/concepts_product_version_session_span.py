from datetime import datetime

from _test_helpers import create_test_product

# @start the_decorator_syntax_options
from galtea import Galtea, SpanType, traced


# Full specification
@traced(name="my_operation", type=SpanType.TOOL)
def my_function_1():
    # Function implementation ...
    print("Doing something...")


# Name only (type defaults to SPAN)
@traced(name="custom_name")
def my_function_2():
    # Function implementation ...
    print("Doing something else...")


# Include function docstring as span description
@traced(type=SpanType.TOOL, include_docstring=True)
def my_function_3(user_id: str):
    """Fetch user data from the database given a user ID."""
    # Function implementation ...
    print(f"Fetching data for user {user_id}...")


# Bare decorator (uses function name)
@traced()
def my_function_4():
    # Function implementation ...
    print("Doing another thing...")


# @end the_decorator_syntax_options


# @start the_decorator_error_tracking
@traced(name="risky_operation", type=SpanType.TOOL)
def risky_call(self, data: str) -> str:
    if not data:
        raise ValueError("Data cannot be empty")
    return f"Processed: {data}"


# @end the_decorator_error_tracking


run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")
galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(galtea, name="Span Concepts Demo " + run_identifier)

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for span concepts",
)
if version is None:
    raise ValueError("version is None")

session = galtea.sessions.create(version.id, is_production=True)
if session is None:
    raise ValueError("session is None")

from galtea import AgentInput, AgentResponse, Galtea, SpanType  # noqa: E402


# Empty parentheses
@traced(name="Function that calls another traced function")
def my_function_nested():
    print("Calling another function...")
    my_function_1()


def my_galtea_agent(input_data: AgentInput) -> AgentResponse:
    user_message = input_data.last_user_message_str()
    response = f"Hello! You said: {user_message}"
    my_function_1()
    my_function_nested()
    my_function_2()
    my_function_3(user_id="12345")
    my_function_4()
    return AgentResponse(content=response)


inference_result = galtea.inference_results.generate(
    my_galtea_agent,
    session,
    "User input",
)

# @start the_decorator_viewing_span_hierarchy
spans = galtea.spans.list(inference_result_id=inference_result.id)

print("Span Hierarchy:")


def print_span_tree(spans, parent_id=None, indent=0):
    for span in spans:
        if span.parent_trace_id == parent_id:
            prefix = "  " * indent + ("└─ " if indent > 0 else "")
            print(f"{prefix}{span.name} ({span.type}) - {span.latency_ms:.2f}ms")
            print_span_tree(spans, span.id, indent + 1)


print_span_tree(spans)
# @end the_decorator_viewing_span_hierarchy


# @start naming_tips
# ✅ Good - descriptive
@traced(name="fetch_customer_orders")
# ❌ Bad - generic
@traced(name="step_1")
# @end naming_tips


# @start span_at_meaningful_boundaries
# ✅ Good - meaningful operation
@traced(name="search_products", type=SpanType.RETRIEVER)
def search_products(self, query):
    results = self._query_vector_db(query)  # Internal, not traced
    return self._format_results(results)  # Internal, not traced


# @end span_at_meaningful_boundaries


# @start select_appropriate_node_types
# ✅ Good - correct classification
@traced(name="generate_evaluation_metrics", type=SpanType.RETRIEVER)
def fetch_user_data(self, user_id: str) -> dict:
    # Function implementation ...
    return {"user_id": user_id, "data": "Sample data"}


# ❌ Bad - incorrect classification
@traced(name="generate_evaluation_metrics", type=SpanType.TOOL)
def fetch_user_data_incorrect(self, user_id: str) -> dict:
    # Function implementation ...
    return {"user_id": user_id, "data": "Sample data"}


# @end select_appropriate_node_types


# @start keep_input_output_data_reasonable
@traced(name="process_document", type=SpanType.TOOL)
def process(self, doc_id: str) -> dict:
    # Only doc_id is captured as input, not the full document
    doc = self.fetch_document(doc_id)
    return {"summary": doc.summary, "status": "processed"}


# @end keep_input_output_data_reasonable


# --- Final Cleanup ---

galtea.products.delete(product_id=product_id)
