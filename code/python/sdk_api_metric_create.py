"""
SDK API: Metric Create
Demonstrates how to create metrics for evaluating products.
"""

from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# @start ai_evaluation
metric = galtea.metrics.create(
    name="accuracy_v1_" + run_identifier,
    evaluator_model_name="GPT-4.1",
    source="partial_prompt",
    judge_prompt="Determine whether the actual output is equivalent to the expected output",
    evaluation_params=["input", "actual_output", "expected_output"],
    tags=["custom", "accuracy"],
    description="A custom accuracy metric.",
)
# @end ai_evaluation

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

# Setup: create a user group for the human evaluation example
user_group = galtea.user_groups.create(
    name="qa-team-" + run_identifier,
    description="QA annotators for human evaluation",
)
if user_group is None:
    raise ValueError("user_group is None")
user_group_id = user_group.id

# @start human_evaluation
metric = galtea.metrics.create(
    name="human_eval_v1_" + run_identifier,
    source="human_evaluation",
    judge_prompt="Review the actual output and score it based on helpfulness, accuracy, and tone. Score 1 if the response is helpful and accurate. Score 0 if it is unhelpful or incorrect.",
    evaluation_params=["input", "actual_output", "expected_output"],
    user_group_ids=[user_group_id],
    tags=["human", "quality"],
    description="A human evaluation metric scored by QA annotators.",
)
# @end human_evaluation

if metric is None:
    raise ValueError("metric is None")
galtea.metrics.delete(metric_id=metric.id)
