"""
Tutorial: Direct Inferences and Evaluations from the Platform
Code examples for the Direct Inference tracing workflow.
"""

from galtea import Galtea, TraceType, clear_context, set_context, trace

galtea = Galtea(api_key="YOUR_API_KEY")


# @start tracing_in_endpoint_handler
@trace(type=TraceType.AGENT)
def run_agent(query: str) -> str:
    # Your agent logic here — all nested @trace calls
    # will be linked to the inference result automatically
    return "Agent response to: " + query


def my_endpoint_handler(request):
    """Your API endpoint that Galtea calls during Direct Inference."""
    body = request.json()
    user_input = body["messages"][-1]["content"]
    inference_result_id = body["metadata"]["inference_result_id"]

    # Set trace context so all @trace calls are linked to this inference result
    token = set_context(inference_result_id=inference_result_id)
    try:
        response = run_agent(user_input)
    finally:
        # Flush traces to Galtea and clear context
        clear_context(token)

    return {"choices": [{"message": {"content": response}}]}


# @end tracing_in_endpoint_handler
