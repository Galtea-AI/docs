"""
SDK API: Metric Analytics Exclusion
Demonstrates how to check the impact of excluding a metric revision from
analytics, then exclude and restore it.
"""

from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

metric = galtea.metrics.create(
    name="analytics-exclusion-demo-" + run_identifier,
    source="self_hosted",
    description="Metric for the analytics exclusion documentation demo.",
)
if metric is None:
    raise ValueError("metric is None")
metric_id = metric.id

try:
    # @start get_analytics_exclusion_impact
    impact = galtea.metrics.get_analytics_exclusion_impact(metric_id=metric_id)
    print(f"Results affected:  {impact.result_count}")
    for product in impact.products:
        print(f"  {product.name}: {product.result_count} results")
    # @end get_analytics_exclusion_impact

    # @start set_analytics_exclusion
    metric = galtea.metrics.set_analytics_exclusion(metric_id=metric_id, excluded=True)
    print(f"Excluded from analytics at: {metric.excluded_from_analytics_at}")

    # Restore it: its results go back into scores and coverage.
    metric = galtea.metrics.set_analytics_exclusion(metric_id=metric_id, excluded=False)
    # @end set_analytics_exclusion
finally:
    galtea.metrics.delete(metric_id=metric_id)
