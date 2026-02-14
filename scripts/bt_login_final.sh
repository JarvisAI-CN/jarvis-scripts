#!/bin/bash
export DISPLAY=:1

# 1. Activate and focus window
WID=$(xdotool search --name "Google Chrome" | tail -1)
xdotool windowactivate --sync $WID
xdotool windowfocus --sync $WID
sleep 1

# 2. Close dialogs
xdotool key Escape
sleep 0.5
xdotool key Escape
sleep 0.5

# 3. Click and clear account field
# Relative to window (1200x800) at (66,32):
# Center is (600, 400)
# Account field roughly (600, 350)
# Absolute: (666, 382)
xdotool mousemove 666 382 click 1
sleep 0.5
xdotool key control+a
xdotool key BackSpace
xdotool key control+a
xdotool key Delete
sleep 0.5

# 4. Type username slowly
xdotool type --delay 150 "fs123"
sleep 1

# 5. Tab to password
xdotool key Tab
sleep 0.5
xdotool key control+a
xdotool key BackSpace
sleep 0.5
xdotool type --delay 150 "fs123456"
sleep 1

# 6. Press Enter
xdotool key Return
sleep 10

# 7. Take screenshot
python3 -c "import pyautogui; pyautogui.screenshot('/tmp/vnc_screen_bt_login_final.png')"
