from shared import mcp

@mcp.tool
def greeting(name: str) -> str:
    """Greets the user with name.

    Greets the user for testing purpose.  
    This may not be called if there is no explicit calling
    For exmaple:

        "Please call the greeting tool. I am Anna"
    
    Args:
        name: A name of the user.
    
    Returns:
        A message greeting the user with given name.
    
    Raises:
        
    """
    return f"Hello {name}!"