"""
SDK API: Trace output files.
Logs turns whose answer is a document, then reads the files back.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-output-files-{run_identifier}",
    description="Product that answers with a document",
    capabilities="Draft a lease agreement and return it as a file",
    inabilities="Cannot sign anything",
)

version = galtea.versions.create(
    product_id=product_id,
    description="Demo version for trace output files",
)
if version is None:
    raise ValueError("version from create is None")

session = galtea.sessions.create(version_id=version.id, is_production=True)
if session is None:
    raise ValueError("session from create is None")

# @start trace_with_output_file
trace = galtea.traces.create(
    session_id=session.id,
    input="Draft the lease agreement we discussed",
    output="Here is the draft you asked for.",
    output_file_paths=["path/to/lease-agreement.pdf"],
)
# @end trace_with_output_file
if not trace.actual_output_files:
    raise ValueError("the created trace carries no output file")
print(f"Attached {trace.actual_output_files[0].filename} ({trace.actual_output_files[0].mime_type})")

# @start trace_file_only
document_only = galtea.traces.create(
    session_id=session.id,
    input="Send me the signed copy",
    output_file_paths=["path/to/lease-agreement.pdf"],
)
# @end trace_file_only
if document_only.actual_output is not None:
    raise ValueError("a document-only answer should have no output text")
if not document_only.actual_output_files:
    raise ValueError("a document-only answer should carry a file")

# @start upload_output_file
lease = galtea.traces.upload_output_file("path/to/lease-agreement.pdf")

for question in ["Send me the lease again", "And a copy for my records"]:
    galtea.traces.create(
        session_id=session.id,
        input=question,
        output={"assistant_message": "Attached.", "content": [lease.model_dump(by_alias=True)]},
    )
# @end upload_output_file

reread = galtea.traces.get(trace.id)
if not reread.actual_output_files:
    raise ValueError("the stored trace lost its output file")
if reread.actual_output_data is None:
    raise ValueError("a file-carrying answer should keep its envelope")
print(f"Trace {reread.id} keeps {len(reread.actual_output_files)} output file(s)")

# === Cleanup ===
galtea.products.delete(product_id=product_id)
