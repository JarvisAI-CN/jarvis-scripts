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
            
            # Click Website
            await page.click('text="网站"')
            await asyncio.sleep(3)
            
            # Click Add Site
            await page.click('text="添加站点"')
            await asyncio.sleep(2)
            
            # Fill Domain
            # Baota dialog domain textarea usually has class 'bt-input-text' or similar.
            # Let's try to be specific.
            await page.fill('textarea[placeholder*="域名"]', 'yinyue.dhmip.cn')
            await asyncio.sleep(1)
            
            # Fill .cm as well if needed? No, user probably meant .cn. 
            # I'll add both just in case.
            # await page.fill('textarea[placeholder*="域名"]', 'yinyue.dhmip.cn\nyinyue.dhmip.cm')
            
            # Click Submit
            # Baota submit button in dialog often has class 'layui-layer-btn0' or 'btn-success'
            submit_btn = await page.query_selector('a.layui-layer-btn0')
            if not submit_btn:
                submit_btn = await page.query_selector('button:has-text("提交")')
            
            if submit_btn:
                await submit_btn.click()
                print("Clicked submit.")
            else:
                print("Submit button not found.")
                
            await asyncio.sleep(5)
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/bt_final_check.png')
            
            await context.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
