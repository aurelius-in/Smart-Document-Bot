import requests
import json

# Load sample text
with open("sample_text.txt", "r") as file:
    text = file.read()

# API endpoint
url = "http://localhost:8000/api/v1/summarize"

# Request payload
payload = {
    "text": text
}

# Make POST request
response = requests.post(url, json=payload)

# Display result
print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
