from fastapi import FastAPI
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b + 10

# Mount the MCP app as a sub-application
mcp_app = mcp.streamable_http_app()

# Create FastAPI app
app = FastAPI(
    title="Weather MCP Service",
    description="A service that provides weather alerts and forecasts",
    version="1.0.0",
    lifespan=mcp_app.router.lifespan_context,
)

app.mount("/mcp-server", mcp_app, "mcp")


# Root endpoint
u/app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint showing service information."""
    return {
        "service": "Weather MCP Service",
        "version": "1.0.0",
        "status": "running",
    }


# Health check endpoint
u/app.get("/health-check")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}