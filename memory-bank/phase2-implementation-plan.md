# Phase 2 Implementation Plan

This document outlines the implementation plan for Phase 2 of the Timekeeper project, focused on integration tests, docstring enhancement, and example suite development.

## Integration Testing Implementation

### 1. Task Scheduler Integration Test

Create a new file: `tests/integration/test_task_scheduler_integration.py`

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

### 2. Visualization Integration Test

Create a new file: `tests/integration/test_visualization_integration.py`

```python
"""
Integration test for Visualization with temporal systems.

Tests that visualization components correctly represent the temporal
structures and operations from the core components.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt

from src.python.agent_temporal import AgentTemporal
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal
from src.python.task_scheduler import TaskScheduler
from src.python.visualization import (
    visualize_timepoint,
    visualize_timeline,
    visualize_schedule
)


@pytest.fixture
def temporal_system():
    """Create a standard AgentTemporal for testing."""
    return AgentTemporal()


@pytest.fixture
def task_schedule():
    """Create a TaskScheduler with a predefined schedule."""
    temporal = AgentTemporal()
    scheduler = TaskScheduler(temporal)

    # Add tasks with various timepoints
    t1 = temporal.create_timepoint(cycle=1, step=0)
    t2 = temporal.create_timepoint(cycle=1, step=500)
    t3 = temporal.create_timepoint(cycle=2, step=0)
    t4 = temporal.create_timepoint(cycle=3, step=0)

    scheduler.add_task("Task 1", timepoint=t1, duration={"cycle": 0, "step": 400})
    scheduler.add_task("Task 2", timepoint=t2, duration={"cycle": 0, "step": 300})
    scheduler.add_task("Task 3", timepoint=t3, duration={"cycle": 1, "step": 0})
    scheduler.add_task("Long Task", timepoint=t4, duration={"cycle": 2, "step": 0})

    return scheduler


class TestVisualizationIntegration:
    """Tests for visualization integration with temporal systems."""

    def test_timepoint_visualization(self, temporal_system):
        """Test that timepoints are correctly visualized."""
        # Create a timepoint to visualize
        tp = temporal_system.create_timepoint(epoch=1, cycle=15, step=30)

        # Generate visualization (most visualization functions return a figure)
        fig = visualize_timepoint(tp, temporal_system)

        # Basic assertions about the visualization
        assert fig is not None
        assert isinstance(fig, plt.Figure)

        # Check that the figure has appropriate elements
        # This is a basic smoke test - in a real test you'd check more properties
        axes = fig.get_axes()
        assert len(axes) > 0

        # Clean up
        plt.close(fig)

    def test_timeline_visualization(self, temporal_system):
        """Test that timelines are correctly visualized."""
        # Create a sequence of timepoints
        timepoints = [
            temporal_system.create_timepoint(cycle=i*5)
            for i in range(5)
        ]

        # Generate visualization
        fig = visualize_timeline(timepoints, temporal_system)

        # Basic assertions
        assert fig is not None
        assert isinstance(fig, plt.Figure)

        # Check for timeline elements
        axes = fig.get_axes()
        assert len(axes) > 0

        # Clean up
        plt.close(fig)

    def test_schedule_visualization(self, task_schedule):
        """Test that task schedules are correctly visualized."""
        # Get ordered tasks
        tasks = task_schedule.get_ordered_tasks()

        # Generate visualization
        fig = visualize_schedule(tasks, task_schedule.temporal_system)

        # Basic assertions
        assert fig is not None
        assert isinstance(fig, plt.Figure)

        # Check for schedule elements
        axes = fig.get_axes()
        assert len(axes) > 0

        # Clean up
        plt.close(fig)

    def test_integrated_visualization(self, task_schedule):
        """Test integrated visualization across multiple components."""
        # This test simulates a workflow that:
        # 1. Creates timepoints
        # 2. Schedules tasks
        # 3. Visualizes the entire system

        scheduler = task_schedule
        temporal = scheduler.temporal_system

        # Create additional timepoints
        current_time = temporal.create_timepoint(cycle=5)

        # Schedule additional tasks
        scheduler.add_task(
            "Integration Task",
            timepoint=current_time,
            duration={"cycle": 1}
        )

        # Get updated tasks
        all_tasks = scheduler.get_ordered_tasks()

        # Generate integrated visualization
        # This would combine multiple visualization elements
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Visualize current time
        visualize_timepoint(current_time, temporal, ax=ax1)
        ax1.set_title("Current Time")

        # Visualize schedule
        visualize_schedule(all_tasks, temporal, ax=ax2)
        ax2.set_title("Task Schedule")

        # Basic assertions
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        assert len(fig.get_axes()) == 2

        # Clean up
        plt.close(fig)


class TestAdaptiveVisualization:
    """Tests for visualization of adaptive temporal systems."""

    def test_adaptive_timeline_visualization(self):
        """Test visualization of timelines with adaptive granularity."""
        # Create adaptive temporal system
        adaptive = AdaptiveAgentTemporal(agent_count=2)

        # Create initial timepoints
        initial_timepoints = [
            adaptive.create_timepoint(cycle=i*10)
            for i in range(3)
        ]

        # Visualize initial timeline
        fig1 = visualize_timeline(initial_timepoints, adaptive)

        # Adapt granularity
        adaptive.adapt_granularity(factor=2.0)

        # Create new timepoints after adaptation
        adapted_timepoints = [
            adaptive.create_timepoint(cycle=i*5)  # Different spacing due to adaptation
            for i in range(6)  # More points after adaptation
        ]

        # Visualize adapted timeline
        fig2 = visualize_timeline(adapted_timepoints, adaptive)

        # Basic assertions
        assert fig1 is not None and fig2 is not None

        # In a real test, we'd compare visual properties between the two figures
        # to verify that the adaptation is correctly represented

        # Clean up
        plt.close(fig1)
        plt.close(fig2)
```

## 3. Complete Workflow Integration Test

Create a new file: `tests/integration/test_workflow_integration.py`

```python
"""
End-to-end workflow integration test for the Timekeeper framework.

Tests complete workflows that span multiple components to verify
full system integration.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt

from src.python.agent_temporal import AgentTemporal
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal
from src.python.task_scheduler import TaskScheduler
from src.python.visualization import visualize_timeline, visualize_schedule


class TestCompleteWorkflows:
    """Tests for complete end-to-end workflows."""

    def test_basic_workflow(self):
        """Test basic workflow from timepoint creation to visualization."""
        # STEP 1: Create temporal system
        temporal = AgentTemporal()

        # STEP 2: Create scheduler
        scheduler = TaskScheduler(temporal)

        # STEP 3: Create timepoints
        start_time = temporal.create_timepoint(cycle=1)

        # STEP 4: Schedule tasks
        task_ids = []
        for i in range(5):
            task_time = temporal.add_time(start_time, cycle=i)
            task_id = scheduler.add_task(
                f"Task {i+1}",
                timepoint=task_time,
                duration={"cycle": 1, "step": i*100}
            )
            task_ids.append(task_id)

        # STEP 5: Create dependencies between tasks
        # Make task 5 depend on tasks 3 and 4
        scheduler.add_dependency(task_ids[4], task_ids[2])
        scheduler.add_dependency(task_ids[4], task_ids[3])

        # STEP 6: Get schedule with resolved dependencies
        resolved_schedule = scheduler.get_ordered_tasks()

        # STEP 7: Verify dependency resolution
        task5 = next((t for t in resolved_schedule if t["id"] == task_ids[4]), None)
        task3 = next((t for t in resolved_schedule if t["id"] == task_ids[2]), None)
        task4 = next((t for t in resolved_schedule if t["id"] == task_ids[3]), None)

        # Task 5 should start after tasks 3 and 4 are complete
        task3_end = temporal.add_time(task3["timepoint"], **task3["duration"])
        task4_end = temporal.add_time(task4["timepoint"], **task4["duration"])

        # Use maximum of end times from task3 and task4
        if temporal.compare_timepoints(task3_end, task4_end) > 0:
            expected_start = task3_end
        else:
            expected_start = task4_end

        # Verify task 5 starts at or after the expected start time
        assert temporal.compare_timepoints(task5["timepoint"], expected_start) >= 0

        # STEP 8: Create visualization of the schedule
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        visualize_schedule(resolved_schedule, temporal, ax=ax)
        plt.close(fig)  # Close to avoid displaying in test

    def test_adaptive_workflow(self):
        """Test workflow with adaptive temporal system."""
        # STEP 1: Create adaptive temporal system
        adaptive = AdaptiveAgentTemporal(agent_count=3)

        # STEP 2: Create scheduler
        scheduler = TaskScheduler(adaptive)

        # STEP 3: Initial scheduling (before adaptation)
        base_time = adaptive.create_timepoint(cycle=0)
        initial_tasks = []

        # Schedule initial tasks for each agent
        for agent_id in range(adaptive.agent_count):
            for i in range(3):
                task_time = adaptive.add_time(
                    base_time,
                    cycle=i*2,
                    agent=agent_id
                )
                task_id = scheduler.add_task(
                    f"Agent {agent_id} Task {i}",
                    timepoint=task_time,
                    duration={"cycle": 1},
                    agent_id=agent_id
                )
                initial_tasks.append(task_id)

        # STEP 4: Get initial schedule
        initial_schedule = scheduler.get_ordered_tasks()

        # STEP 5: Adapt granularity based on workload
        # Simulate increased workload for agent 1
        adaptive.adapt_granularity(factor=1.5, agent=1)

        # STEP 6: Schedule additional tasks after adaptation
        adapted_tasks = []
        for agent_id in range(adaptive.agent_count):
            for i in range(2):
                # Use shorter cycles for the agent with increased granularity
                cycle_incr = i * (1 if agent_id == 1 else 2)

                task_time = adaptive.add_time(
                    adaptive.create_timepoint(cycle=10),  # Later timepoint
                    cycle=cycle_incr,
                    agent=agent_id
                )

                task_id = scheduler.add_task(
                    f"Adapted Agent {agent_id} Task {i}",
                    timepoint=task_time,
                    duration={"cycle": 1 if agent_id == 1 else 2},
                    agent_id=agent_id
                )
                adapted_tasks.append(task_id)

        # STEP 7: Get adapted schedule
        adapted_schedule = scheduler.get_ordered_tasks()

        # STEP 8: Verify adaptation effects
        # Count tasks per agent after adaptation
        agent_task_counts = {}
        for task in adapted_schedule:
            agent_id = task.get("agent_id", 0)
            agent_task_counts[agent_id] = agent_task_counts.get(agent_id, 0) + 1

        # All agents should have their tasks
        for agent_id in range(adaptive.agent_count):
            assert agent_id in agent_task_counts

        # STEP 9: Create visualization comparing before/after adaptation
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Filter for just the initial tasks
        initial_task_objs = [t for t in adapted_schedule if t["id"] in initial_tasks]
        visualize_schedule(initial_task_objs, adaptive, ax=ax1)
        ax1.set_title("Before Adaptation")

        # Filter for just the adapted tasks
        adapted_task_objs = [t for t in adapted_schedule if t["id"] in adapted_tasks]
        visualize_schedule(adapted_task_objs, adaptive, ax=ax2)
        ax2.set_title("After Adaptation")

        plt.close(fig)  # Close to avoid displaying in test

    def test_multi_agent_workflow_with_synchronization(self):
        """Test workflow with multiple agents and synchronization points."""
        # STEP 1: Create adaptive temporal system with multiple agents
        adaptive = AdaptiveAgentTemporal(agent_count=3)

        # STEP 2: Create scheduler
        scheduler = TaskScheduler(adaptive)

        # STEP 3: Create synchronization timepoints
        sync_points = [
            adaptive.create_timepoint(cycle=5),
            adaptive.create_timepoint(cycle=10),
            adaptive.create_timepoint(cycle=15)
        ]

        # STEP 4: Schedule independent tasks for each agent
        independent_tasks = []
        for agent_id in range(adaptive.agent_count):
            for i in range(4):
                task_time = adaptive.create_timepoint(
                    cycle=i,
                    agent=agent_id
                )

                task_id = scheduler.add_task(
                    f"Agent {agent_id} Indep {i}",
                    timepoint=task_time,
                    duration={"cycle": 1},
                    agent_id=agent_id
                )
                independent_tasks.append(task_id)

        # STEP 5: Schedule synchronized tasks that depend on all agents
        # completing their independent tasks
        sync_tasks = []
        for i, sync_point in enumerate(sync_points):
            # For each sync point, add a task for each agent
            for agent_id in range(adaptive.agent_count):
                # Create dependencies on all independent tasks for this agent
                dependencies = [
                    task_id for idx, task_id in enumerate(independent_tasks)
                    if idx % adaptive.agent_count == agent_id
                ]

                task_id = scheduler.add_task(
                    f"Agent {agent_id} Sync {i}",
                    timepoint=sync_point,  # All agents sync at same timepoint
                    duration={"cycle": 2},
                    agent_id=agent_id,
                    dependencies=dependencies
                )
                sync_tasks.append(task_id)

        # STEP 6: Create cross-agent dependencies for final task
        final_task_deps = sync_tasks[-adaptive.agent_count:]  # Last sync task from each agent

        final_time = adaptive.create_timepoint(cycle=20)
        final_task = scheduler.add_task(
            "Final Integrated Task",
            timepoint=final_time,
            duration={"cycle": 5},
            dependencies=final_task_deps
        )

        # STEP 7: Get resolved schedule
        resolved_schedule = scheduler.get_ordered_tasks()

        # STEP 8: Verify synchronization points
        for i in range(len(sync_points)):
            # Get all sync tasks for this sync point
            sync_point_tasks = [
                t for t in resolved_schedule
                if t["id"] in sync_tasks[i*adaptive.agent_count:(i+1)*adaptive.agent_count]
            ]

            # All tasks for a sync point should have the same timepoint
            assert len(sync_point_tasks) == adaptive.agent_count
            first_tp = sync_point_tasks[0]["timepoint"]

            for task in sync_point_tasks[1:]:
                assert adaptive.compare_timepoints(first_tp, task["timepoint"]) == 0

        # STEP 9: Verify final task depends on all agents
        final_task_obj = next((t for t in resolved_schedule if t["id"] == final_task), None)
        assert final_task_obj is not None

        # Final task should start after all sync tasks are complete
        for dep_id in final_task_deps:
            dep_task = next((t for t in resolved_schedule if t["id"] == dep_id), None)
            dep_end = adaptive.add_time(dep_task["timepoint"], **dep_task["duration"])
            assert adaptive.compare_timepoints(final_task_obj["timepoint"], dep_end) >= 0
```

## 2. Docstring Enhancement Implementation

I recommend starting with the core `agent_temporal.py` file, as it's the foundation of the system:

1. Open the file: `src/python/agent_temporal.py`
2. Enhance docstrings with LaTeX mathematical formulations
3. Add explicit cross-references to the theory documentation

Here's a template for enhanced docstrings:

```python
def normalize(self, timepoint):
    """
    Normalize a timepoint to ensure all unit values are within their valid ranges.

    This implements the normalization function $N: T \\rightarrow T$ defined in the
    Temporal Universe theory (see docs/theory/temporal_universe.md), where:

    \\begin{align}
    N(t) = (u_1, u_2, \\ldots, u_n) \\text{ such that } 0 \\leq u_i < s_i \\text{ for } i < n
    \\end{align}

    where $s_i$ is the number of subdivisions for unit $i$, and $u_n$ (the base unit)
    can be any non-negative integer.

    Parameters
    ----------
    timepoint : dict
        Dictionary representation of a timepoint with unit names as keys
        and unit values as values.

    Returns
    -------
    dict
        Normalized timepoint where all values are within their valid ranges.

    See Also
    --------
    docs/theory/temporal_universe.md : Definition of the temporal universe
    docs/theory/timepoint_operations.md : Detailed explanation of normalization
    """
```

## 3. Example Suite Development

Create a comprehensive example in the `docs/examples/` directory:

````markdown
# Complete Workflow Example

This example demonstrates a complete workflow using the Timekeeper framework, including:

1. Creating temporal systems
2. Defining and scheduling tasks
3. Managing dependencies
4. Adapting temporal granularity
5. Visualizing the results

## Setup

```python
import matplotlib.pyplot as plt
from src.python.agent_temporal import AgentTemporal
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal
from src.python.task_scheduler import TaskScheduler
from src.python.visualization import visualize_timepoint, visualize_timeline, visualize_schedule
```
````

## Basic Temporal Operations

First, let's create a temporal system and perform some basic operations:

```python
# Create a standard temporal system
temporal = AgentTemporal()

# Create some timepoints
t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
t2 = temporal.create_timepoint(epoch=1, cycle=15, step=45)

# Add timepoints
t3 = temporal.add_time(t1, cycle=10, step=20)
print(f"t1 + (10 cycles, 20 steps) = {t3}")

# Convert to human time
human_time = temporal.to_human_time(t3)
print(f"Equivalent human time: {human_time}")
```

## Task Scheduling

Next, let's schedule some tasks:

```python
# Create a scheduler
scheduler = TaskScheduler(temporal)

# Define some tasks
scheduler.add_task("Task A", timepoint=t1, duration={"cycle": 2})
scheduler.add_task("Task B", timepoint=t2, duration={"cycle": 1})
scheduler.add_task("Task C", timepoint=t3, duration={"cycle": 3})

# Get the ordered tasks
tasks = scheduler.get_ordered_tasks()
for task in tasks:
    print(f"{task['name']} at {task['timepoint']} for {task['duration']}")
```

## Dependencies

Let's add dependencies between tasks:

```python
# Create new tasks with dependencies
task_d_id = scheduler.add_task("Task D", timepoint=t1, duration={"cycle": 1})
task_e_id = scheduler.add_task("Task E", timepoint=t2, duration={"cycle": 2})

# Task F depends on both D and E
task_f_id = scheduler.add_task(
    "Task F",
    timepoint=temporal.create_timepoint(),  # Will be adjusted based on dependencies
    duration={"cycle": 2},
    dependencies=[task_d_id, task_e_id]
)

# Get the updated schedule
updated_tasks = scheduler.get_ordered_tasks()

# Find Task F
task_f = next((t for t in updated_tasks if t["id"] == task_f_id), None)
print(f"Task F scheduled at: {task_f['timepoint']}")
```

## Adaptive Temporal System

Now let's use an adaptive temporal system:

```python
# Create an adaptive system with multiple agents
adaptive = AdaptiveAgentTemporal(agent_count=2)

# Create tasks for different agents
agent_scheduler = TaskScheduler(adaptive)

# Add tasks for agent 0
for i in range(3):
    timepoint = adaptive.create_timepoint(cycle=i*2, agent=0)
    agent_scheduler.add_task(
        f"Agent 0 Task {i}",
        timepoint=timepoint,
        duration={"cycle": 1},
        agent_id=0
    )

# Add tasks for agent 1
for i in range(3):
    timepoint = adaptive.create_timepoint(cycle=i*2, agent=1)
    agent_scheduler.add_task(
        f"Agent 1 Task {i}",
        timepoint=timepoint,
        duration={"cycle": 1},
        agent_id=1
    )

# Adapt granularity for agent 1
adaptive.adapt_granularity(factor=2.0, agent=1)

# Add more tasks after adaptation
for i in range(2):
    timepoint = adaptive.create_timepoint(cycle=10 + i, agent=1)
    agent_scheduler.add_task(
        f"Agent 1 Adapted Task {i}",
        timepoint=timepoint,
        duration={"cycle": 1},
        agent_id=1
    )

# Get all tasks
all_tasks = agent_scheduler.get_ordered_tasks()
```

## Visualization

Finally, let's visualize the results:

```python
# Create figure for visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Visualize tasks for agent 0
agent0_tasks = [t for t in all_tasks if t.get("agent_id") == 0]
visualize_schedule(agent0_tasks, adaptive, ax=ax1)
ax1.set_title("Agent 0 Schedule (Standard)")

# Visualize tasks for agent 1
agent1_tasks = [t for t in all_tasks if t.get("agent_id") == 1]
visualize_schedule(agent1_tasks, adaptive, ax=ax2)
ax2.set_title("Agent 1 Schedule (Adapted)")

plt.tight_layout()
plt.show()
```

## Conclusion

This example has demonstrated the key capabilities of the Timekeeper framework:

1. Creating and manipulating timepoints
2. Scheduling tasks with dependencies
3. Working with multiple agents
4. Adapting temporal granularity
5. Visualizing temporal schedules

The framework provides a mathematically rigorous approach to temporal management in agent systems, with full support for complex scheduling scenarios.

```

## Implementation Priority Order

Based on the overall project status, I recommend this priority order for Phase 2 implementation:

1. Integration tests implementation
   - Task Scheduler Integration (highest priority)
   - Complete Workflow tests
   - Visualization Integration tests

2. Docstring enhancement
   - agent_temporal.py (highest priority)
   - task_scheduler.py
   - adaptive_agent_temporal.py
   - visualization.py

3. Example suite development
   - Complete workflow example
   - Specialized examples for specific use cases

This plan focuses first on ensuring that all components work together correctly through integration tests, then improves the documentation to ensure bidirectional traceability between theory and implementation, and finally provides comprehensive examples to demonstrate the framework's capabilities.
```
