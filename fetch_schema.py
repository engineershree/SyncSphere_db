import urllib.request
import json

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/v1/openapi.json')
    data = json.loads(response.read().decode('utf-8'))
    with open('openapi_schema.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Successfully fetched OpenAPI schema")
except Exception as e:
    print(f"Error: {e}")
