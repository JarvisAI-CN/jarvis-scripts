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
        
        # Click Website
        await page.click('text="网站"')
        await asyncio.sleep(3)
        
        # Click Add Site
        await page.click('text="添加站点"')
        await asyncio.sleep(2)
        
        # Take screenshot of the dialog
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_dialog.png')
        
        # List all buttons and their texts
        elements = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"]')).map(e => ({
                tag: e.tagName,
                text: e.innerText || e.value,
                className: e.className,
                id: e.id
            }));
        }''')
        print(f"Elements: {elements}")
        
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
