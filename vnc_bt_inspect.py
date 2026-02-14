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
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(i => ({
                name: i.name,
                type: i.type,
                placeholder: i.placeholder,
                className: i.className
            }));
        }''')
        print(f"Inputs: {inputs}")
        
        # Look for login button
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.innerText,
                className: b.className
            }));
        }''')
        print(f"Buttons: {buttons}")
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
