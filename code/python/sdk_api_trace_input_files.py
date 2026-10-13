"""
SDK API: Trace input files.
Logs turns that received a document, then reads the files back.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-input-files-{run_identifier}",
    description="Product that reads a document",
    capabilities="Read a lease agreement and answer questions about it",
    inabilities="Cannot sign anything",
)

version = galtea.versions.create(
    product_id=product_id,
    description="Demo version for trace input files",
)
if version is None:
    raise ValueError("version from create is None")

session = galtea.sessions.create(version_id=version.id, is_production=True)
if session is None:
    raise ValueError("session from create is None")

# @start trace_with_input_file
trace = galtea.traces.create(
    session_id=session.id,
    input="Who is the tenant in this lease agreement?",
    input_file_paths=["path/to/lease-agreement.pdf"],
    output="The tenant is Marta Ruiz.",
)
# @end trace_with_input_file
if len(trace.input_files) != 1:
    raise ValueError("the created trace should carry exactly one input file")
if "X-Amz-Signature" in trace.input_files[0].uri:
    raise ValueError("the stored input file should not keep the upload signature")
print(f"Attached {trace.input_files[0].filename} ({trace.input_files[0].mime_type})")

# @start trace_input_file_only
document_only = galtea.traces.create(
    session_id=session.id,
    input_file_paths=["path/to/lease-agreement.pdf"],
    output="This is a residential lease agreement.",
)
# @end trace_input_file_only
if len(document_only.input_files) != 1:
    raise ValueError("a document-only input should carry exactly one file")
if "X-Amz-Signature" in document_only.input_files[0].uri:
    raise ValueError("the stored input file should not keep the upload signature")

# === Cleanup ===
galtea.products.delete(product_id=product_id)
