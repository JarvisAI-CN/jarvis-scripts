import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.openclaw/workspace/chrome_vnc_profile',
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = context.pages[0]
        await page.goto('http://82.157.20.7:8888/fs123456')
        await asyncio.sleep(5)
        
        # Fill username and password
        await page.fill('input[name="username"]', 'fs123')
        await page.fill('input[name="password"]', 'fs123456')
        
        # Click login
        await page.click('button.login-submit')
        await asyncio.sleep(5)
        
        # Check URL
        print(f"Final URL: {page.url}")
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_login_final.png', full_page=True)
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
