import json
import base64

with open("pdf_response_2.json", "r") as f:
    data = json.load(f)

if "body" in data and data.get("isBase64Encoded"):
    pdf_content = base64.b64decode(data["body"])
    output_path = r"C:\Users\alans.triggo\.gemini\antigravity\brain\d1331005-a534-4aae-8385-3bd6ae621c9d\debug_roadmap.pdf"
    with open(output_path, "wb") as pdf_file:
        pdf_file.write(pdf_content)
    print(f"PDF recovered to {output_path}")
else:
    print("No base64 body found.")
