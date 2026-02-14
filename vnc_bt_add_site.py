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
        await page.goto('http://82.157.20.7:8888/fs123456')
        await asyncio.sleep(5)
        
        # Click on "Website" (网站) menu
        # The selector might vary, usually it's an 'a' with text '网站' or similar.
        try:
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # Click "Add Site" (添加站点)
            await page.click('text="添加站点"')
            await asyncio.sleep(2)
            
            # Fill domain yinyue.dhmip.cn
            # Baota dialog usually has a textarea for domains.
            await page.fill('textarea[name="webname"]', 'yinyue.dhmip.cn')
            
            # Keep other defaults (PHP version, document root etc.)
            # Click "Submit" (提交)
            await page.click('.btn-success:has-text("提交")')
            await asyncio.sleep(5)
            
            print("Site creation attempt finished.")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_site_added.png')
        except Exception as e:
            print(f"Error during Baota operation: {e}")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_error.png')
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
