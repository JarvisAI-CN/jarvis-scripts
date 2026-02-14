#!/bin/bash
export DISPLAY=:1

# 1. Activate window
xdotool windowactivate 27262980
sleep 1

# 2. Click Account Field (Absolute coordinates based on geometry)
xdotool mousemove 666 382 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123"
sleep 0.5

# 3. Click Password Field
xdotool mousemove 666 452 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123456"
sleep 0.5

# 4. Click Green Login Button
xdotool mousemove 666 582 click 1
sleep 10

# 5. Take screenshot
python3 -c "import pyautogui; pyautogui.screenshot('/tmp/vnc_screen_bt_login_step7.png')"
