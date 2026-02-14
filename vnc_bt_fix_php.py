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
            # Search for PHP in the top search box or Software Store
            await page.click('text="软件商店"')
            await asyncio.sleep(3)
            
            # Fill search box
            # Baota search box id is often 'softSearch'
            await page.fill('#softSearch', 'PHP-8.1')
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(3)
            
            # Click "设置" (Settings)
            # The row for PHP-8.1
            await page.click('tr:has-text("PHP-8.1") a:has-text("设置")')
            await asyncio.sleep(3)
            
            # Click "禁用函数"
            await page.click('text="禁用函数"')
            await asyncio.sleep(2)
            
            # Find 'exec' in the list and click '删除' (Delete) next to it
            # The list usually contains spans or table cells
            exec_item = await page.query_selector('tr:has-text("exec") a:has-text("删除")')
            if exec_item:
                await exec_item.click()
                await asyncio.sleep(1)
                # Confirm deletion if there's a prompt
                confirm_btn = await page.query_selector('button:has-text("确定")')
                if confirm_btn:
                    await confirm_btn.click()
                print("Deleted 'exec' from disabled functions.")
            
            # Also delete 'shell_exec'
            shell_exec_item = await page.query_selector('tr:has-text("shell_exec") a:has-text("删除")')
            if shell_exec_item:
                await shell_exec_item.click()
                await asyncio.sleep(1)
                confirm_btn = await page.query_selector('button:has-text("确定")')
                if confirm_btn:
                    await confirm_btn.click()
                print("Deleted 'shell_exec' from disabled functions.")

            # Take final screenshot
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_fixed.png')
                
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_fix_error.png')
            
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
