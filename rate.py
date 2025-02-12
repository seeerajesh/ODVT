import json

with open("/Users/admin/Downloads/solid-scheme-450717-q8-f5d059394adf.json", "r") as file:
    creds = json.load(file)

print(json.dumps(creds))  # Copy this output for GitHub Secret
