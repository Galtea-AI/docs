from datetime import datetime

from galtea import Galtea

# @start creating_custom_metrics_via_partial

judge_prompt = """
**Evaluation Criteria:**
Check if the ACTUAL_OUTPUT is good by comparing it to what was expected. Focus on:
1. Factual accuracy and correctness
2. Completeness of the ACTUAL_OUTPUT, regarding the user INPUT
3. Appropriate use of provided CONTEXT information to answer the user INPUT
4. Overall helpfulness and relevance to the user INPUT

**Rubric:**
Score 1 (Good): The ACTUAL_OUTPUT is accurate, complete, uses information properly, and truly helps the user.
Score 0 (Bad): The ACTUAL_OUTPUT has major errors, missing parts, ignores important info, or doesn't help the user.
"""
# @end creating_custom_metrics_via_partial
run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")
metric_name = "Human Quality Review " + run_identifier
galtea = Galtea(api_key="YOUR_API_KEY")

# Setup: create user groups for the human evaluation example
quality_reviewers_group = galtea.user_groups.create(
    name="quality-reviewers-" + run_identifier,
    description="Quality reviewers for human evaluation",
)
if quality_reviewers_group is None:
    raise ValueError("Failed to create quality reviewers user group")
quality_reviewers_group_name = (
    quality_reviewers_group.name if quality_reviewers_group else ""
)

# @start human_evaluation_example
quality_reviewers_group = galtea.user_groups.get_by_name(quality_reviewers_group_name)
metric = galtea.metrics.create(
    name=metric_name,
    source="human_evaluation",
    judge_prompt="Evaluate the quality of the response based on accuracy, completeness, and clarity.",
    evaluation_params=["input", "actual_output", "expected_output"],
    user_group_ids=[quality_reviewers_group.id],
)
# @end human_evaluation_example

if metric is None:
    raise ValueError("Failed to create human evaluation metric")

# Cleanup
try:
    galtea.metrics.delete(metric_id=metric.id)
except Exception:
    pass
try:
    galtea.user_groups.delete(user_group_id=quality_reviewers_group.id)
except Exception:
    pass
