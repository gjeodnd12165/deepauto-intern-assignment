from deepauto_intern_assignment import mcp

from pathlib import Path

from fastmcp import Context

from playwright.async_api import async_playwright

@mcp.tool
async def html_to_pdf(input_file_path: str, output_file_path: str, ctx: Context) -> None:
    """Converts a html file to a pdf file.

    Transfrom given html to a pdf file using playwright.

    Args:
        input_file_path: A path to a html file relative to the server directory.
            This path must be under html/
        output_file_path: A path of a pdf file to save relative to the server
            directory. This path must be under pdf/
    
    Returns:
        None
    
    Raises:
        ValueError: If the specified input_file_path towards not existing file.
    """

    if not Path(input_file_path).is_file():
        raise ValueError(
            f"{input_file_path} is not a valid file path."
        )
    
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
