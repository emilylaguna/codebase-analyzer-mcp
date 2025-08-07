import asyncio
from main import startup, index_codebase_manual, IndexCodebaseInput

async def main():
    await startup()
    result = await index_codebase_manual(
        input_data=IndexCodebaseInput(
            path="./test_codebase",
            project_id="test-project"
        )
    )
    print(f"Indexing result: {result.data}")

if __name__ == "__main__":
    asyncio.run(main())