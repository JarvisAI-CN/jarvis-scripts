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
            
            # Go to Website to check PHP version
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # Click on yinyue.dhmip.cn to open settings
            await page.click('text="yinyue.dhmip.cn"')
            await asyncio.sleep(3)
            
            # Get PHP version
            await page.click('text="PHP版本"')
            await asyncio.sleep(2)
            php_version = await page.evaluate('document.querySelector(".php_version_select").value')
            print(f"Site is using PHP version: {php_version}")
            
            # Close site settings
            await page.click('.layui-layer-close')
            await asyncio.sleep(1)
            
            # Go to Software Store
            await page.click('text="软件商店"')
            await asyncio.sleep(3)
            
            # Search for the PHP version
            await page.fill('#softSearch', f'PHP-{php_version[:1]}.{php_version[1:]}') # e.g. 81 -> 8.1
            await page.press('#softSearch', 'Enter')
            await asyncio.sleep(2)
            
            # Open PHP settings
            await page.click(f'tr:has-text("PHP-{php_version[:1]}.{php_version[1:]}") a:has-text("设置")')
            await asyncio.sleep(3)
            
            # 1. Enable functions
            await page.click('text="禁用函数"')
            await asyncio.sleep(2)
            for func in ['exec', 'shell_exec', 'system', 'passthru']:
                del_btn = await page.query_selector(f'tr:has-text("{func}") a:has-text("删除")')
                if del_btn:
                    await del_btn.click()
                    await asyncio.sleep(1)
                    await page.click('button:has-text("确定")')
                    print(f"Enabled function: {func}")
            
            # 2. Increase upload limit
            await page.click('text="上传限制"')
            await asyncio.sleep(2)
            await page.fill('.bt-input-text[name="file_size"]', '300')
            await page.click('button:has-text("保存")')
            print("Increased upload limit to 300MB.")
            
            # 3. Increase max execution time (for large files)
            await page.click('text="配置修改"')
            await asyncio.sleep(2)
            # This is harder via UI textarea, but let's try 'max_execution_time'
            # Or just use "性能调整" tab if it exists
            perf_tab = await page.query_selector('text="性能调整"')
            if perf_tab:
                await perf_tab.click()
                await asyncio.sleep(2)
                await page.fill('input[name="max_execution_time"]', '300')
                await page.fill('input[name="memory_limit"]', '512')
                await page.click('button:has-text("保存")')
                print("Adjusted performance settings.")
            
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_php_config_done.png')
            await context.close()
        except Exception as e:
            print(f"Error during Baota re-config: {e}")

if __name__ == '__main__':
    asyncio.run(main())
