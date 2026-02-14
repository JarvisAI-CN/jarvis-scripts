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
        await page.goto('http://82.157.20.7:8888/files')
        await asyncio.sleep(5)
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_success.png', full_page=True)
        print(f"Logged in title: {await page.title()}")
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
