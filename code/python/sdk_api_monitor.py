"""
SDK API: Monitor
Demonstrates how to create, list, get, update, pause, resume, and delete monitors.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

product_id: str = create_test_product(
    galtea,
    name=f"docs-monitor-product-{run_identifier}",
    description="Product for monitor documentation",
    capabilities="Answer questions about products",
    inabilities="Cannot process payments",
)

# A monitor scores production sessions with metric FAMILIES, not specific metric revisions.
# The family key is `metric.metric_group_id` — pass that, not `metric.id`.
# A monitor cannot bind a self-hosted metric: it evaluates production sessions with no caller
# to supply a score, and a self-hosted metric's score always comes from the caller.
metric = galtea.metrics.create(
    name=f"monitor-demo-metric-{run_identifier}",
    evaluator_model_name="GPT-4.1",
    source="partial_prompt",
    judge_prompt="Determine whether the actual output answers the input politely and on topic",
    evaluation_params=["input", "actual_output"],
    description="Metric for monitor documentation",
)
if metric is None:
    raise ValueError("metric is None")
if metric.metric_group_id is None:
    raise ValueError("metric.metric_group_id is None")
metric_group_id: str = metric.metric_group_id

# @start create
monitor = galtea.monitors.create(
    name="Production quality monitor",
    product_id=product_id,
    metric_group_ids=[metric_group_id],
    # Optional: watch a single version. Omit to watch every version of the product.
    # version_id="your-version-id",
    sampling_percentage=10,  # score 10% of production sessions (default)
    monthly_credit_cap=5000,  # stop scoring after 5000 credits this month; None means uncapped
)
# @end create

if monitor is None:
    raise ValueError("monitor is None")

# A Specification groups the metrics that measure one product requirement. A monitor can bind it
# instead of picking metric families, and follows the Specification's metric links from its next scan.
specification = galtea.specifications.create(
    product_id=product_id,
    name="Answer product questions",
    description="The assistant answers questions about the product politely and on topic.",
    type="CAPABILITY",
)
if specification is None:
    raise ValueError("specification is None")
galtea.specifications.link_metrics(specification_id=specification.id, metric_ids=[metric.id])

# @start create_with_specification
specification_monitor = galtea.monitors.create(
    name="Production specification monitor",
    product_id=product_id,
    specification_ids=[specification.id],
    # Optional: add metric families too. The monitor scores the union of both.
    # metric_group_ids=[metric_group_id],
)
# @end create_with_specification

if specification_monitor is None:
    raise ValueError("specification_monitor is None")

# @start get
monitor = galtea.monitors.get(monitor_id=monitor.id)
# @end get

# @start list
monitors = galtea.monitors.list(
    product_ids=[product_id],
    statuses=["ACTIVE"],
)
# @end list

# @start update
# Raise the sampling rate. Only the fields you pass change.
galtea.monitors.update(monitor.id, sampling_percentage=25)
# @end update

# @start update_specifications
# Replace the bound Specifications. Pass an empty list to unbind them all.
# The monitor must keep at least one metric family or Specification.
galtea.monitors.update(specification_monitor.id, specification_ids=[specification.id])
# @end update_specifications

# @start pause
# Stop scoring until the monitor is resumed. The monitor keeps its configuration.
paused_monitor = galtea.monitors.pause(monitor.id)
# @end pause

# @start resume
# Score new production sessions again.
resumed_monitor = galtea.monitors.resume(monitor.id)
# @end resume

# @start delete
galtea.monitors.delete(monitor_id=monitor.id)
# @end delete

galtea.monitors.delete(monitor_id=specification_monitor.id)
