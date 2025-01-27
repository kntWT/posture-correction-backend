import sys
import asyncio
from scripts.estimate import estimate
from scripts.export_openapi import export_openapi_scheme
from configs.env import image_dir

if __name__ == "__main__":
    operation = sys.argv[1]
    if operation == "openapi":
        export_openapi_scheme()
    elif operation == "estimate":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(estimate(f"images", "0", sys.argv[2]))
