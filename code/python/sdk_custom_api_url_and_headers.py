import os

from galtea import Galtea

# @start custom_api_url_and_headers
galtea = Galtea(
    api_key="YOUR_API_KEY",
    base_url=os.environ["GALTEA_API_URL"],  # for example, your API gateway URL
    headers={"X-IBM-Client-Id": "YOUR_CLIENT_ID"},
)
# @end custom_api_url_and_headers
