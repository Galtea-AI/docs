from datetime import datetime

# @start the_decorator_syntax_options
from galtea import Galtea, TraceType, trace


# Full specification
@trace(name="my_operation", type=TraceType.TOOL)
def my_function_1():
    # Function implementation ...
    print("Doing something...")


# Name only (type defaults to None, for unclassified operations)
@trace(name="custom_name")
def my_function_2():
    # Function implementation ...
    print("Doing something else...")


# Include function docstring as trace description
@trace(type=TraceType.TOOL, include_docstring=True)
def my_function_3(user_id: str):
    """Fetch user data from the database given a user ID."""
    # Function implementation ...
    print(f"Fetching data for user {user_id}...")


# Bare decorator (uses function name)
@trace()
def my_function_4():
    # Function implementation ...
    print("Doing another thing...")


# @end the_decorator_syntax_options


# @start the_decorator_error_tracking
@trace(name="risky_operation", type=TraceType.TOOL)
def risky_call(self, data: str) -> str:
    if not data:
        raise ValueError("Data cannot be empty")
    return f"Processed: {data}"


# @end the_decorator_error_tracking


run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")
galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Trace Concepts Demo " + run_identifier,
        "description": "Demo product for trace concepts",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for trace concepts",
)
if version is None:
    raise ValueError("version is None")

session = galtea.sessions.create(version.id, is_production=True)
if session is None:
    raise ValueError("session is None")

from galtea import AgentInput, AgentResponse, Galtea, TraceType  # noqa: E402


# Empty parentheses
@trace(name="Function that calls another traced function")
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

# @start the_decorator_viewing_trace_hierarchy
traces = galtea.traces.list(inference_result_id=inference_result.id)

print("Trace Hierarchy:")


def print_trace_tree(traces, parent_id=None, indent=0):
    for trace in traces:
        if trace.parent_trace_id == parent_id:
            prefix = "  " * indent + ("└─ " if indent > 0 else "")
            print(f"{prefix}{trace.name} ({trace.type}) - {trace.latency_ms:.2f}ms")
            print_trace_tree(traces, trace.id, indent + 1)


print_trace_tree(traces)
# @end the_decorator_viewing_trace_hierarchy


# @start naming_tips
# ✅ Good - descriptive
@trace(name="fetch_customer_orders")
# ❌ Bad - generic
@trace(name="step_1")
# @end naming_tips


# @start trace_at_meaningful_boundaries
# ✅ Good - meaningful operation
@trace(name="search_products", type=TraceType.RETRIEVER)
def search_products(self, query):
    results = self._query_vector_db(query)  # Internal, not traced
    return self._format_results(results)  # Internal, not traced


# @end trace_at_meaningful_boundaries


# @start select_appropriate_node_types
# ✅ Good - correct classification
@trace(name="generate_evaluation_metrics", type=TraceType.RETRIEVER)
def fetch_user_data(self, user_id: str) -> dict:
    # Function implementation ...
    return {"user_id": user_id, "data": "Sample data"}


# ❌ Bad - incorrect classification
@trace(name="generate_evaluation_metrics", type=TraceType.TOOL)
def fetch_user_data_incorrect(self, user_id: str) -> dict:
    # Function implementation ...
    return {"user_id": user_id, "data": "Sample data"}


# @end select_appropriate_node_types


# @start keep_input_output_data_reasonable
@trace(name="process_document", type=TraceType.TOOL)
def process(self, doc_id: str) -> dict:
    # Only doc_id is captured as input, not the full document
    doc = self.fetch_document(doc_id)
    return {"summary": doc.summary, "status": "processed"}


# @end keep_input_output_data_reasonable


# --- Final Cleanup ---

galtea.products.delete(product_id=product_id)
