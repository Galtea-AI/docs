"""
SDK API: User Group
Demonstrates how to create, list, get, update, delete user groups, and link/unlink users and metrics.
"""

from datetime import datetime

from _test_helpers import list_users
from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Setup: create two self-hosted metrics for link/unlink demos
metric_1 = galtea.metrics.create(
    name="ug-demo-metric-1-" + run_identifier,
    source="self_hosted",
    description="Temporary metric for user group demo",
)
if metric_1 is None:
    raise ValueError("Failed to create metric_1")
metric_id_1 = metric_1.id

metric_2 = galtea.metrics.create(
    name="ug-demo-metric-2-" + run_identifier,
    source="self_hosted",
    description="Temporary metric for user group demo",
)
if metric_2 is None:
    raise ValueError("Failed to create metric_2")
metric_id_2 = metric_2.id

# @start create
user_group = galtea.user_groups.create(
    name="quality-reviewers-" + run_identifier,
    description="Team responsible for reviewing output quality",
)
# @end create

if user_group is None:
    raise ValueError("user_group is None")

user_group_id = user_group.id

# Setup: fetch a real user ID for link/unlink demos (filtered by organization)
users_data = list_users(galtea, organization_id=user_group.organization_id)
user_id_1 = users_data[0]["id"]

# @start list
user_groups = galtea.user_groups.list(
    sort_by_created_at="desc",
    limit=10,
)
# @end list

# @start get
user_group = galtea.user_groups.get(user_group_id=user_group_id)
# @end get

# @start get_by_name
user_group = galtea.user_groups.get_by_name(name="quality-reviewers-" + run_identifier)
# @end get_by_name

# @start update
user_group = galtea.user_groups.update(
    user_group_id=user_group_id,
    name="senior-quality-reviewers-" + run_identifier,
    description="Senior team for quality reviews",
)
# @end update

# @start link_users
galtea.user_groups.link_users(
    user_group_id=user_group_id,
    user_ids=[user_id_1],
)
# @end link_users

# @start unlink_users
galtea.user_groups.unlink_users(
    user_group_id=user_group_id,
    user_ids=[user_id_1],
)
# @end unlink_users

# @start link_metrics
galtea.user_groups.link_metrics(
    user_group_id=user_group_id,
    metric_ids=[metric_id_1, metric_id_2],
)
# @end link_metrics

# @start create_human_evaluation_metric
metric = galtea.metrics.create(
    name="domain-expert-review",
    source="human_evaluation",
    judge_prompt="Review the assistant's response for accuracy and helpfulness. Score 1 if the response is correct and useful, 0 if it contains errors or is unhelpful.",
    evaluation_params=["input", "actual_output", "expected_output"],
    user_group_ids=[user_group_id],
    description="Domain expert review of response quality",
)

# Link the metric to the user group
galtea.user_groups.link_metrics(
    user_group_id=user_group_id,
    metric_ids=[metric.id],
)
# @end create_human_evaluation_metric

# @start unlink_metrics
galtea.user_groups.unlink_metrics(
    user_group_id=user_group_id,
    metric_ids=[metric_id_2],
)
# @end unlink_metrics

# Cleanup: unlink remaining metric before deleting
galtea.user_groups.unlink_metrics(
    user_group_id=user_group_id,
    metric_ids=[metric_id_1],
)

# @start delete
galtea.user_groups.delete(user_group_id=user_group_id)
# @end delete

# Cleanup: delete the temporary metrics
galtea.metrics.delete(metric_id=metric_id_1)
galtea.metrics.delete(metric_id=metric_id_2)
