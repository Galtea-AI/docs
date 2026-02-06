from datetime import datetime

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")
metric_name = "Generic Metric " + run_identifier

# @start example
import os

from dotenv import load_dotenv
from galtea import Galtea

load_dotenv()

galtea = Galtea(api_key=os.getenv("GALTEA_API_KEY"))

# Create a new metric
metric = galtea.metrics.create(
    name=metric_name,
    test_type="ACCURACY",  # or "SECURITY", "BEHAVIOR"
    source="partial_prompt",
    judge_prompt="""
    **Role:** You are evaluating the [aspect] of the ACTUAL_OUTPUT.

    **Evaluation Criteria:**

    For each [unit of analysis], verify:

    1. **[Criterion name]:** [Specific, measurable condition with examples]
    2. **[Criterion name]:** [Specific, measurable condition with examples]
    3. **[Criterion name]:** [Specific, measurable condition with examples]

    **Scoring Rubric:**

    - **Score 1:** [Clear threshold for success, e.g., "All evaluation criteria are met."]
    - **Score 0:** [Clear threshold for failure, e.g., "One or more evaluation criteria are not met."]
    """,
    evaluator_model_name="GPT-4o",
    evaluation_params=["input", "actual_output"],
    description="Generic Metric",
    tags=["quality"],
)
# @end example

if metric is None:
    raise ValueError("metric is None")
galtea.metrics.delete(metric.id)
