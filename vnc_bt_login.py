import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        # Launching with headless=False so it shows up in VNC
        browser = await p.chromium.launch(
            headless=False, 
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        # Use a persistent context to "remember" login
        context = await p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.openclaw/workspace/chrome_vnc_profile',
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = context.pages[0]
        await page.goto('http://82.157.20.7:8888/fs123456')
        await asyncio.sleep(3)
        
        # Check if already logged in (look for logout button or similar)
        if await page.query_selector('text="退出"'):
            print("Already logged in.")
        else:
            # Baota panel login fields are usually visible
            # Let's try to fill them. 
            # Note: Baota uses different selectors depending on version.
            # Common ones: input[name="username"], input[name="password"]
            try:
                await page.fill('input[name="username"]', 'fs123')
                await page.fill('input[name="password"]', 'fs123456')
                
                # Look for the agreement checkbox if it exists
                agreement = await page.query_selector('.login-agreement input')
                if agreement:
                    await agreement.click()
                
                # Click login button
                await page.click('button.login-btn')
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Login attempt failed or fields not found: {e}")
                # Take a screenshot to debug
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_debug.png')
        
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_final.png')
        # Keep browser open for a bit to ensure it "remembers"
        await asyncio.sleep(2)
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
