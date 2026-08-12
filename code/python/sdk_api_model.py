"""
SDK API: Model
Demonstrates how to create, list, get, update, and delete models,
and how to link a model to a version for cost tracking.
"""

from datetime import datetime

from _test_helpers import create_test_product

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

_demo_product_id = create_test_product(
    galtea,
    name="Model Linking Demo " + run_identifier,
    description="Demo product used to showcase how to link a Model to a Version for cost tracking.",
    capabilities="* Demonstrates the models -> versions linking pattern",
    inabilities="* Anything outside the model-linking demo",
)

# @start create
model = galtea.models.create(
    name="gpt-5.5-pro " + run_identifier,
    input_cost_per_token=0.00001,
    output_cost_per_token=0.00003,
    cache_read_input_token_cost=0.000005,
    cache_creation_input_token_cost=0.0000125,
    tokenizer_provider="OpenAI",
    source="https://openai.com/api/pricing/",
)
# @end create

if model is None:
    raise ValueError("model is None")

model_id = model.id
model_name = model.name

# @start list
models = galtea.models.list(
    sort_by_created_at="desc",
    limit=10,
)
# @end list

# @start get
model = galtea.models.get(model_id=model_id)
# @end get

# @start get_by_name
model = galtea.models.get_by_name(name=model_name)
# @end get_by_name

# @start update
model = galtea.models.update(
    model_id=model_id,
    input_cost_per_token=0.000015,
    output_cost_per_token=0.000035,
)
# @end update

# @start link_to_version
# Look up an existing model by name (created earlier via galtea.models.create).
selected_model = galtea.models.get_by_name(name=model_name)

# Pass its id to versions.create so Galtea can track cost for this version's
# traces using the model's per-token pricing.
version = galtea.versions.create(
    name="v1.0-with-model-" + run_identifier,
    product_id=_demo_product_id,
    model_id=selected_model.id,
    description="Version linked to a model for cost tracking.",
)
# @end link_to_version

# @start delete
galtea.models.delete(model_id=model_id)
# @end delete
