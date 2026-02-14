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
        
        try:
            # Go to Website
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # List all domains in the table
            domains = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[onclick*="WebEdit"]')).map(a => a.innerText);
            }''')
            print(f"Domains: {domains}")
            
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_all_sites.png')
                
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
