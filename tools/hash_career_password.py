#!/usr/bin/env python3
import sys
from portal.server import password_hash
if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 tools/hash_career_password.py '<password>'")
print(password_hash(sys.argv[1]))
