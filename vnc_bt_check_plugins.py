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
            # Click "软件商店"
            await page.click('text="软件商店"')
            await asyncio.sleep(3)
            
            # Search for "项目管理器"
            await page.fill('#softSearch', '项目管理器')
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(3)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_project_manager_search.png')
            
            # Check for Python项目管理器
            # (In some versions it is a separate plugin)
            await page.fill('#softSearch', 'Python项目管理器')
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(3)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_python_manager_search.png')
            
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
