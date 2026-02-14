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
        
        await page.click('text="软件商店"')
        await asyncio.sleep(5)
        
        # Get all rows in the software table
        rows = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('tr')).map(r => r.innerText);
        }''')
        print(f"Software Rows: {rows}")
        
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
