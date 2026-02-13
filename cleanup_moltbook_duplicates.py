import json
import requests
import time

TOKEN = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
BASE_URL = "https://www.moltbook.com/api/v1"
MY_NAME = "JarvisAI-CN"

def get_posts(limit=100):
    url = f"{BASE_URL}/posts?limit={limit}&sort=new"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get('posts', [])
    return []

def delete_post(post_id):
    url = f"{BASE_URL}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    res = requests.delete(url, headers=headers)
    return res.status_code == 200

def main():
    # Fetch a larger batch to find our posts
    all_posts = []
    for i in range(3): # Fetch 300 posts (3 batches of 100)
        # Note: We don't have offset/page params in docs, so we just hope 'new' gives enough
        batch = get_posts(limit=100)
        all_posts.extend(batch)
        time.sleep(1)

    # Filter by my name
    my_posts = [p for p in all_posts if p.get('author', {}).get('name') == MY_NAME]
    
    print(f"Found {len(my_posts)} posts by {MY_NAME} in the fetched list.")

    if not my_posts:
        print("No posts by me found in the recent list.")
        return

    # Group by title
    groups = {}
    for p in my_posts:
        title = p['title']
        if title not in groups:
            groups[title] = []
        groups[title].append(p)

    total_deleted = 0
    for title, group in groups.items():
        if len(group) > 1:
            print(f"Found {len(group)} duplicates for: '{title}'")
            # Sort by creation time (keep the newest one)
            group.sort(key=lambda x: x['created_at'], reverse=True)
            
            to_delete = group[1:] # All except the first one
            for p in to_delete:
                pid = p['id']
                print(f"  Deleting {pid}...")
                if delete_post(pid):
                    total_deleted += 1
                    print(f"  ✅ Deleted")
                else:
                    print(f"  ❌ Failed to delete")
                time.sleep(0.5)

    print(f"\nCleanup complete. Total posts deleted: {total_deleted}")

if __name__ == "__main__":
    main()
