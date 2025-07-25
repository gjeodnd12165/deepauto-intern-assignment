import os
from pathlib import Path
import re

from deepauto_intern_assignment import mcp

from markdownify import MarkdownConverter, markdownify
from bs4 import Tag
import readabilipy.simple_json
import requests

@mcp.tool(enabled=False)
async def read_as_markdown(
    input_file_path: str
) -> str:
    """Converts pdf file into markdown text.

    Takes given pdf document and transpiles it into markdown text.
    **This is mocking tool, doesn't use docling at all.**

    Args:
        input_file_path: A path to a directory of a pdf document 
            relative to main server directory. It should be under pdf/ .
    
    Returns:
        A string of converted markdown text.

    Raises:
        ValueError: If the specified input_file_path towards not existing file.
    """

    if not Path(input_file_path).is_file():
        raise ValueError(
            f"{input_file_path} is not a valid file path."
        )

@mcp.tool
async def read_as_markdownify(
    input_file_path: str
) -> str:
    """Converts a HTML file into markdown text.

    This tool reads an HTML document from a local file path, simplifies
    the HTML content, and then converts it into markdown text.

    Args:
        input_file_path: The path to the local HTML file.

    Returns:
        A string of converted markdown text, or an error message
        if conversion fails.

    Raises:
        ValueError: If the specified input_file_path is not a valid file.
        FileNotFoundError: If the file is not found at the specified path.
    """
    file_path = Path(input_file_path)

    if not file_path.is_file():
        raise ValueError(f"The provided path '{input_file_path}' is not a file.")

    try:
        # Read the file directly instead of using requests
        with open(file_path, "rb") as f:
            html = f.read()
        
        md = _markdownify_display_none(html)

        return md
    except FileNotFoundError:
        # This is raised if the file is deleted between the check and the open call
        raise FileNotFoundError(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        return f"<error>An unexpected error occurred: {e}</error>"


class _RemoveDisplayNoneConverter(MarkdownConverter):
    """
    See https://github.com/matthewwithanm/python-markdownify?tab=readme-ov-file#creating-custom-converters
    """
    def convert_div(self, el, text, parent_tags):
        style = el.get('style', '')

        if re.search(r'display:\s*none', style, re.IGNORECASE):
            return ''
        
        return super().convert_div(el, text, parent_tags)

def _markdownify_display_none(html, **options):
    return _RemoveDisplayNoneConverter(**options).convert(html)