"""
SDK API: Run
Demonstrates how to open a run, join work to it, find it again, list runs,
close a run explicitly and delete it, through the handle and through the service.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

product_id: str = create_test_product(
    galtea,
    name=f"docs-run-product-{run_identifier}",
    description="Product for run documentation",
    capabilities="Answer questions about geography",
    inabilities="Cannot process payments",
)

version = galtea.versions.create(product_id=product_id)
if version is None:
    raise ValueError("version is None")
version_id: str = version.id

# @start start
with galtea.runs.start(product_id=product_id, custom_id="ci-build-42") as run:
    print(f"Opened run #{run.ordinal} ({run.id})")

    # Every session and evaluation created inside the block joins the run.
    session = galtea.sessions.create(version_id=version_id, is_production=False)
    galtea.traces.create_batch(
        session_id=session.id,
        conversation_turns=[
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
        ],
    )
    galtea.evaluations.create(session_id=session.id, metrics=[{"name": "Conversation Relevancy"}])
# Leaving the block closes the run, whether the block finished or raised.
# @end start

closed_run_id: str = run.id

# @start get_by_custom_id
run = galtea.runs.get_by_custom_id(product_id=product_id, custom_id="ci-build-42")
print(f"Run {run.id} holds {run.session_count} sessions and {run.evaluation_count} evaluations")
# @end get_by_custom_id

assert run.id == closed_run_id, "get_by_custom_id returned another run"
assert run.session_count == 1, f"expected 1 session in the run, got {run.session_count}"

# @start get
run = galtea.runs.get(run_id=run.id)
for launch in run.launches or []:
    print(f"{launch.kind}: {launch.status}")
# @end get

# @start list
runs = galtea.runs.list(
    product_ids=[product_id],
    sort_by_created_at="desc",
    limit=10,
)
# @end list

assert any(listed.id == closed_run_id for listed in runs), "the closed run is missing from the list"

# @start close
# A run you open without a `with` block stays open until you close it yourself.
nightly_run = galtea.runs.start(product_id=product_id, custom_id="nightly-2026-09-16")
closed_run = nightly_run.close()
print(f"Run {closed_run.id} ended as {closed_run.status}")

# With only the id in hand, close the run through the service.
rerun = galtea.runs.start(product_id=product_id, custom_id="nightly-2026-09-16-rerun")
galtea.runs.close(run_id=rerun.id)
# @end close

# @start delete
# The handle deletes the run it holds.
nightly_run.delete()

# With only the id in hand, delete the run through the service.
galtea.runs.delete(run_id=rerun.id)
# @end delete

# === Cleanup ===
galtea.products.delete(product_id=product_id)
