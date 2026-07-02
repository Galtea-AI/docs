"""
SDK API: WebRTC Connection
Demonstrates how to create, list, get, update, and delete WebRTC connections.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Setup: register a product for this demo
product_id = create_test_product(
    galtea,
    name="WebRTC Connection Demo " + run_identifier,
    description="Demo product for WebRTC connection API",
)

# @start create
web_rtc_connection = galtea.web_rtc_connections.create(
    product_id=product_id,
    name="production-voice-agent-" + run_identifier,
    api_key="YOUR_PIPECAT_CLOUD_API_KEY",
    agent_name="my-pipecat-agent",
    agent_speaks_first=False,
)
# @end create

if web_rtc_connection is None:
    raise ValueError("web_rtc_connection is None")

web_rtc_connection_id = web_rtc_connection.id

# The API never returns the api_key. Use has_api_key to check that a key is set.
assert web_rtc_connection.has_api_key is True

# @start list
web_rtc_connections = galtea.web_rtc_connections.list(
    product_ids=[product_id],
    sort_by_created_at="desc",
    limit=10,
)
# @end list

# @start get
web_rtc_connection = galtea.web_rtc_connections.get(web_rtc_connection_id=web_rtc_connection_id)
# @end get

# @start get_by_name
web_rtc_connection = galtea.web_rtc_connections.get_by_name(
    name="production-voice-agent-" + run_identifier,
    product_id=product_id,
)
# @end get_by_name

# @start update
web_rtc_connection = galtea.web_rtc_connections.update(
    web_rtc_connection_id=web_rtc_connection_id,
    agent_speaks_first=True,
)
# @end update

# @start delete
galtea.web_rtc_connections.delete(web_rtc_connection_id=web_rtc_connection_id)
# @end delete

# === Cleanup ===
galtea.products.delete(product_id=product_id)
