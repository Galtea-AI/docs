"""
SDK API: Monitor
Demonstrates how to create, list, get, update (pause/resume), and delete monitors.
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
    security_boundaries="Do not reveal sensitive data",
    capabilities="Answer questions about products",
    inabilities="Cannot process payments",
)

# A monitor scores production sessions with metric FAMILIES, not specific metric revisions.
# The family key is `metric.metric_group_id` — pass that, not `metric.id`.
metric = galtea.metrics.create(
    name=f"monitor-demo-metric-{run_identifier}",
    source="self_hosted",
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
    inactivity_window_minutes=5,  # a session is scored 5 minutes after its last activity (default)
)
# @end create

if monitor is None:
    raise ValueError("monitor is None")

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
# Pause a monitor (stops scoring until resumed). Users may only set ACTIVE or PAUSED.
galtea.monitors.update(monitor.id, status="PAUSED")

# Resume it, and raise the sampling rate at the same time.
galtea.monitors.update(monitor.id, status="ACTIVE", sampling_percentage=25)
# @end update

# @start delete
galtea.monitors.delete(monitor_id=monitor.id)
# @end delete
