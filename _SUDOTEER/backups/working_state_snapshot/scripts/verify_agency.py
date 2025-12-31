import asyncio
import json
import logging
from backend.agency import main

# Mock sys.argv for testing
import sys
sys.argv = ["agency.py", json.dumps({"command": "Implement a secure login function in Python with tab indentation"})]

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
	print("Starting Agency Verification Pipe...")
	asyncio.run(main())
