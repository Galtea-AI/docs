"""
SDK API: Endpoint Connection
Demonstrates how to create, list, get, update, delete, and test endpoint connections.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import EndpointConnectionType, Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Setup: create a product for this demo
product_id = create_test_product(
    galtea,
    name="Endpoint Connection Demo " + run_identifier,
    description="Demo product for endpoint connection API",
)

# @start create
endpoint_connection = galtea.endpoint_connections.create(
    name="production-chat-api-" + run_identifier,
    product_id=product_id,
    url="https://api.example.com/v1/chat",
    type=EndpointConnectionType.CONVERSATION,
    http_method="POST",
    auth_type="BEARER",
    auth_token="YOUR_AUTH_TOKEN",
    input_template='{"message": "{{ input.user_message }}"}',
    output_mapping={"output": "$.response"},
    timeout=30,
)
# @end create

if endpoint_connection is None:
    raise ValueError("endpoint_connection is None")

endpoint_connection_id = endpoint_connection.id

# @start list
endpoint_connections = galtea.endpoint_connections.list(
    product_ids=[product_id],
    sort_by_created_at="desc",
    limit=10,
)
# @end list

# @start get
endpoint_connection = galtea.endpoint_connections.get(
    endpoint_connection_id=endpoint_connection_id
)
# @end get

# @start get_by_name
endpoint_connection = galtea.endpoint_connections.get_by_name(
    name="production-chat-api-" + run_identifier,
    product_id=product_id,
)
# @end get_by_name

# @start update
endpoint_connection = galtea.endpoint_connections.update(
    endpoint_connection_id=endpoint_connection_id,
    timeout=60,
    rate_limit=100,
)
# @end update

# test() makes a real HTTP request to the endpoint URL.
# The API handles connection failures gracefully (returns success=False),
# but we wrap in try/except to ensure cleanup (delete) always runs.
try:
    # @start test
    test_result = galtea.endpoint_connections.test(
        id=endpoint_connection_id,
    )
    # @end test

    # @start test_no_id
    test_result = galtea.endpoint_connections.test(
        url="https://api.example.com/v1/chat",
        http_method="POST",
        auth_type="BEARER",
        auth_token="YOUR_AUTH_TOKEN",
        input_template='{"message": "{{ input.user_message }}"}',
        output_mapping={"output": "$.response"},
        type=EndpointConnectionType.CONVERSATION,
        timeout=30,
    )
    # @end test_no_id
except Exception:
    pass

# @start delete
galtea.endpoint_connections.delete(
    endpoint_connection_id=endpoint_connection_id
)
# @end delete

# === Cleanup ===
galtea.products.delete(product_id=product_id)
