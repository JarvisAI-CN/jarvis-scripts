import requests

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"

post_ids = [
    # Post 14 placeholders
    "ace9dae7-5d67-4c1a-8a5b-ebca16f4ccef",
    "39783a97-6105-44f8-a42f-f766138546d2",
    "3c0f4dd8-7b7a-4148-848a-0eb96f68e0ce",
    "1b3dc49d-9286-4d3b-ade6-9d200e7a99fb",
    "985353da-6b2a-41d6-91f3-724b101d509a",
    # Post 3-12 placeholders
    "120284e6-c0da-41e4-a3bb-97dd90aee0e1",
    "0e01c869-2ebd-4db4-ac63-13d8f77a60b4",
    "70967145-663b-43b7-8add-68211bca5b80",
    "c9e0b5d2-7cb2-4232-9cc4-7d0af2febab1",
    "99ea68e2-0576-40a5-92a0-5faf6f0b89ee",
    "1e44dcb6-3b97-4c56-9333-e7bcb5b22776",
    "ccac09e0-8f63-4dfe-b749-d5ba9582a2f3"
]

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

for pid in post_ids:
    url = f"{API_BASE}/posts/{pid}"
    print(f"Deleting post {pid}...")
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Deleted {pid}")
        else:
            print(f"❌ Failed to delete {pid}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception deleting {pid}: {e}")
