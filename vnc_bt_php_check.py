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
            # Click Software Store
            await page.click('text="软件商店"')
            await asyncio.sleep(3)
            
            # Click "已安装" (Installed)
            await page.click('text="已安装"')
            await asyncio.sleep(2)
            
            # Find PHP version (e.g., PHP-8.1)
            # Click "设置" (Settings) for PHP
            php_setting = await page.query_selector('tr:has-text("PHP-") a:has-text("设置")')
            if php_setting:
                await php_setting.click()
                await asyncio.sleep(2)
                
                # Click "禁用函数" (Disabled Functions)
                await page.click('text="禁用函数"')
                await asyncio.sleep(2)
                
                # Check for exec, shell_exec, proc_open
                disabled_functions = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('.disabled-functions-list span')).map(s => s.innerText);
                }''')
                print(f"Disabled Functions: {disabled_functions}")
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_disabled.png')
                
                # If exec is disabled, remove it
                # (I won't do it yet, just learning)
            else:
                print("PHP setting not found in Installed list.")
                
        except Exception as e:
            print(f"Error: {e}")
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
