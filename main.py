from pathlib import Path
import logging

from fastmcp import FastMCP, Context

from playwright.async_api import async_playwright

from resources import expose_static_resources, expose_pdf_file, expose_html_file

mcp = FastMCP("deepauto intern assignment mcp server")


@mcp.tool
def greeting(name: str) -> str:
    """
    Greet the user with name!
    """
    return f"Hello {name}!"

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
    # elif not Path(output_file_path).is_file():
    #     error_message = f"{output_file_path} is not a valid file path" 
    #     await ctx.error(error_message)
    #     return error_message
    
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

        expose_pdf_file(Path(output_file_path), mcp)

        await browser.close()


if __name__ == "__main__":
    expose_static_resources()
    mcp.run()