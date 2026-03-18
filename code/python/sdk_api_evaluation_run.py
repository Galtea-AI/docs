from galtea import Galtea

galtea = Galtea(api_key="YOUR_API_KEY")
version_id = "YOUR_VERSION_ID"

# @start run_endpoint_connection
# Run evaluation using your deployed endpoint connection
result = galtea.evaluations.run(version_id=version_id)
print(f"Job {result['jobId']} queued {result['testCaseCount']} test cases")
for spec in result["specifications"]:
    print(f"  Spec {spec['specificationId']}: {spec['testCount']} tests, {spec['metricCount']} metrics")
# @end run_endpoint_connection

# Extract real specification IDs from the result for subsequent examples
specification_ids = [spec["specificationId"] for spec in result["specifications"]][:2]

# @start run_with_specification_ids
# Evaluate only specific specifications
result = galtea.evaluations.run(
    version_id=version_id,
    specification_ids=specification_ids,
)
# @end run_with_specification_ids

# @start run_with_agent
# Run evaluation with a local agent (SDK-side loop)
def my_agent(user_message: str) -> str:
    # Replace with your actual agent logic
    return "Agent response"

result = galtea.evaluations.run(
    version_id=version_id,
    agent=my_agent,
    specification_ids=specification_ids[:1],
)
print(f"Processed {result['testCaseCount']} test cases")
print(f"Created {len(result['evaluations'])} evaluations")
# @end run_with_agent
