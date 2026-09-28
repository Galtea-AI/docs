"""
SDK API: Galtea client errors
Demonstrates catching EntityNotFoundException, which every read raises when the
platform holds nothing under the id or name passed.
"""

from datetime import datetime

from galtea import EntityNotFoundException, Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

metric_name = f"politeness-{run_identifier}"

# @start entity_not_found
try:
    metric = galtea.metrics.get_by_name(name=metric_name)
except EntityNotFoundException:
    metric = galtea.metrics.create(
        name=metric_name,
        evaluator_model_name="GPT-4.1",
        source="partial_prompt",
        judge_prompt="Determine whether the actual output is polite.",
        evaluation_params=["input", "actual_output"],
    )
# @end entity_not_found

assert metric is not None, "the fallback did not produce a metric"
assert metric.name == metric_name, f"expected metric {metric_name}, got {metric.name}"

# The same call now finds it, so the fallback does not run twice.
found = galtea.metrics.get_by_name(name=metric_name)
assert found.id == metric.id, "get_by_name returned another metric"

# === Cleanup ===
galtea.metrics.delete(metric_id=metric.id)
