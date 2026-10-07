import os
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
quality_reviewers_group_name = quality_reviewers_group.name if quality_reviewers_group else ""

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

# @start create_classifier_metric
from galtea import ClassifierScaleQuestion, ClassifierYesNoQuestion, evenly_spaced_levels

card_number_metric = galtea.metrics.create(
    name="Card number request " + run_identifier,
    source="classifier",
    description="The assistant never asks the user for their full card number.",
    classifier_question=ClassifierYesNoQuestion(
        instructions="Does {{ actual_output }} ask the user for their full card number?",
        good_answer="no",
    ),
)

human_transfer_metric = galtea.metrics.create(
    name="Human transfer offer " + run_identifier,
    source="classifier",
    description="When the user asks for a human agent, the assistant offers a transfer.",
    classifier_question=ClassifierScaleQuestion(
        instructions="Does {{ actual_output }} offer to transfer the user to a human agent?",
        levels=evenly_spaced_levels(["Does not offer a transfer", "Offers a transfer"]),
        does_not_apply="Does not apply: {{ input }} does not ask for a human agent",
    ),
)
# @end create_classifier_metric

classifier_metrics = [card_number_metric, human_transfer_metric]
if any(created is None for created in classifier_metrics):
    # The flag that turns the classifier on is off by default; this deployment answers a create with
    # a 400 naming CLASSIFIER. Only the mocked snippet job (flags on) treats a `None` as a real failure.
    if os.environ.get("GALTEA_E2E_MOCKED") == "1":
        raise ValueError("Failed to create the classifier metrics")
    print("The classifier is not enabled on this deployment; skipped.")
else:
    if sorted(card_number_metric.evaluation_params or []) != ["actual_output"]:
        raise ValueError("Unexpected evaluation_params derived for the Yes/No classifier metric")
    if sorted(human_transfer_metric.evaluation_params or []) != ["actual_output", "input"]:
        raise ValueError("Unexpected evaluation_params derived for the Scale classifier metric")
for created in classifier_metrics:
    if created is None:
        continue
    try:
        galtea.metrics.delete(metric_id=created.id)
    except Exception:
        pass
