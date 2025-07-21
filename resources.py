from pathlib import Path

from fastmcp import FastMCP
from fastmcp.resources import FileResource

def expose_static_resources(mcp: FastMCP) -> None:
    """
    Scans the pdf/ and html/ directories and exposes each file
    as a discoverable resource.
    """

    PDF_DIR = Path("pdf")
    HTML_DIR = Path("html")

    PDF_DIR.mkdir(exist_ok=True)
    HTML_DIR.mkdir(exist_ok=True)

    # Files in the html/ directory
    for html_file in HTML_DIR.glob("**/*.htm"):
        expose_html_file(html_file, mcp)
    # Files in the pdf/ directory
    for pdf_file in PDF_DIR.glob("**/*.pdf"):
        expose_pdf_file(pdf_file, mcp)

def expose_html_file(path: Path, mcp: FastMCP) -> None:
    """
    Exposes given html file as a resource.
    
    TODO: Remove mcp dependency
    """
    resolved_path = path.resolve()
    resource = FileResource(
        uri=resolved_path.as_uri(),
        path=resolved_path,
        name=resolved_path.name,
        description=f"Static document resource, {resolved_path.name}",
        mime_type="text/html"
    )
    mcp.add_resource(resource)

def expose_pdf_file(path: Path, mcp: FastMCP) -> None:
    """
    Exposes given pdf file as a resource.

    TODO: Remove mcp dependency
    """
    resolved_path = path.resolve()
    resource = FileResource(
        uri=resolved_path.as_uri(),
        path=resolved_path,
        name=resolved_path.name,
        description=f"Static document resource, {resolved_path.name}",
        mime_type="application/pdf"
    )
    mcp.add_resource(resource)