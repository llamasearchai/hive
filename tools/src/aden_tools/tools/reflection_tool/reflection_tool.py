"""
Reflection Tool - Allows agents to inspect their own execution history.
"""

from typing import Any

from framework.runtime.event_bus import EventBus
from mcp.server.fastmcp import FastMCP


class ReflectionTool:
    """
    Tool for agents to query their own event history.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def get_recent_events(
        self, limit: int = 10, event_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get the most recent events from the agent's execution history.

        Args:
            limit: Number of events to return (max 100)
            event_type: Optional filter by event type (e.g., 'execution_failed', 'tool_use')
        """
        limit = min(limit, 100)

        # We need to map string event_type to Enum if needed, or update EventBus
        # For now, we assume EventBus handles filtering by string if we cast it or
        # we do manual filtering here if EventBus requires Enum.

        # Looking at EventBus implementation:
        # get_history(event_type: EventType | None ...)

        # So we need to convert string to EventType if provided.
        from framework.runtime.event_bus import EventType

        e_type = None
        if event_type:
            try:
                e_type = EventType(event_type)
            except ValueError:
                # If invalid type is passed, return empty list or ignored?
                # Let's return error message or just ignore filtering for robustness?
                # Best to return empty or error. Let's return empty events.
                return []

        events = self.event_bus.get_history(event_type=e_type, limit=limit)
        return [e.to_dict() for e in events]

    async def get_execution_stats(self) -> dict[str, Any]:
        """Get statistics about the current execution session."""
        return self.event_bus.get_stats()


def register_tools(mcp: FastMCP, event_bus: EventBus) -> None:
    """Register reflection tools with MCP server."""
    tool = ReflectionTool(event_bus)

    @mcp.tool()
    async def get_recent_events(limit: int = 10, event_type: str | None = None) -> str:
        """
        Get recent events from the agent's execution history.
        Useful for understanding what happened previously, debugging errors,
        or checking previous tool outputs.
        """
        import json

        events = await tool.get_recent_events(limit, event_type)
        return json.dumps(events, indent=2)

    @mcp.tool()
    async def get_execution_stats() -> str:
        """
        Get statistics about the current execution session (success/failure counts, etc).
        """
        import json

        stats = await tool.get_execution_stats()
        return json.dumps(stats, indent=2)
