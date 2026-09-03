from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-input-files-{run_identifier}",
    description="Product that reads uploaded documents",
    capabilities="Read a contract and answer questions about it",
    inabilities="Cannot sign anything",
)

# @start dataset_with_input_files
dataset = galtea.datasets.create(
    name=f"document-dataset-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    dataset_file_path="path/to/document_dataset.csv",
)
# @end dataset_with_input_files
if dataset is None:
    raise ValueError("dataset from create is None")

# @start test_case_with_input_file
test_case = galtea.test_cases.create(
    dataset_id=dataset.id,
    input="Summarize this contract",
    input_file_paths=["path/to/contrato-arrendamiento.pdf"],
)
# @end test_case_with_input_file
if not test_case.input_files:
    raise ValueError("the created test case carries no file")
print(f"Attached {test_case.input_files[0].filename} ({test_case.input_files[0].mime_type})")

# @start test_case_file_only
document_only = galtea.test_cases.create(
    dataset_id=dataset.id,
    input_file_paths=["path/to/contrato-arrendamiento.pdf"],
)
# @end test_case_file_only
if document_only.input is not None:
    raise ValueError("a document-only test case should have no input text")

# @start upload_input_file
lease = galtea.test_cases.upload_input_file("path/to/contrato-arrendamiento.pdf")

for question in ["Which clauses limit the cover?", "What is the excess?"]:
    galtea.test_cases.create(
        dataset_id=dataset.id,
        input={"user_message": question, "content": [lease.model_dump(by_alias=True)]},
    )
# @end upload_input_file

reread = galtea.test_cases.get(test_case.id)
if not reread.input_files:
    raise ValueError("the stored test case lost its file")
print(f"Test case {reread.id} keeps {len(reread.input_files)} file(s)")
