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
            
            # Go to Software Store
            await page.click('text="软件商店"')
            await asyncio.sleep(5)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_software_check.png')
            
            # Search PHP 8.1
            await page.fill('#softSearch', 'PHP-8.1')
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(3)
            
            # Click settings
            await page.click('tr:has-text("PHP-8.1") a:has-text("设置")')
            await asyncio.sleep(3)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_settings.png')
            
            # Disabled Functions
            await page.click('text="禁用函数"')
            await asyncio.sleep(2)
            
            # Find and remove exec
            # The Baota 9.x+ uses a different list. 
            # I'll use a more generic way to find the delete button
            await page.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('tr'));
                for (const row of rows) {
                    if (row.innerText.includes('exec') && !row.innerText.includes('shell_exec')) {
                        const delBtn = row.querySelector('a:has-text("删除"), a[onclick*="Del")');
                        if (delBtn) delBtn.click();
                    }
                }
            }''')
            # Wait for confirm
            await asyncio.sleep(1)
            confirm = await page.query_selector('button:has-text("确定")')
            if confirm: await confirm.click()
            
            # Repeat for shell_exec
            await page.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('tr'));
                for (const row of rows) {
                    if (row.innerText.includes('shell_exec')) {
                        const delBtn = row.querySelector('a');
                        if (delBtn) delBtn.click();
                    }
                }
            }''')
            await asyncio.sleep(1)
            confirm = await page.query_selector('button:has-text("确定")')
            if confirm: await confirm.click()
            
            # Upload limit
            await page.click('text="上传限制"')
            await asyncio.sleep(2)
            await page.fill('input[name="file_size"]', '300')
            await page.click('button:has-text("保存")')
            await asyncio.sleep(1)
            
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_configured.png')
            await context.close()
            print("PHP Reconfigured successfully.")
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_error.png')

if __name__ == '__main__':
    asyncio.run(main())
