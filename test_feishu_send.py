#!/usr/bin/env python3
import subprocess
import sys

# Test with explicit parameters
cmd = [
    "openclaw", "message", "send",
    "--channel", "feishu",
    "--account", "main",
    "--target", "ou_5f1c95e17c1b9d8f679c500e8864999f",
    "--message", "TEST_MESSAGE_FROM_PYTHON"
]

print(f"Running command: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"STDOUT:\n{result.stdout}")
print(f"STDERR:\n{result.stderr}")
sys.exit(result.returncode)
