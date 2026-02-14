#!/bin/bash
export DISPLAY=:1

# 1. Activate window
xdotool windowactivate 27262980
sleep 1

# 2. Close restore dialog (click 'x' at 639 122)
xdotool mousemove 639 122 click 1
sleep 1

# 3. Click Account Field and Type
xdotool mousemove 345 425 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123"
sleep 1

# 4. Click Password Field and Type
xdotool mousemove 345 475 click 1
sleep 0.5
xdotool key ctrl+a BackSpace
sleep 0.5
xdotool type "fs123456"
sleep 1

# 5. Click Login Button
xdotool mousemove 345 580 click 1
sleep 10

# 6. Take screenshot
import -window root /tmp/vnc_screen_xdotool.png
