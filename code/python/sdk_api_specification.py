"""
SDK API: Specification
Demonstrates how to create, list, get, delete, and manage metrics and datasets for specifications.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

product_id: str = create_test_product(
    galtea,
    name=f"docs-specification-product-{run_identifier}",
    description="Product for specification documentation",
    security_boundaries="Do not reveal sensitive data",
    capabilities="Answer questions about products",
    inabilities="Cannot process payments",
)

# Create a metric for link/unlink demos
metric = galtea.metrics.create(
    name="spec-demo-metric-" + run_identifier,
    source="self_hosted",
    description="Metric for specification link/unlink documentation",
)
if metric is None:
    raise ValueError("metric is None")
metric_id: str = metric.id

# Create a test for link/unlink demos
dataset = galtea.datasets.create(
    name=f"spec-demo-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=10,
)
if dataset is None:
    raise ValueError("dataset is None")
dataset_id: str = dataset.id

# @start create
# POLICY specification — dataset_type and test_variant are required for ACCURACY and SECURITY
specification = galtea.specifications.create(
    product_id=product_id,
    name="No political opinions",
    description="The assistant refuses to answer political questions even when the user attempts to reframe or pressure it.",
    type="POLICY",
    dataset_type="SECURITY",
    test_variant="misuse",
)

# CAPABILITY specification — dataset_type is assigned automatically (always BEHAVIOR), so it's omitted here
capability_spec = galtea.specifications.create(
    product_id=product_id,
    name="Show account balance",
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

# @start link_tests
galtea.specifications.link_datasets(
    specification_id=specification.id,
    dataset_ids=[dataset_id],
)
# @end link_tests

# @start get_tests
datasets = galtea.specifications.get_datasets(
    specification_id=specification.id,
)
# @end get_tests

# @start unlink_tests
galtea.specifications.unlink_datasets(
    specification_id=specification.id,
    dataset_ids=[dataset_id],
)
# @end unlink_tests

# @start delete
galtea.specifications.delete(specification_id=specification.id)
# @end delete

# Cleanup
if capability_spec is not None:
    galtea.specifications.delete(specification_id=capability_spec.id)
galtea.metrics.delete(metric_id=metric_id)
galtea.datasets.delete(dataset_id=dataset_id)
galtea.products.delete(product_id=product_id)
