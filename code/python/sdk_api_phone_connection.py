"""
SDK API: Phone Connection
Demonstrates how to create, list, get, update, and delete phone connections.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Setup: register a product for this demo
product_id = create_test_product(
    galtea,
    name="Phone Connection Demo " + run_identifier,
    description="Demo product for phone connection API",
)

# @start create
phone_connection = galtea.phone_connections.create(
    product_id=product_id,
    name="production-voice-agent-" + run_identifier,
    phone_number="+14155552671",
    voice="alloy",
    language_code="en",
)
# @end create

if phone_connection is None:
    raise ValueError("phone_connection is None")

phone_connection_id = phone_connection.id

# @start list
phone_connections = galtea.phone_connections.list(
    product_ids=[product_id],
    sort_by_created_at="desc",
    limit=10,
)
# @end list

# @start get
phone_connection = galtea.phone_connections.get(
    phone_connection_id=phone_connection_id
)
# @end get

# @start get_by_name
phone_connection = galtea.phone_connections.get_by_name(
    name="production-voice-agent-" + run_identifier,
    product_id=product_id,
)
# @end get_by_name

# @start update
phone_connection = galtea.phone_connections.update(
    phone_connection_id=phone_connection_id,
    language_code="es",
)
# @end update

# @start delete
galtea.phone_connections.delete(
    phone_connection_id=phone_connection_id
)
# @end delete

# === Cleanup ===
galtea.products.delete(product_id=product_id)
