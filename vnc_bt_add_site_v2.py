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
        
        # Click on "网站"
        await page.click('.menu-item:has-text("网站")')
        await asyncio.sleep(3)
        
        # Click "添加站点"
        await page.click('button:has-text("添加站点")')
        await asyncio.sleep(2)
        
        # Fill domain
        await page.fill('textarea.bt-input-text', 'yinyue.dhmip.cm')
        
        # Submit
        await page.click('button[name="submit"]')
        await asyncio.sleep(5)
        
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_site_attempt_2.png')
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
