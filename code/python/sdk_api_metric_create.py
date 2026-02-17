"""
SDK API: Metric Create
Demonstrates how to create metrics for evaluating products.
"""

from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# @start full_prompt_llm_as_a_judge
metric = galtea.metrics.create(
    name="accuracy_v1_full_" + run_identifier,

    evaluator_model_name="GPT-4.1",
    source="full_prompt",
    judge_prompt='Determine whether the output is equivalent to the expected output. Output: "{actual_output}". Expected Output: "{expected_output}."',
    tags=["custom", "accuracy"],
    description="A custom accuracy metric.",
)
# @end full_prompt_llm_as_a_judge

if metric is None:
    raise ValueError("metric is None")
galtea.metrics.delete(metric_id=metric.id)

# @start partial_prompt_llm_as_a_judge
metric = galtea.metrics.create(
    name="accuracy_v1_partial_" + run_identifier,

    evaluator_model_name="GPT-4.1",
    source="partial_prompt",
    judge_prompt="Determine whether the actual output is equivalent to the expected output",
    evaluation_params=["actual_output", "expected_output"],
    tags=["custom", "accuracy"],
    description="A custom accuracy metric.",
)
# @end partial_prompt_llm_as_a_judge

if metric is None:
    raise ValueError("metric is None")
galtea.metrics.delete(metric_id=metric.id)

# @start self_hosted
metric = galtea.metrics.create(
    name="accuracy_v1_self_" + run_identifier,

    source="self_hosted",
    tags=["custom", "accuracy"],
    description="A custom accuracy metric calculated by our custom score function.",
)
# @end self_hosted

if metric is None:
    raise ValueError("metric is None")
galtea.metrics.delete(metric_id=metric.id)
