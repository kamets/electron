"""
🛠️ _SUDOTEER MCP MANAGER 🛠️
Orchestrates the lifecycle of MCP servers and clients.
Bridges the gap between standardized tools and the SudoAgency.
"""
import asyncio
import logging
import os
import subprocess
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("_SUDOTEER")

class MCPManager:
    """Manages the lifecycle of MCP connections for Sudoteer Agents."""

    def __init__(self):
        self.sessions = {}
        self.internal_server_proc = None
        # Registry of available MCP servers and their run commands
        self.registry = {
            "fetch": {
                "command": "python",
                "args": ["-m", "mcp_server_fetch"]
            },
            "sqlite": {
                "command": "python",
                "args": ["-m", "mcp_server_sqlite", "--db-path", "backend/data/sudoteer.db"]
            },
            "hardware": {
                "command": "python",
                "args": ["backend/mcp_server.py"]
            }
        }

    async def start_internal_server(self):
        """Launches the Sudoteer Hardware MCP server as a subprocess."""
        # Ensure data directory exists for sqlite
        os.makedirs("backend/data", exist_ok=True)

        info = self.registry["hardware"]
        python_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "Scripts", "python.exe"))
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", info["args"][0]))

        logger.info(f"🚀 Launching Internal MCP Server: {script_path}")
        # We start it as a stdio server
        self.internal_server_proc = subprocess.Popen(
            [python_exe, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        logger.info("✅ Internal Hardware MCP Server is online (PID: %s)", self.internal_server_proc.pid)

    async def get_all_tools(self):
        """Discovers tools across all registered MCP servers."""
        all_tools = {}
        python_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "Scripts", "python.exe"))

        for name, config in self.registry.items():
            try:
                # Prepare transport params
                cmd = python_exe if config["command"] == "python" else config["command"]
                params = StdioServerParameters(command=cmd, args=config["args"])

                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        all_tools[name] = tools
                        logger.info(f"🔍 MCP: Discovered {len(tools.tools)} tools on '{name}' server.")
            except Exception as e:
                logger.warning(f"Failed to discover tools for {name}: {e}")

        return all_tools

    async def connect_to_server(self, server_id: str, command: str, args: list):
        """Connect to an MCP server and store the session."""
        server_params = StdioServerParameters(command=command, args=args)

        # Note: In a production async app, we'd handle the context manager differently
        # For now, we provide a helper to run a specific tool
        return server_params

    async def call_tool(self, server_params: StdioServerParameters, tool_name: str, tool_args: dict):
        """Helper to invoke a tool on an MCP server."""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, tool_args)
                    return result
        except Exception as e:
            logger.error(f"MCP Tool Call Failed ({tool_name}): {e}")
            return None

    def shutdown(self):
        """Clean up all processes."""
        if self.internal_server_proc:
            self.internal_server_proc.terminate()
            logger.info("🛑 Internal MCP Server stopped.")

# Global Manager Instance
mcp_manager = MCPManager()
