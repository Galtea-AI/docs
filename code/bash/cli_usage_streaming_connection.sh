# List the presets, with the stream format and settings of each one
galtea endpoint-connections list-stream-presets

# Create the connection from the JSON body above
galtea endpoint-connections create < streaming-connection.json

# Try a preset on the saved connection before you change it
galtea endpoint-connections test id: YOUR_CONNECTION_ID, streamFormat: SSE, streamAssembly.preset: OPENAI_CHAT_COMPLETIONS

# Turn streaming off again: the agent answers with one JSON reply
galtea endpoint-connections update YOUR_CONNECTION_ID streamFormat: null, streamAssembly: null
