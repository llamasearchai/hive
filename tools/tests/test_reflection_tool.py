"""
Tests for Reflection Tool.
"""

import pytest

from aden_tools.tools.reflection_tool.reflection_tool import ReflectionTool
from framework.runtime.event_bus import AgentEvent, EventBus, EventType


@pytest.mark.asyncio
async def test_get_recent_events():
    """Should return list of events from EventBus."""
    bus = EventBus()
    tool = ReflectionTool(bus)

    # Populate bus
    await bus.publish(AgentEvent(EventType.EXECUTION_STARTED, "s1", "e1"))
    await bus.publish(AgentEvent(EventType.EXECUTION_COMPLETED, "s1", "e1", data={"res": 1}))

    events = await tool.get_recent_events(limit=5)

    assert len(events) == 2
    assert events[0]["type"] == EventType.EXECUTION_COMPLETED.value
    assert events[1]["type"] == EventType.EXECUTION_STARTED.value


@pytest.mark.asyncio
async def test_get_recent_events_filtered():
    """Should filter events by type."""
    bus = EventBus()
    tool = ReflectionTool(bus)

    await bus.publish(AgentEvent(EventType.EXECUTION_STARTED, "s1", "e1"))
    await bus.publish(AgentEvent(EventType.EXECUTION_COMPLETED, "s1", "e1"))

    events = await tool.get_recent_events(limit=5, event_type="execution_started")

    assert len(events) == 1
    assert events[0]["type"] == EventType.EXECUTION_STARTED.value


@pytest.mark.asyncio
async def test_get_execution_stats():
    """Should return stats from EventBus."""
    bus = EventBus()
    tool = ReflectionTool(bus)

    await bus.publish(AgentEvent(EventType.EXECUTION_STARTED, "s1"))

    stats = await tool.get_execution_stats()

    assert stats["total_events"] == 1
    assert "execution_started" in stats["events_by_type"]
