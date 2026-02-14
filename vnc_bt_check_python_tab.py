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
            # Click "网站" (Website)
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # Check for tabs like "PHP项目", "Python项目"
            tabs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.tab-nav-item, .bt-menu p')).map(t => t.innerText);
            }''')
            print(f"Tabs/Menu: {tabs}")
            
            # Click "Python项目"
            python_tab = await page.query_selector('text="Python项目"')
            if python_tab:
                await python_tab.click()
                await asyncio.sleep(3)
                print("Clicked Python项目 tab.")
                
                # Check for "添加Python项目" (Add Python Project)
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_python_project.png')
            else:
                print("Python项目 tab not found in Website section.")
                
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
