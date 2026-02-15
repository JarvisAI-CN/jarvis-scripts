#!/bin/bash
export DISPLAY=:1

# Clear username
xdotool mousemove 450 525 click 1
xdotool key ctrl+a BackSpace
xdotool type "fs123"

# Clear password
xdotool key Tab
xdotool key ctrl+a BackSpace
xdotool type "fs123456"

# Type captcha
xdotool key Tab
# I need a fresh captcha. I'll take a screenshot and then the user can tell me or I'll guess.
