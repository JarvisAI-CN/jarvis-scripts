import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.environ['DISPLAY'] = ':1'
    async with async_playwright() as p:
        # Use headless=False to interact properly with display :1
        browser = await p.chromium.launch(headless=False, args=['--no-sandbox'])
        page = await browser.new_page()
        
        test_url = 'http://yinyue.dhmip.cn'
        file_path = '/home/ubuntu/123pan/共享资源/梓渝 - 萤火星球.ncm'
        
        print(f"Navigating to {test_url}...")
        try:
            await page.goto(test_url, timeout=60000)
            await asyncio.sleep(5)
            
            print(f"Uploading file: {file_path}")
            # Ensure the input is ready
            await page.set_input_files('input[name="ncm_file"]', file_path)
            await asyncio.sleep(2)
            
            # Check if file name is displayed
            file_name_display = await page.inner_text('#fileName')
            print(f"File selected: {file_name_display}")
            
            print("Clicking Start Conversion button...")
            await page.click('#submitBtn')
            
            # Wait for message to appear
            print("Waiting for conversion results...")
            for i in range(60): # 120 seconds total
                await asyncio.sleep(2)
                msg = await page.inner_text('#message')
                if msg:
                    print(f"Current message: {msg}")
                    if "成功" in msg:
                        print("Test passed!")
                        break
                    if "失败" in msg or "错误" in msg:
                        print("Test failed with error message.")
                        break
                # Also check URL
                if "download.php" in page.url:
                    print("URL redirected to download. Success!")
                    break
            
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/test_final_result.png')
            print(f"Final URL: {page.url}")
                
        except Exception as e:
            print(f"Error during test: {e}")
            await page.screenshot(path='/home/ubuntu/.openclaw/workspace/test_error.png')
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
