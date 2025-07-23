from shared import mcp

@mcp.tool
def greeting(name: str) -> str:
    """
    Greet the user with name!
    """
    return f"Hello {name}!"