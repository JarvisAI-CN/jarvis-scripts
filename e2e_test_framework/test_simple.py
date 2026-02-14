#!/usr/bin/env python3
"""
Simple test to verify framework works without complex imports.
"""

import sys
import os

# Change to framework directory
os.chdir('/home/ubuntu/.openclaw/workspace/e2e_test_framework')
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/e2e_test_framework')

# Now try importing as package
try:
    # This will trigger all imports
    import core.assertions as assertions
    import core.case as case
    import core.runner as runner

    print("✅ All modules imported successfully\n")

    # Test assertions
    print("Testing assertions...")
    assertions.expect(1 + 1).to_eq(2)
    print("  ✓ Basic assertion works")

    assertions.expect("hello").to_contain("ell")
    print("  ✓ String assertion works")

    assertions.expect([1, 2, 3]).to_have_length(3)
    print("  ✓ Collection assertion works")

    assertions.expect(10).to_be_gt(5)
    print("  ✓ Numeric assertion works")

    assertions.expect(5).not_().to_eq(10)
    print("  ✓ Negation works")

    print("\n✅ All import tests passed!")

    print("\n" + "="*50)
    print("Framework is ready to use!")
    print("="*50)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
