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
        await asyncio.sleep(3)
        
        # Fill username and password
        await page.fill('input[name="username"]', 'fs123')
        await page.fill('input[name="password"]', 'fs123456')
        
        # Check for captcha image
        captcha_img = await page.query_selector('img.login-form-code-img')
        if captcha_img:
            print("Captcha found.")
            await captcha_img.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_captcha.png')
        else:
            print("No captcha found (at least not with that selector).")
            # Try to click login and see if it asks for captcha
            await page.click('button.login-submit')
            await asyncio.sleep(2)
            # Check for error or captcha now
            if await page.query_selector('text="验证码错误"'):
                print("Error: Needs captcha")
        
        await page.screenshot(path='/home/ubuntu/.openclaw/workspace/vnc_bt_login_attempt.png')
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
