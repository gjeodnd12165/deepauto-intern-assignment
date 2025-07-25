# deepauto-intern-assignment
Assignment for the MCP engineer internship at DeepAuto.

This MCP server fetches filings from the SEC DEGAR API and converts them.

## Usage
### With Claude desktop

Add the object under mcpServers into:
- macOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### uv

To use `uv` to run the server, you **need** to run `uv sync` in the project root directory 
to register the project script and install dependencies.  


```json
{
  "mcpServers": {
    "deepauto-intern-assignment": {
      "command": "uv",
      "args": [
        "--directory",
        "<absolute path to where pyproject.toml is>",
        "run",
        "mcp-server"
      ]
    }
  }
}
```

#### Docker

It will use the latest version of `gjeodnd12165/deepauto-intern-assignment` image on Docker Hub.  

```json
{
  "mcpServers": {
    "deepauto-intern-assignment-docker": {
      "command": "docker",
      "args": [
        "run",
        "gjeodnd12165/deepauto-intern-assignment",
        "--rm",
        "-i",
        "--name",
        "deepauto-intern-assignment-docker-claude",
        "--pull=always"
      ]
    }
  }
}
```

### Prompt Examples
#### Single tool calling
```
Convert tm2329302d4_def14a.htm into a pdf file.
```
```
Convert tm2329302d4_def14a.htm into a markdown text.
```
> This task should be performed in multiple tools according to the assignment.  
> However, it was mocked in a single tool due to the current situation.
```
Download 10-k filings of 320193, in 2024. 
```

### Multiple tool callings
```
Download 10-k filings of 320193, in 2023 and convert that into a pdf file. 
```
```
Download 8-k filings of 320193, in 2024 and convert that into a markdown text. 
```
```
Download def 14a filings of 320193, in 2021 and convert them into a pdf file and a markdown text.
```
> This prompt mocks the final integration test result.

---

### Tools
#### ~~read_as_markdown~~
> **Not implemented**

##### read_as_markdownify
Converts a local HTML file into markdown text using markdownify.  
Mocks `html_to_pdf` -> `read_as_markdown` workflow.

#### download_sec_filing
Fetches the most recent filing via the SEC EDGAR api.  
Returns a path to the primary document of the filing.

#### html_to_pdf
Converts the given local HTML file into a PDF file.  
Returns a path to the converted document.  

> You cannot see the converted file unless you visit the path manually.  
> For those using Docker: The working directory is `/app`. Look below it.
