"""
Configuration and shared fixtures for integration tests.
"""

import pytest

# Assuming these are the correct import paths
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal
from src.python.task_scheduler import TaskScheduler


@pytest.fixture(scope="function")  # Default scope, can be adjusted if needed
def adaptive_temporal():
    """Fixture providing an AdaptiveAgentTemporal instance for integration tests."""
    # Using agent_count=2 as seen in the original definition
    return AdaptiveAgentTemporal(agent_count=2)


@pytest.fixture(scope="function")
def adaptive_scheduler(adaptive_temporal):
    """Fixture providing a TaskScheduler instance linked to the adaptive_temporal fixture."""
    # Pass the adaptive_temporal instance to the scheduler's constructor
    return TaskScheduler(temporal_system=adaptive_temporal)
