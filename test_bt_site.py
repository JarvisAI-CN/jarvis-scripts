import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    # Use the persistent profile where I'm already logged into Baota if needed (though the site is public)
    # But for a fresh test, just a regular launch is fine.
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = await browser.new_page()
        
        test_url = 'http://yinyue.dhmip.cn'
        file_path = '/home/ubuntu/123pan/共享资源/梓渝 - 萤火星球.ncm'
        
        print(f"Navigating to {test_url}...")
        try:
            await page.goto(test_url, timeout=60000)
            await asyncio.sleep(2)
            
            print(f"Uploading file: {file_path}")
            # The input has id="fileInput"
            await page.set_input_files('#fileInput', file_path)
            await asyncio.sleep(1)
            
            print("Clicking Start Conversion button...")
            # The button has id="submitBtn"
            await page.click('#submitBtn')
            
            # Wait for result
            # The message area has id="message" and gains "active" class
            # Successful conversion triggers window.location.href change or message update
            print("Waiting for conversion results (up to 120s)...")
            
            # We wait for the success message or a download trigger
            # In the code, successful conversion sets window.location.href = data.downloadUrl
            # We can check if URL changed or if an error message appeared
            try:
                await page.wait_for_selector('.message.success.active', timeout=120000)
                print("Success message detected!")
                # Check for download trigger URL change
                await asyncio.sleep(2)
                print(f"Final URL after conversion: {page.url}")
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/test_conversion_success.png')
            except Exception as e:
                # Check for error message
                error_msg = await page.query_selector('.message.error.active')
                if error_msg:
                    text = await error_msg.inner_text()
                    print(f"Conversion failed with message: {text}")
                else:
                    print(f"Timeout or unexpected state: {e}")
                await page.screenshot(path='/home/ubuntu/.openclaw/workspace/test_conversion_failed.png')
                
        except Exception as e:
            print(f"Error during test: {e}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
