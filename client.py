import asyncio
from fastmcp import Client

client = Client("main.py")
        

async def pdf_to_markdown(input_file_path: str):
    print(input_file_path)
    async with client:
        result = await client.call_tool("greeting", {"name": "Anna"})
        print(result)
        result = await client.call_tool("read_as_markdown", {"input_file_path": input_file_path})
        print(result)

asyncio.run(pdf_to_markdown("Amazon.com Inc. - Form 8-K. 2024-05-14.pdf"))
