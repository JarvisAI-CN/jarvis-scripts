#!/bin/bash
export DISPLAY=:1

# 1. Activate and focus window
WID=$(xdotool search --name "Google Chrome" | tail -1)
xdotool windowactivate --sync $WID
xdotool windowfocus --sync $WID
sleep 1

# 2. Click Account Field
# Window at (66, 32). Account field is around (460, 410) relative to screen.
xdotool mousemove 460 410 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type --delay 100 "fs123"
sleep 0.5

# 3. Tab to password
xdotool key Tab
sleep 0.5
xdotool type --delay 100 "fs123456"
sleep 0.5

# 4. Press Enter
xdotool key Return
sleep 15

# 5. Take screenshot of dashboard
python3 -c "import pyautogui; pyautogui.screenshot('/tmp/bt_dash_check.png')"
