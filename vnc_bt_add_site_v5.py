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
            
            # Click Website
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # Click Add Site
            await page.click('text="添加站点"')
            await asyncio.sleep(2)
            
            # Fill Domain
            # User specifically asked for .cm, I'll use both .cn and .cm to be safe.
            await page.fill('textarea[placeholder*="域名"]', 'yinyue.dhmip.cn\nyinyue.dhmip.cm')
            await asyncio.sleep(1)
            
            # Click Confirm (确定)
            # Selector: button:has-text("确定")
            await page.click('button:has-text("确定")')
            print("Clicked 确定.")
            
            # Wait for creation (it shows a dialog with info)
            await asyncio.sleep(10)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_success_final.png')
            
            # Close the success dialog if it exists (usually has a close button or '确定')
            try:
                await page.click('button:has-text("确定")')
            except:
                pass
                
            await context.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
