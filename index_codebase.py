import asyncio
from fastmcp import Client
import json
import uuid
async def main():
    async with Client("main.py") as client:
        random_uuid = str(uuid.uuid4())
        result = await client.call_tool("index_codebase", {"path": "./test_codebase", "project_id": random_uuid})
        print(json.dumps(result.data, indent=4))
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())