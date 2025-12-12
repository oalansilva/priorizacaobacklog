import json

with open("response.json", "r") as f:
    data = json.load(f)

# output from lambda invoke is pure body string in this case?
# No, it's a structure with StatusCode, etc. IF I didn't verify raw-in-base64-out
# But I suspect response.json contains the lambda result payload.
# Mangum returns an API Gateway response: { "statusCode": 200, "body": "...", ... }

print("Raw keys:", data.keys())

if "body" in data:
    body = data["body"]
    try:
        roadmaps = json.loads(body)
        print(f"Found {len(roadmaps)} roadmaps.")
        if len(roadmaps) > 0:
            print(f"First ID: '{roadmaps[0]['id']}'")
            # Save it to a file
            with open("roadmap_id.txt", "w") as out:
                out.write(roadmaps[0]['id'])
        else:
            print("No roadmaps found.")
    except Exception as e:
        print(f"Error parsing body: {e}")
        print("Body sample:", body[:100])
else:
    print("No body in response")
    print(data)
