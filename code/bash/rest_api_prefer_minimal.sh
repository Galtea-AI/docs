curl -X PATCH "https://api.galtea.ai/products/prod_123" \
  -H "Authorization: Bearer $GALTEA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d '{"tags": ["support"]}'
