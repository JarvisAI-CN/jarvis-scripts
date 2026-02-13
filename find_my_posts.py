import requests
import time

TOKEN = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
BASE_URL = "https://www.moltbook.com/api/v1"
MY_NAME = "JarvisAI-CN"

def main():
    found_posts = []
    # We don't have offset, so we just fetch multiple times and hope for the best
    # or check if there's an 'offset' or 'page' parameter not in docs
    for i in range(10): 
        url = f"{BASE_URL}/posts?limit=100&sort=new"
        # Wait, if there's no offset, we just get the same 100 posts every time!
        # Let's try adding offset=... just in case
        url = f"{BASE_URL}/posts?limit=100&sort=new&offset={i*100}"
        
        headers = {"Authorization": f"Bearer {TOKEN}"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            posts = res.json().get('posts', [])
            batch_my_posts = [p for p in posts if p.get('author', {}).get('name') == MY_NAME]
            found_posts.extend(batch_my_posts)
            print(f"Batch {i}: Found {len(batch_my_posts)} posts by me (Total: {len(found_posts)})")
            if posts:
                print(f"  First post date: {posts[0]['created_at']}")
        else:
            print(f"Batch {i} failed: {res.status_code}")
        time.sleep(0.5)

    if found_posts:
        print(f"\nTotal posts by me found: {len(found_posts)}")
        for p in found_posts:
            print(f"- {p['id']} [{p['created_at']}] {p['title']}")
    else:
        print("\nNo posts by me found.")

if __name__ == "__main__":
    main()
