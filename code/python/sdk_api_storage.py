from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-storage-{run_identifier}",
    description="Product that reads uploaded documents",
    capabilities="Read a contract and answer questions about it",
    inabilities="Cannot sign anything",
)

dataset = galtea.datasets.create(
    name=f"storage-dataset-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    dataset_file_path="path/to/document_dataset.csv",
)
if dataset is None:
    raise ValueError("dataset from create is None")

test_case = galtea.test_cases.create(
    dataset_id=dataset.id,
    input="Summarize this contract",
    input_file_paths=["path/to/lease-agreement.pdf"],
)
if not test_case.input_files:
    raise ValueError("the created test case carries no file")

# @start upload
uri = galtea.storage.upload("path/to/lease-agreement.pdf")
# @end upload
print(f"Uploaded to {uri.split('?')[0]}")

# @start download
downloaded_path = galtea.storage.download(test_case.input_files[0], output_directory="./.temp")
# @end download

with open("path/to/lease-agreement.pdf", "rb") as original, open(downloaded_path, "rb") as saved:
    if original.read() != saved.read():
        raise ValueError("downloaded bytes do not match the uploaded file")

print(f"Saved {test_case.input_files[0].filename} to {downloaded_path}")
