import asyncio
from fastmcp import Client

client = Client("main.py")

async def pdf_to_markdown(input_file_path: str) -> None:
    print(input_file_path)
    async with client:
        result = await client.call_tool("greeting", {"name": "Anna"})
        print(result)

async def html_to_pdf(input_file_path: str, output_file_path: str) -> None:
    print(f"input_file_path: {input_file_path}")
    print(f"output_file_path: {output_file_path}")

    async with client:
        result = await client.call_tool("html_to_pdf", {"input_file_path": input_file_path, "output_file_path": output_file_path})
        return

# asyncio.run(pdf_to_markdown("pdf/Amazon.com Inc. - Form 8-K. 2024-05-14.pdf"))

asyncio.run(html_to_pdf(input_file_path="html/amzn-20240331.htm", output_file_path="pdf/amzn-20240331.pdf"))