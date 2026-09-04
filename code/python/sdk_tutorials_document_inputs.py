from datetime import datetime
from typing import Optional

from galtea import Galtea

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
    """Read the documents and answer. This step is yours: Galtea stores the files, it does not read them."""
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

galtea.products.delete(product_id=product_id)
