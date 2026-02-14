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
            # Go to Website -> PHP Project
            await page.click('text="网站"')
            await asyncio.sleep(2)
            
            # Find the site yinyue.dhmip.cn
            site_row = await page.query_selector('tr:has-text("yinyue.dhmip.cn")')
            if site_row:
                # Click on the site name to open settings
                await page.click('text="yinyue.dhmip.cn"')
                await asyncio.sleep(3)
                
                # Check current PHP version for this site
                php_ver_text = await page.evaluate('''() => {
                    return document.querySelector("#webedit-con").innerText;
                }''')
                print(f"Site Settings Content: {php_ver_text[:200]}")
                
                # Usually there's a "PHP版本" tab in site settings
                await page.click('text="PHP版本"')
                await asyncio.sleep(2)
                
                current_version = await page.evaluate('''() => {
                    return document.querySelector(".php_version_select").value;
                }''')
                print(f"Current PHP Version for site: {current_version}")
                
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_site_php_version.png')
            else:
                print("Site yinyue.dhmip.cn not found.")
                
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
