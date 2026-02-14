#!/bin/bash
export DISPLAY=:1

# 1. Activate window
xdotool windowactivate 0x1a00004
sleep 1

# 2. Dismiss Chrome popups
xdotool key Escape
sleep 0.5
xdotool key Escape
sleep 0.5

# 3. Click Account and Type
xdotool mousemove 599 429 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123"
sleep 1

# 4. Click Password and Type
xdotool mousemove 599 484 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123456"
sleep 1

# 5. Click Captcha and Type
xdotool mousemove 478 584 click 1
sleep 0.5
xdotool type "EmkG"
sleep 1

# 6. Click Login
xdotool mousemove 599 637 click 1
sleep 10

# 7. Take screenshot
python3 -c "import pyautogui; pyautogui.screenshot('/tmp/vnc_bt_login_result.png')"
