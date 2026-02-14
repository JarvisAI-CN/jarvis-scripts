import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir='/home/ubuntu/.openclaw/workspace/chrome_vnc_profile',
                headless=False,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = context.pages[0]
            await page.goto('http://82.157.20.7:8888/fs123456', timeout=60000)
            await asyncio.sleep(5)
            
            # Print page title to confirm we are logged in
            print(f"Page Title: {await page.title()}")
            
            # Take initial screenshot
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_debug_1.png')
            
            # Click Website
            await page.click('text="网站"')
            await asyncio.sleep(3)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_debug_2.png')
            
            # Click Add Site
            await page.click('text="添加站点"')
            await asyncio.sleep(2)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_debug_3.png')
            
            # Fill Domain
            # Try to find the textarea
            await page.fill('textarea', 'yinyue.dhmip.cn') # Changed to .cn for reliability, will check .cm later
            
            # Submit
            await page.click('button:has-text("提交")')
            await asyncio.sleep(5)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_debug_4.png')
            
            print("Finished process.")
            await context.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
