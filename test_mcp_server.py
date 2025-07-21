from fastmcp import FastMCPServer, tool

# Create a server instance
server = FastMCPServer()

@tool
def get_greeting(name: str) -> str:
    """Returns a personalized greeting."""
    return f"Hello, {name}! Welcome to the world of MCP."

if __name__ == "__main__":
    server.run()