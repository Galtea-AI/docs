import os
from datetime import datetime
from typing import Optional

from galtea import AgentInput, AgentResponse, Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-document-inputs-{run_identifier}",
    description="Product that reads lease contracts and extracts their terms",
    capabilities="Read a lease contract and return the tenant and the monthly rent as JSON",
    inabilities="Cannot sign anything",
)

version = galtea.versions.create(product_id=product_id, name=f"v-{run_identifier}")

# @start attach
dataset = galtea.datasets.create(
    name=f"lease-documents-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    dataset_file_path="path/to/lease_dataset.csv",
)
# @end attach


# @start pipeline
def answer_from_documents(question: Optional[str], document_paths: list[str]) -> str:
    """Read the documents and answer. Galtea never reads them for you. This step is yours when you
    drive the run; Galtea can also send the files to your endpoint instead."""
    # Replace this with the call to your own model, parser or agent.
    return '{"tenant": "A. Garcia", "monthly_rent": 900}'


# @end pipeline

# @start workflow
test_cases = galtea.test_cases.list(dataset_id=dataset.id, include_legacy=False)

for test_case in test_cases:
    # None when the test case carries a document and no text of its own.
    question = test_case.input

    # Each file is saved under the name it was uploaded with, not its storage key.
    document_paths = [
        galtea.storage.download(attached, output_directory="./.temp/lease-documents")
        for attached in test_case.input_files
    ]
    print(f"Test case {test_case.id}: {question or '(document only)'} + {len(document_paths)} file(s)")

    answer = answer_from_documents(question, document_paths)

    session = galtea.sessions.create(version_id=version.id, test_case_id=test_case.id)
    galtea.traces.create_and_evaluate(
        session_id=session.id,
        output=answer,
        metrics=[{"name": "JSON Field Match"}],
    )
# @end workflow

if len(test_cases) != 2:
    raise ValueError(f"expected the csv's two rows, got {len(test_cases)}")

# Link the metric and the dataset to a specification so `evaluations.run()` can discover both.
json_field_match = galtea.metrics.get_by_name(name="JSON Field Match")
specification = galtea.specifications.create(
    product_id=product_id,
    name="Extracts the lease terms",
    description="The product returns the tenant and the monthly rent of the lease as JSON.",
    type="POLICY",
    dataset_type="ACCURACY",
    dataset_variant="entity_extraction",
    metric_ids=[json_field_match.id],
)
if specification is None:
    raise ValueError("Failed to create specification")
galtea.specifications.link_datasets(specification_id=specification.id, dataset_ids=[dataset.id])


# @start evaluations_run
def document_agent(input_data: AgentInput) -> AgentResponse:
    # The same InputFile objects as test_case.input_files: filename and mime_type match.
    document_paths = [
        galtea.storage.download(attached, output_directory="./.temp/lease-documents")
        for attached in input_data.input_files
    ]
    # None for a document-only test case, like test_case.input above.
    question = input_data.last_user_message_str() or None
    return AgentResponse(content=answer_from_documents(question, document_paths))


result = galtea.evaluations.run(
    version_id=version.id,
    agent=document_agent,
    specification_ids=[specification.id],
)
print(f"Evaluated {result['testCaseCount']} test cases")
# @end evaluations_run

if result["testCaseCount"] != 2:
    raise ValueError(f"expected evaluations.run() to cover the csv's two rows, got {result['testCaseCount']}")

# Checked out here, where a failure fails this script: raised inside the callback it would
# reach simulate(), which reports it as an empty agent response and ends the run normally.
# The callback only writes this file when the attached document reached it.
delivered = os.path.join("./.temp/lease-documents", "lease-agreement.pdf")
if not os.path.isfile(delivered) or os.path.getsize(delivered) == 0:
    raise ValueError(f"the agent never received the attached lease-agreement.pdf at {delivered}")

galtea.products.delete(product_id=product_id)
