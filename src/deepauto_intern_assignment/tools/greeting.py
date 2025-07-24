from deepauto_intern_assignment import mcp

@mcp.tool
async def get_a_name() -> str:
    """Returns hard-coded name.

    Returns a name "Anna". This tool should be called
    when the user doesn't provide any name.

    Returns:
        A fixed pre-configured name.
    
    """

    return "Anna"

@mcp.tool
async def greeting(name: str) -> str:
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