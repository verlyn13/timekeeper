# Task Scheduler Integration Test Implementation Plan

## Overview

This document provides a detailed plan for implementing the Task Scheduler integration tests, which are a high-priority component of the Phase 2 implementation. These tests will verify that the `TaskScheduler` correctly integrates with both `AgentTemporal` and `AdaptiveAgentTemporal` classes.

## Prerequisites

- Existing implementation of `AgentTemporal`
- Existing implementation of `AdaptiveAgentTemporal`
- Existing implementation of `TaskScheduler`
- Understanding of the project's testing framework (pytest + hypothesis)

## Implementation Steps

### 1. Create the Test File

Create a new file at `tests/integration/test_task_scheduler_integration.py` with the following structure:

```python
"""
Integration test for TaskScheduler with AgentTemporal and AdaptiveAgentTemporal.

Tests the interaction between the scheduling system and temporal systems,
verifying that tasks are correctly scheduled according to temporal constraints.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st

from src.python.agent_temporal import AgentTemporal
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal
from src.python.task_scheduler import TaskScheduler


@pytest.fixture
def standard_scheduler():
    """Create a standard TaskScheduler with AgentTemporal."""
    temporal = AgentTemporal()
    return TaskScheduler(temporal)


@pytest.fixture
def adaptive_scheduler():
    """Create a TaskScheduler with AdaptiveAgentTemporal."""
    adaptive_temporal = AdaptiveAgentTemporal(agent_count=3)
    return TaskScheduler(adaptive_temporal)
```

### 2. Basic Scheduler-Temporal Integration Tests

First, implement basic tests for TaskScheduler integration with AgentTemporal:

```python
class TestSchedulerTemporalIntegration:
    """Tests for integration between TaskScheduler and temporal systems."""

    def test_basic_scheduling(self, standard_scheduler):
        """Test that tasks can be scheduled and queried in temporal order."""
        # Create sample tasks with different temporal constraints
        scheduler = standard_scheduler
        temporal = scheduler.temporal_system

        # Create timepoints for tasks
        t1 = temporal.create_timepoint(cycle=5)
        t2 = temporal.create_timepoint(cycle=3)
        t3 = temporal.create_timepoint(cycle=10)

        # Schedule tasks
        scheduler.add_task("Task A", timepoint=t1, duration={"cycle": 2})
        scheduler.add_task("Task B", timepoint=t2, duration={"cycle": 1})
        scheduler.add_task("Task C", timepoint=t3, duration={"cycle": 3})

        # Get temporally ordered tasks
        ordered_tasks = scheduler.get_ordered_tasks()

        # Verify order based on timepoints
        assert ordered_tasks[0]["name"] == "Task B"  # cycle 3
        assert ordered_tasks[1]["name"] == "Task A"  # cycle 5
        assert ordered_tasks[2]["name"] == "Task C"  # cycle 10
```

### 3. Task Dependency Tests

Next, implement tests for task dependencies, which involve both the scheduler and temporal system:

```python
    def test_scheduler_task_dependencies(self, standard_scheduler):
        """Test that task dependencies are correctly handled."""
        scheduler = standard_scheduler
        temporal = scheduler.temporal_system

        # Create task timepoints
        start_time = temporal.create_timepoint(cycle=1)

        # Schedule tasks with dependencies
        task_a_id = scheduler.add_task("Task A", timepoint=start_time, duration={"cycle": 2})
        task_b_id = scheduler.add_task("Task B", timepoint=start_time, duration={"cycle": 1})

        # Task C depends on both A and B
        dependencies = [task_a_id, task_b_id]
        task_c_id = scheduler.add_task(
            "Task C",
            timepoint=start_time,  # Will be adjusted based on dependencies
            duration={"cycle": 3},
            dependencies=dependencies
        )

        # Get tasks with resolved timepoints
        all_tasks = scheduler.get_ordered_tasks()
        task_c = next((t for t in all_tasks if t["id"] == task_c_id), None)

        # Task C should start after both A and B are complete
        # A ends at cycle 3, B ends at cycle 2, so C should start at cycle 3
        assert task_c["timepoint"]["cycle"] >= 3
```

### 4. Multi-Agent Scheduling Tests

Implement tests for multi-agent scheduling using AdaptiveAgentTemporal:

```python
    def test_multi_agent_scheduling(self, adaptive_scheduler):
        """Test scheduling with multiple agents using AdaptiveAgentTemporal."""
        scheduler = adaptive_scheduler
        temporal = scheduler.temporal_system

        # Create tasks for different agents
        for agent_id in range(temporal.agent_count):
            for i in range(3):  # 3 tasks per agent
                timepoint = temporal.create_timepoint(cycle=i*2, agent=agent_id)
                scheduler.add_task(
                    f"Agent {agent_id} Task {i}",
                    timepoint=timepoint,
                    duration={"cycle": 1},
                    agent_id=agent_id
                )

        # Get tasks for each agent
        for agent_id in range(temporal.agent_count):
            agent_tasks = scheduler.get_agent_tasks(agent_id)

            # Verify correct number of tasks
            assert len(agent_tasks) == 3

            # Verify tasks are for the correct agent
            for task in agent_tasks:
                assert task["agent_id"] == agent_id

            # Verify temporal ordering
            for i in range(len(agent_tasks) - 1):
                t1 = agent_tasks[i]["timepoint"]
                t2 = agent_tasks[i+1]["timepoint"]
                assert temporal.compare_timepoints(t1, t2) <= 0
```

### 5. Adaptive Scheduling Tests

Finally, test the integration between scheduling and adaptive temporal systems:

```python
    def test_adaptive_scheduling(self, adaptive_scheduler):
        """Test adaptive scheduling with changing temporal granularity."""
        scheduler = adaptive_scheduler
        temporal = scheduler.temporal_system

        # Initial timepoint
        start_time = temporal.create_timepoint(cycle=1)

        # Schedule some initial tasks
        for i in range(5):
            scheduler.add_task(
                f"Task {i}",
                timepoint=temporal.add_time(start_time, cycle=i),
                duration={"cycle": 1}
            )

        # Get initial task count and timings
        initial_tasks = scheduler.get_ordered_tasks()

        # Trigger adaptation (e.g., by changing workload or agent count)
        temporal.adapt_granularity(factor=2.0)  # Double the granularity

        # Schedule some new tasks after adaptation
        for i in range(5):
            scheduler.add_task(
                f"Adapted Task {i}",
                timepoint=temporal.add_time(start_time, cycle=i*2),  # Adjusted for new granularity
                duration={"cycle": 2}  # Adjusted duration
            )

        # Get tasks after adaptation
        adapted_tasks = scheduler.get_ordered_tasks()

        # Verify adaptation effects
        # 1. We should have more tasks now
        assert len(adapted_tasks) > len(initial_tasks)

        # 2. Task timepoints should reflect the new granularity
        # This requires examining the timepoints and comparing them correctly
        for i, task in enumerate(adapted_tasks):
            if task["name"].startswith("Adapted"):
                # Verify these tasks have appropriate durations and timepoints
                assert task["duration"]["cycle"] == 2
```

### 6. Mathematical Property Testing with Hypothesis

Add property-based tests using hypothesis to verify that scheduling operations maintain mathematical properties:

```python
# Define custom strategies for scheduler tasks
@st.composite
def task_strategy(draw, scheduler=None):
    """Generate random tasks that work with the given scheduler."""
    if scheduler is None:
        # Use default TaskScheduler with AgentTemporal for strategy generation
        temporal = AgentTemporal()
        scheduler = TaskScheduler(temporal)

    # Generate a random timepoint
    timepoint = {}
    for unit in scheduler.temporal_system.units:
        name = unit["name"]
        if "subdivisions" in unit:
            max_val = unit["subdivisions"] * 2  # Allow values that need normalization
            timepoint[name] = draw(st.integers(min_value=0, max_value=max_val))
        else:
            # Base unit
            timepoint[name] = draw(st.integers(min_value=0, max_value=100))

    # Generate random duration
    duration = {}
    for unit in scheduler.temporal_system.units:
        name = unit["name"]
        include = draw(st.booleans())
        if include:
            duration[name] = draw(st.integers(min_value=1, max_value=5))

    # Ensure at least one duration unit
    if not duration:
        base_unit = scheduler.temporal_system.units[-1]["name"]
        duration[base_unit] = draw(st.integers(min_value=1, max_value=5))

    # Generate random name
    name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')),
                       min_size=3, max_size=10))

    # Return task parameters
    return {
        "name": name,
        "timepoint": timepoint,
        "duration": duration
    }


class TestSchedulerProperties:
    """Tests for mathematical properties of scheduler operations."""

    @given(tasks=st.lists(task_strategy(), min_size=1, max_size=5))
    def test_temporal_ordering_preservation(self, standard_scheduler, tasks):
        """Test that temporal ordering is preserved in the scheduler."""
        scheduler = standard_scheduler
        temporal = scheduler.temporal_system

        # Add all tasks
        for task in tasks:
            # Normalize timepoint first
            tp = temporal.normalize(task["timepoint"])
            scheduler.add_task(task["name"], timepoint=tp, duration=task["duration"])

        # Get ordered tasks
        ordered_tasks = scheduler.get_ordered_tasks()

        # Verify ordering is correct
        for i in range(len(ordered_tasks) - 1):
            t1 = ordered_tasks[i]["timepoint"]
            t2 = ordered_tasks[i+1]["timepoint"]
            # Current task should be earlier or equal to next task
            assert temporal.compare_timepoints(t1, t2) <= 0
```

## Testing Approach

### Manual Testing First

Before running automated tests, manually verify the `TaskScheduler` behavior by:

1. Creating a few tasks with simple timepoints
2. Setting up a simple dependency chain
3. Confirming that the tasks are scheduled in the expected order

### Automated Test Run

Once you've manually verified basic behavior, run the automated tests:

```
python -m pytest tests/integration/test_task_scheduler_integration.py -v
```

### Test Coverage

Ensure the tests cover these key integration aspects:

- Task ordering based on timepoints
- Task dependency resolution
- Multi-agent scheduling
- Adaptation effects on scheduling
- Mathematical properties of scheduling operations

## Potential Issues and Solutions

### 1. Task Ordering Edge Cases

**Issue**: Tasks with identical timepoints might be ordered inconsistently.

**Solution**: Implement and test a secondary ordering criterion (e.g., by task ID or creation time).

### 2. Dependency Resolution Complexity

**Issue**: Complex dependency chains could be difficult to verify.

**Solution**: Use helper functions to calculate expected start times from dependencies, then compare to actual schedule.

### 3. Adaptation Effects

**Issue**: Adaptation effects might not be easy to predict or verify.

**Solution**: Focus on verifying that post-adaptation tasks maintain correct relative ordering rather than trying to predict exact timepoint values.

## Success Criteria

The implementation is considered successful when:

1. All tests pass consistently
2. Test coverage for the integration points exceeds the target threshold (90%)
3. Each test clearly verifies a specific aspect of the integration
4. Tests handle edge cases appropriately
5. Test code follows project coding standards and patterns

## Documentation

Once the tests are implemented, update the relevant documentation:

1. Add a reference to the integration tests in the `docs/implementation/task_scheduler.md` file
2. Update the relevant theory documentation to note that implementation has been verified via integration tests
3. Consider adding a specific section about integration testing in the example suite

## Next Steps

After implementing the `TaskScheduler` integration tests:

1. Implement workflow integration tests
2. Implement visualization integration tests
3. Move on to docstring enhancement for `agent_temporal.py`
