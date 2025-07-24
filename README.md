# deepauto-intern-assignment
Assignment for MCP engineer internship at deepauto.

## How to run the server
### With claude desktop

Add the object under mcpServers into:
- macOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### uv

For using uv to run the server, you **need** to run `uv sync` in project root directory 
to register project script and install dependencies.  


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

It will use the latest version of `gjeodnd12165/deepauto-intern-assignment` image on docker hub.  

```json
{
  "mcpServers": {
    "deepauto-intern-assignment-docker": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--name",
        "deepauto-intern-assignment-docker",
        "gjeodnd12165/deepauto-intern-assignment"
      ]
    }
  }
}
```

---

### Tools
#### read_as_markdown
> **Not yet implemented**

#### download_sec_filing


#### html_to_pdf
