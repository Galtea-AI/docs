"""
SDK API: Specification
Demonstrates how to create, list, get, delete, and manage metrics for specifications.
"""

from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create product via direct API call (SDK doesn't expose products.create)
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
client.post(
    "products",
    json={
        "name": f"docs-specification-product-{run_identifier}",
        "description": "Product for specification documentation",
        "securityBoundaries": "Do not reveal sensitive data",
        "capabilities": "Answer questions about products",
        "inabilities": "Cannot process payments",
    },
)
products = galtea.products.list(limit=1)
product = products[0]
product_id: str = product.id

# Create a metric for link/unlink demos
metric = galtea.metrics.create(
    name="spec-demo-metric-" + run_identifier,
    source="self_hosted",
    description="Metric for specification link/unlink documentation",
)
if metric is None:
    raise ValueError("metric is None")
metric_id: str = metric.id

# @start create
# POLICY specification — test_type and test_variant are required for QUALITY and RED_TEAMING
specification = galtea.specifications.create(
    product_id=product_id,
    description="The assistant refuses to answer political questions even when the user attempts to reframe or pressure it.",
    type="POLICY",
    test_type="RED_TEAMING",
    test_variant="misuse",
)

# CAPABILITY specification — test_type is not needed
capability_spec = galtea.specifications.create(
    product_id=product_id,
    description="The assistant accurately retrieves and displays the user's current account balance when asked.",
    type="CAPABILITY",
)
# @end create

if specification is None:
    raise ValueError("specification is None")

# @start get
specification = galtea.specifications.get(specification_id=specification.id)
# @end get

# @start list
specifications = galtea.specifications.list(
    product_id=product_id,
    type="CAPABILITY",
)
# @end list

# @start link_metrics
galtea.specifications.link_metrics(
    specification_id=specification.id,
    metric_ids=[metric_id],
)
# @end link_metrics

# @start get_metrics
metrics = galtea.specifications.get_metrics(
    specification_id=specification.id,
)
# @end get_metrics

# @start unlink_metrics
galtea.specifications.unlink_metrics(
    specification_id=specification.id,
    metric_ids=[metric_id],
)
# @end unlink_metrics

# @start delete
galtea.specifications.delete(specification_id=specification.id)
# @end delete

# Cleanup
if capability_spec is not None:
    galtea.specifications.delete(specification_id=capability_spec.id)
galtea.metrics.delete(metric_id=metric_id)
galtea.products.delete(product_id=product_id)
