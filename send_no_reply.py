#!/usr/bin/env python3
import subprocess
import sys

cmd = [
    "openclaw", "message", "send",
    "--channel", "feishu",
    "--account", "main",
    "--target", "ou_5f1c95e17c1b9d8f679c500e8864999f",
    "--message", "NO_REPLY"
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("SUCCESS: Message sent")
    sys.exit(0)
else:
    print(f"ERROR: {result.stderr}")
    sys.exit(1)
