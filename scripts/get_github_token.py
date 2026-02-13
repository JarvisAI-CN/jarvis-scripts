#!/usr/bin/env python3
import re
import os

PASSWORDS_FILE = "/home/ubuntu/.openclaw/workspace/PASSWORDS.md"

def get_token():
    if not os.path.exists(PASSWORDS_FILE):
        return None
    with open(PASSWORDS_FILE, "r") as f:
        content = f.read()
        # Look for the token pattern ghp_...
        match = re.search(r"ghp_[a-zA-Z0-9]{36}", content)
        if match:
            return match.group(0)
    return None

if __name__ == "__main__":
    token = get_token()
    if token:
        print(token)
