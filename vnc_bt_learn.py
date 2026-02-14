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
        
        # Click "软件商店" (Software Store)
        try:
            await page.click('text="软件商店"')
            await asyncio.sleep(5)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_software_store.png')
            
            # Search for "Python"
            await page.fill('#softSearch', 'Python')
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(3)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_python_search.png')
            
            # Click "网站" -> "Python项目" (if it exists)
            await page.click('text="网站"')
            await asyncio.sleep(2)
            # Check if there is a "Python项目" tab
            tabs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.tab-nav-item')).map(t => t.innerText);
            }''')
            print(f"Website Tabs: {tabs}")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_website_tabs.png')
            
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
