import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.openclaw/workspace/chrome_vnc_profile',
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = context.pages[0]
        try:
            await page.goto('http://82.157.20.7:8888/fs123456', timeout=30000)
            await asyncio.sleep(5)
            content = await page.content()
            print(f"Content length: {len(content)}")
            print(f"Title: {await page.title()}")
            # Print a snippet of content
            print(f"Snippet: {content[:500]}")
        except Exception as e:
            print(f"Error: {e}")
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
