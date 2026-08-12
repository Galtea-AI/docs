"""
Tutorial: Direct Inferences and Evaluations from the Platform
Code examples for the Direct Inference tracing workflow.
"""

from galtea import Galtea, SpanType, clear_context, set_context, traced

galtea = Galtea(api_key="YOUR_API_KEY")


# @start tracing_in_endpoint_handler
@traced(type=SpanType.AGENT)
def run_agent(query: str) -> str:
    # Your agent logic here — all nested @traced calls
    # will be linked to the trace automatically
    return "Agent response to: " + query


def my_endpoint_handler(request):
    """Your API endpoint that Galtea calls during Direct Inference."""
    body = request.json()
    user_input = body["messages"][-1]["content"]
    trace_id = body["metadata"]["trace_id"]

    # Set Galtea context so all @traced calls are linked to this trace
    token = set_context(trace_id=trace_id)
    try:
        response = run_agent(user_input)
    finally:
        # Flush spans to Galtea and clear context
        clear_context(token)

    return {"choices": [{"message": {"content": response}}]}


# @end tracing_in_endpoint_handler


# @start otel_exporter_programmatic_python
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Read the Galtea API key from the environment at runtime.
# The exporter will send it as `Authorization: Bearer <key>` on every request.
galtea_api_key = os.environ.get("GALTEA_API_KEY")
if not galtea_api_key:
    raise ValueError("GALTEA_API_KEY environment variable is not set")

exporter = OTLPSpanExporter(
    endpoint="https://otel.platform.prod-main.galtea.ai:4318/otel/traces",
    headers={"Authorization": f"Bearer {galtea_api_key}"},
)

# Register the exporter without clobbering a provider another library may have
# already installed — e.g. `opentelemetry-bootstrap` auto-instrumentation (set up
# in step 2 above) or the Galtea SDK. `set_tracer_provider()` is a silent no-op if
# a real provider is already active, so only create one when the active provider is
# still the default proxy; otherwise attach the exporter to the existing provider.
provider = trace.get_tracer_provider()
if isinstance(provider, trace.ProxyTracerProvider):
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

provider.add_span_processor(BatchSpanProcessor(exporter))
# @end otel_exporter_programmatic_python


# @start otel_exporter_programmatic_python_grpc
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Read the Galtea API key from the environment at runtime.
# The exporter will send it as `Authorization: Bearer <key>` on every request.
galtea_api_key = os.environ.get("GALTEA_API_KEY")
if not galtea_api_key:
    raise ValueError("GALTEA_API_KEY environment variable is not set")

# gRPC exporter: the endpoint is `host:port` (no URL path), with TLS enabled.
# gRPC metadata keys must be lowercase, so the header is `authorization`.
exporter = OTLPSpanExporter(
    endpoint="otel.platform.prod-main.galtea.ai:4317",
    insecure=False,
    headers=(("authorization", f"Bearer {galtea_api_key}"),),
)

# Register the exporter without clobbering a provider another library may have
# already installed — e.g. `opentelemetry-bootstrap` auto-instrumentation (set up
# in step 2 above) or the Galtea SDK. `set_tracer_provider()` is a silent no-op if
# a real provider is already active, so only create one when the active provider is
# still the default proxy; otherwise attach the exporter to the existing provider.
provider = trace.get_tracer_provider()
if isinstance(provider, trace.ProxyTracerProvider):
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

provider.add_span_processor(BatchSpanProcessor(exporter))
# @end otel_exporter_programmatic_python_grpc
