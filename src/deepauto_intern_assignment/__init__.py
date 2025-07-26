from .server import mcp

from .tools import download_sec_filing, html_to_pdf, read_as_markdown

def main():
    mcp.run()

if __name__ == "__main__":
    main()