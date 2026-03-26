from galtea import Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

# @start wait_for_basic
# Create evaluations and wait for them to complete
evaluations = galtea.evaluations.create(
    session_id="session_123",
    metrics=[{"name": "accuracy"}, {"name": "relevance"}],
)

# Wait for all evaluations to leave PENDING status
completed = galtea.evaluations.wait_for(
    evaluation_ids=[e.id for e in evaluations],
)

for evaluation in completed:
    print(f"{evaluation.id}: {evaluation.status} — score: {evaluation.score}")
# @end wait_for_basic

# @start wait_for_custom_timeout
# Wait with a custom timeout and poll interval
completed = galtea.evaluations.wait_for(
    evaluation_ids=[e.id for e in evaluations],
    timeout=600,       # wait up to 10 minutes
    poll_interval=10,  # check every 10 seconds
)
# @end wait_for_custom_timeout

# @start wait_for_run_lifecycle
# Full async evaluation lifecycle: run, then wait for results
result = galtea.evaluations.run(
    version_id="version_123",
    agent=lambda msg: "Agent response",
)

# Collect evaluation IDs from the run result
evaluation_ids = [e.id for e in result["evaluations"]]

# Wait for all evaluations to complete
completed = galtea.evaluations.wait_for(evaluation_ids)

for evaluation in completed:
    print(f"Metric {evaluation.metric_id}: {evaluation.status} — {evaluation.score}")
# @end wait_for_run_lifecycle
