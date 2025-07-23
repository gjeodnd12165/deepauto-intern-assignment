from shared import mcp

from pathlib import Path

from fastmcp import Context

from playwright.async_api import async_playwright

@mcp.tool
async def html_to_pdf(input_file_path: str, output_file_path: str, ctx: Context) -> None:
    """
    Recieve a name of a htm/html file and
    save that as a pdf file.
    """

    if not Path(input_file_path).is_file():
        error_message = f"{input_file_path} is not a valid file path."
        await ctx.error(error_message)
        return error_message
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(Path(input_file_path).resolve().as_uri())

        await page.pdf(
            path=output_file_path,
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        )

        await browser.close()
