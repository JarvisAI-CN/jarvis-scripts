from PIL import Image
img = Image.open('/home/ubuntu/.openclaw/workspace/bt_final_attempt.png')
# Crop around the captcha area
# Captcha input is approx (280, 525)
# Error text is below it
crop = img.crop((200, 480, 500, 620))
crop.save('/home/ubuntu/.openclaw/workspace/bt_captcha_crop.png')
