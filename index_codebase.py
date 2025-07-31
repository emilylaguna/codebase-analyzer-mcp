import asyncio
from fastmcp import Client

async def main():
    async with Client("main.py") as client:
        result = await client.call_tool("index_codebase", {"path": "/Users/emilylaguna/Desktop/Personal/Shooting/Grids", "project_id": "test"})
        print(result)
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())