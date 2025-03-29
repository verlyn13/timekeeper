# Integration Test Examples

This document provides example code for the integration tests that need to be implemented for the Timekeeper MVP. These examples can be used as templates when implementing the actual test files.

## Temporal Scheduling Integration Tests

The following example demonstrates how to test the integration between `AgentTemporal` and `TaskScheduler` components.

```python
"""
Integration test suite for the interaction between AgentTemporal and TaskScheduler.

This test suite verifies that the temporal system and the task scheduler work
together correctly, maintaining temporal consistency and properly handling
dependencies.
"""

import pytest
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.task_scheduler import TaskScheduler


class TestTemporalSchedulingIntegration:
    """Test suite for AgentTemporal and TaskScheduler integration."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.temporal = AgentTemporal()
        self.scheduler = TaskScheduler(self.temporal)

    def test_basic_scheduling_workflow(self):
        """Test basic scheduling workflow with temporal dependencies."""
        # Define some tasks with temporal durations
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 2}, ["T1"])
        self.scheduler.add_task("T3", {"epoch": 1, "step": 500}, ["T2"])

        # Schedule the tasks
        scheduled_tasks = self.scheduler.schedule()

        # Verify the schedule length
        assert len(scheduled_tasks) == 3

        # Verify the scheduling order respects dependencies
        task_order = [task["id"] for task in scheduled_tasks]
        assert task_order.index("T1") < task_order.index("T2")
        assert task_order.index("T2") < task_order.index("T3")

        # Verify the start/end times are consistent with temporal system
        for i in range(len(scheduled_tasks) - 1):
            current_task = scheduled_tasks[i]
            next_task = scheduled_tasks[i + 1]

            # If next task depends on current, check that it starts after current ends
            if current_task["id"] in next_task["dependencies"]:
                comparison = self.temporal.compare_timepoints(
                    current_task["end"], next_task["start"]
                )
                assert comparison <= 0, f"{current_task['id']} should end before {next_task['id']} starts"

    def test_schedule_with_custom_temporal_system(self):
        """Test scheduling with a custom temporal system configuration."""
        # Create a custom temporal system
        custom_config = [
            {"name": "project", "subdivisions": 3},
            {"name": "phase", "subdivisions": 4},
            {"name": "task", "subdivisions": None, "is_base": True},
        ]
        custom_temporal = AgentTemporal(custom_config)
        custom_scheduler = TaskScheduler(custom_temporal)

        # Add tasks with custom time units
        custom_scheduler.add_task("P1", {"project": 0, "phase": 1})
        custom_scheduler.add_task("P2", {"project": 0, "phase": 2}, ["P1"])

        # Schedule tasks
        scheduled_tasks = custom_scheduler.schedule()

        # Verify the schedule
        assert len(scheduled_tasks) == 2
        assert scheduled_tasks[0]["id"] == "P1"
        assert scheduled_tasks[1]["id"] == "P2"

        # Verify the temporal consistency
        p1_end = scheduled_tasks[0]["end"]
        p2_start = scheduled_tasks[1]["start"]

        # P2 should start at or after P1 ends
        comparison = custom_temporal.compare_timepoints(p1_end, p2_start)
        assert comparison <= 0

    def test_multi_agent_scheduling(self):
        """Test scheduling with multiple agents."""
        # Add tasks with varying durations
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"step": 150})  # No dependency, can run in parallel
        self.scheduler.add_task("T3", {"step": 200}, ["T1"])
        self.scheduler.add_task("T4", {"step": 50}, ["T2"])

        # Schedule with 2 agents
        scheduled_tasks = self.scheduler.schedule(agent_count=2)

        # Verify all tasks are scheduled
        assert len(scheduled_tasks) == 4

        # Group tasks by agent
        agent_tasks = {}
        for task in scheduled_tasks:
            agent = task["agent"]
            if agent not in agent_tasks:
                agent_tasks[agent] = []
            agent_tasks[agent].append(task)

        # Verify each agent's tasks don't overlap in time
        for agent_id, tasks in agent_tasks.items():
            # Sort tasks by start time
            sorted_tasks = sorted(tasks, key=lambda t: self.temporal.to_base_units(t["start"]))

            # Check for overlaps
            for i in range(len(sorted_tasks) - 1):
                current_task = sorted_tasks[i]
                next_task = sorted_tasks[i + 1]

                # Current task should end before or at the same time next task starts
                comparison = self.temporal.compare_timepoints(
                    current_task["end"], next_task["start"]
                )
                assert comparison <= 0, f"Tasks {current_task['id']} and {next_task['id']} overlap for agent {agent_id}"

    def test_schedule_visualization_data(self):
        """Test the integration between scheduling and visualization data generation."""
        # Create tasks
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 1}, ["T1"])

        # Schedule tasks
        self.scheduler.schedule()

        # Generate visualization data
        viz_data = self.scheduler.visualize_schedule()

        # Verify the visualization data
        assert len(viz_data) == 2
        assert viz_data[0]["id"] == "T1"
        assert viz_data[1]["id"] == "T2"

        # Check that the visualization data has the required fields
        for task_data in viz_data:
            assert "id" in task_data
            assert "start" in task_data
            assert "end" in task_data
            assert "duration" in task_data
            assert "agent" in task_data
            assert "dependencies" in task_data

        # Verify T2 starts after T1 ends
        t1_end = viz_data[0]["end"]
        t2_start = viz_data[1]["start"]
        assert t2_start >= t1_end
```

## Adaptive Temporal System Integration Tests

The following example shows how to test the integration between `AdaptiveAgentTemporal` and other components.

```python
"""
Integration test suite for AdaptiveAgentTemporal and its interactions
with other components of the Timekeeper framework.
"""

import pytest
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal
from timekeeper.task_scheduler import TaskScheduler


class TestAdaptiveTemporalIntegration:
    """Test suite for AdaptiveAgentTemporal integration with other components."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.adaptive = AdaptiveAgentTemporal(agent_count=2)
        self.scheduler = TaskScheduler(self.adaptive)

    def test_adaptation_effect_on_scheduling(self):
        """Test how temporal adaptation affects task scheduling."""
        # Add tasks
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 2}, ["T1"])
        self.scheduler.add_task("T3", {"epoch": 1}, ["T2"])

        # Schedule before adaptation
        before_schedule = self.scheduler.schedule()

        # Record key metrics before adaptation
        before_end_time = self.adaptive.to_base_units(before_schedule[-1]["end"])

        # Simulate many operations focused on a specific unit
        # This should trigger adaptation
        for _ in range(150):
            tp = self.adaptive.create_timepoint(step=1)
            self.adaptive.add_time(tp, step=1)
            self.adaptive.track_operation("add", "step")

        # Schedule after adaptation
        after_schedule = self.scheduler.schedule()

        # Record key metrics after adaptation
        after_end_time = self.adaptive.to_base_units(after_schedule[-1]["end"])

        # Verify that the schedule structure is preserved
        assert len(after_schedule) == 3
        assert [task["id"] for task in after_schedule] == ["T1", "T2", "T3"]

        # The absolute time values might change due to adaptation
        # but the relative ordering should be preserved
        assert after_schedule[0]["id"] == "T1"
        assert after_schedule[1]["id"] == "T2"
        assert after_schedule[2]["id"] == "T3"

        # Check that dependencies are still respected
        for task in after_schedule:
            if task["dependencies"]:
                for dep_id in task["dependencies"]:
                    dep_task = next(t for t in after_schedule if t["id"] == dep_id)
                    comparison = self.adaptive.compare_timepoints(
                        dep_task["end"], task["start"]
                    )
                    assert comparison <= 0

    def test_human_time_conversion_with_adaptation(self):
        """Test human time conversion before and after adaptation."""
        # Create a timepoint
        agent_tp = self.adaptive.create_timepoint(epoch=1, cycle=10, step=30)

        # Convert to human time before adaptation
        human_before = self.adaptive.to_human_time(agent_tp)

        # Simulate operations that trigger adaptation
        for _ in range(150):
            self.adaptive.track_operation("to_human", "epoch")

        # Convert the same timepoint to human time after adaptation
        human_after = self.adaptive.to_human_time(agent_tp)

        # The absolute values might change, but the timepoint should still
        # represent the same moment in time
        agent_tp_before = self.adaptive.from_human_time(human_before)
        agent_tp_after = self.adaptive.from_human_time(human_after)

        # The base unit representation should be equivalent
        before_base = self.adaptive.to_base_units(agent_tp_before)
        after_base = self.adaptive.to_base_units(agent_tp_after)

        # Allow for small floating-point differences
        assert abs(before_base - after_base) < 1e-10

    def test_add_time_unit_effect(self):
        """Test the effect of adding a new time unit during execution."""
        # Schedule tasks with initial time units
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 2}, ["T1"])

        initial_schedule = self.scheduler.schedule()

        # Add a new time unit between existing units
        self.adaptive.add_time_unit("megacycle", 5, after_unit="cycle")

        # Create a new scheduler with the updated adaptive system
        new_scheduler = TaskScheduler(self.adaptive)

        # Add the same tasks
        new_scheduler.add_task("T1", {"step": 100})
        new_scheduler.add_task("T2", {"cycle": 2}, ["T1"])

        # Schedule with the new time unit structure
        new_schedule = new_scheduler.schedule()

        # Verify that tasks can still be scheduled correctly
        assert len(new_schedule) == 2
        assert new_schedule[0]["id"] == "T1"
        assert new_schedule[1]["id"] == "T2"

        # Verify that dependencies are still respected
        t1_end = new_schedule[0]["end"]
        t2_start = new_schedule[1]["start"]
        comparison = self.adaptive.compare_timepoints(t1_end, t2_start)
        assert comparison <= 0
```

## Visualization Integration Tests

The following example shows how to test the integration between the visualization module and other components.

```python
"""
Integration test suite for visualization components and their interactions
with other Timekeeper components.
"""

import pytest
import matplotlib.pyplot as plt
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.task_scheduler import TaskScheduler
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal
from timekeeper.visualization import (
    visualize_temporal_hierarchy,
    visualize_timepoint,
    visualize_conversions,
    visualize_schedule
)


class TestVisualizationIntegration:
    """Test suite for visualization integration with other components."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.temporal = AgentTemporal()
        self.scheduler = TaskScheduler(self.temporal)
        plt.close('all')  # Close any open figures

    def test_timepoint_visualization(self):
        """Test that timepoint visualization works with the temporal system."""
        # Create a timepoint
        tp = self.temporal.create_timepoint(epoch=1, cycle=10, step=30)

        # Generate visualization
        fig, ax = visualize_timepoint(self.temporal, tp)

        # Verify that the visualization was created
        assert fig is not None
        assert ax is not None

        # Check that the title contains the timepoint values
        assert "epoch=1" in ax.get_title()
        assert "cycle=10" in ax.get_title()
        assert "step=30" in ax.get_title()

        plt.close(fig)

    def test_schedule_visualization(self):
        """Test that schedule visualization works with the task scheduler."""
        # Create tasks
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 2}, ["T1"])
        self.scheduler.add_task("T3", {"step": 500}, ["T1"])

        # Schedule tasks
        self.scheduler.schedule(agent_count=2)

        # Generate visualization
        fig, ax = visualize_schedule(self.scheduler)

        # Verify that the visualization was created
        assert fig is not None
        assert ax is not None

        # Check that the title is set
        assert "Task Schedule" in ax.get_title()

        plt.close(fig)

    def test_temporal_hierarchy_visualization(self):
        """Test visualization of temporal hierarchy with different configurations."""
        # Standard configuration
        fig, ax = visualize_temporal_hierarchy(self.temporal)
        assert fig is not None
        assert ax is not None
        plt.close(fig)

        # Custom configuration
        custom_config = [
            {"name": "project", "subdivisions": 3},
            {"name": "phase", "subdivisions": 4},
            {"name": "task", "subdivisions": None, "is_base": True},
        ]
        custom_temporal = AgentTemporal(custom_config)

        fig, ax = visualize_temporal_hierarchy(custom_temporal)
        assert fig is not None
        assert ax is not None

        # Check that y-axis labels include all units
        labels = [text.get_text() for text in ax.get_yticklabels()]
        assert "project" in labels
        assert "phase" in labels
        assert "task" in labels

        plt.close(fig)

    def test_adaptive_system_visualization(self):
        """Test visualization with an adaptive temporal system."""
        # Create adaptive system
        adaptive = AdaptiveAgentTemporal(agent_count=2)

        # Visualize before adaptation
        fig1, ax1 = visualize_temporal_hierarchy(adaptive)
        plt.close(fig1)

        # Trigger adaptation
        for _ in range(150):
            tp = adaptive.create_timepoint(step=1)
            adaptive.add_time(tp, step=1)
            adaptive.track_operation("add", "step")

        # Visualize after adaptation
        fig2, ax2 = visualize_temporal_hierarchy(adaptive)
        assert fig2 is not None
        assert ax2 is not None

        plt.close(fig2)

        # Create conversion visualization after adaptation
        fig3, ax3 = visualize_conversions(adaptive)
        assert fig3 is not None
        assert ax3 is not None

        plt.close(fig3)
```

## End-to-End Workflow Tests

This example demonstrates how to test a complete workflow through all components.

```python
"""
End-to-end integration tests for the Timekeeper framework.
These tests verify that all components work together correctly in complete workflows.
"""

import pytest
import matplotlib.pyplot as plt
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.task_scheduler import TaskScheduler
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal
from timekeeper.visualization import (
    visualize_temporal_hierarchy,
    visualize_timepoint,
    visualize_conversions,
    visualize_schedule
)


class TestEndToEndWorkflows:
    """Test suite for end-to-end workflows in the Timekeeper framework."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        plt.close('all')  # Close any open figures

    def test_basic_end_to_end_workflow(self):
        """Test a complete basic workflow through all components."""
        # 1. Create a temporal system
        temporal = AgentTemporal()

        # 2. Create and manipulate timepoints
        t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
        t2 = temporal.add_time(t1, cycle=5, step=20)

        # Verify timepoint operations
        diff = temporal.time_difference(t1, t2)
        assert diff["cycle"] == 5
        assert diff["step"] == 20

        # 3. Visualize timepoints
        fig1, ax1 = visualize_timepoint(temporal, t1)
        plt.close(fig1)

        # 4. Create a scheduler
        scheduler = TaskScheduler(temporal)

        # 5. Add tasks
        scheduler.add_task("T1", {"step": 100})
        scheduler.add_task("T2", {"cycle": 1}, ["T1"])
        scheduler.add_task("T3", {"step": 300}, ["T2"])

        # 6. Schedule tasks
        scheduled_tasks = scheduler.schedule(agent_count=2)

        # Verify schedule
        assert len(scheduled_tasks) == 3
        assert scheduled_tasks[0]["id"] == "T1"
        assert scheduled_tasks[1]["id"] == "T2"
        assert scheduled_tasks[2]["id"] == "T3"

        # 7. Visualize schedule
        fig2, ax2 = visualize_schedule(scheduler)
        plt.close(fig2)

        # 8. Convert between agent and human time
        human_time = temporal.to_human_time(t1)
        agent_time = temporal.from_human_time(human_time)

        # Verify human-agent time conversion
        assert temporal.compare_timepoints(t1, agent_time) == 0

    def test_adaptive_end_to_end_workflow(self):
        """Test a complete workflow with adaptive temporal system."""
        # 1. Create an adaptive temporal system
        adaptive = AdaptiveAgentTemporal(agent_count=2)

        # 2. Visualize initial temporal hierarchy
        fig1, ax1 = visualize_temporal_hierarchy(adaptive)
        plt.close(fig1)

        # 3. Create a scheduler
        scheduler = TaskScheduler(adaptive)

        # 4. Add tasks
        scheduler.add_task("T1", {"step": 100})
        scheduler.add_task("T2", {"cycle": 1}, ["T1"])
        scheduler.add_task("T3", {"step": 300}, ["T2"])

        # 5. Schedule tasks before adaptation
        before_schedule = scheduler.schedule(agent_count=2)

        # 6. Visualize schedule before adaptation
        fig2, ax2 = visualize_schedule(scheduler)
        plt.close(fig2)

        # 7. Trigger adaptation
        for _ in range(150):
            tp = adaptive.create_timepoint(step=1)
            adaptive.add_time(tp, step=1)
            adaptive.track_operation("add", "step")

        # 8. Visualize adapted temporal hierarchy
        fig3, ax3 = visualize_temporal_hierarchy(adaptive)
        plt.close(fig3)

        # 9. Reschedule with adapted system
        after_schedule = scheduler.schedule(agent_count=2)

        # 10. Visualize schedule after adaptation
        fig4, ax4 = visualize_schedule(scheduler)
        plt.close(fig4)

        # 11. Verify task order is preserved despite adaptation
        assert [task["id"] for task in before_schedule] == [task["id"] for task in after_schedule]

        # 12. Use a different number of agents
        adaptive.optimize_for_agent_count(3)

        # 13. Schedule with optimized system
        optimized_schedule = scheduler.schedule(agent_count=3)

        # 14. Verify dependencies are still respected
        for task in optimized_schedule:
            if task["dependencies"]:
                for dep_id in task["dependencies"]:
                    dep_task = next(t for t in optimized_schedule if t["id"] == dep_id)
                    comparison = adaptive.compare_timepoints(
                        dep_task["end"], task["start"]
                    )
                    assert comparison <= 0
```

## Property-Based Tests

Here's an example of how to implement property-based tests using the Hypothesis library.

```python
"""
Property-based tests for the Timekeeper framework.
These tests verify mathematical properties of the temporal operations.
"""

import pytest
from hypothesis import given, strategies as st
from timekeeper.agent_temporal import AgentTemporal


# Define strategies for generating timepoints
@st.composite
def timepoint_strategy(draw, temporal_system=None):
    """Generate random timepoints that are valid for the given temporal system."""
    if temporal_system is None:
        temporal_system = AgentTemporal()

    # Get unit names
    units = [u["name"] for u in temporal_system.units]

    # Generate values for each unit
    values = {}
    for i, unit in enumerate(temporal_system.units):
        # For all but the base unit, respect subdivision limits
        if i < len(temporal_system.units) - 1:
            subdiv = temporal_system.units[i]["subdivisions"]
            values[unit["name"]] = draw(st.integers(min_value=0, max_value=subdiv * 2))
        else:
            # Base unit can have a wider range
            values[unit["name"]] = draw(st.integers(min_value=0, max_value=1000))

    return values


class TestTemporalProperties:
    """Property-based tests for the temporal system."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.temporal = AgentTemporal()

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy(), tp3=timepoint_strategy())
    def test_addition_associativity(self, tp1, tp2, tp3):
        """Test that timepoint addition is associative: (a + b) + c = a + (b + c)."""
        # Create normalized timepoints
        t1 = self.temporal.normalize(tp1)
        t2 = self.temporal.normalize(tp2)
        t3 = self.temporal.normalize(tp3)

        # (t1 + t2) + t3
        t1_plus_t2 = self.temporal.add_time(t1, **t2)
        result1 = self.temporal.add_time(t1_plus_t2, **t3)

        # t1 + (t2 + t3)
        t2_plus_t3 = self.temporal.add_time(t2, **t3)
        result2 = self.temporal.add_time(t1, **t2_plus_t3)

        # Verify associativity
        assert self.temporal.compare_timepoints(result1, result2) == 0

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy())
    def test_addition_commutativity(self, tp1, tp2):
        """Test that timepoint addition is commutative: a + b = b + a."""
        # Create normalized timepoints
        t1 = self.temporal.normalize(tp1)
        t2 = self.temporal.normalize(tp2)

        # t1 + t2
        result1 = self.temporal.add_time(t1, **t2)

        # t2 + t1
        result2 = self.temporal.add_time(t2, **t1)

        # Verify commutativity
        assert self.temporal.compare_timepoints(result1, result2) == 0

    @given(tp=timepoint_strategy())
    def test_addition_identity(self, tp):
        """Test that the zero timepoint is the identity for addition: a + 0 = a."""
        # Create normalized timepoint
        t = self.temporal.normalize(tp)

        # Create zero timepoint
        zero = self.temporal.create_timepoint()

        # t + 0
        result = self.temporal.add_time(t, **zero)

        # Verify identity property
        assert self.temporal.compare_timepoints(result, t) == 0

    @given(tp=timepoint_strategy())
    def test_normalization_idempotence(self, tp):
        """Test that normalizing an already normalized timepoint has no effect."""
        # Normalize once
        t1 = self.temporal.normalize(tp)

        # Normalize again
        t2 = self.temporal.normalize(t1)

        # Verify idempotence
        assert self.temporal.compare_timepoints(t1, t2) == 0

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy())
    def test_comparison_transitivity(self, tp1, tp2):
        """Test that timepoint comparison is transitive."""
        # Create a third timepoint that is the sum of the first two
        tp3 = self.temporal.add_time(tp1, **tp2)

        # If tp1 <= tp2 and tp2 <= tp3, then tp1 <= tp3
        comp1_2 = self.temporal.compare_timepoints(tp1, tp2)
        comp2_3 = self.temporal.compare_timepoints(tp2, tp3)
        comp1_3 = self.temporal.compare_timepoints(tp1, tp3)

        if comp1_2 <= 0 and comp2_3 <= 0:
            assert comp1_3 <= 0

    @given(tp=timepoint_strategy())
    def test_human_time_conversion_roundtrip(self, tp):
        """Test that converting to human time and back preserves the timepoint."""
        # Normalize the original timepoint
        original = self.temporal.normalize(tp)

        # Convert to human time
        human = self.temporal.to_human_time(original)

        # Convert back to agent time
        roundtrip = self.temporal.from_human_time(human)

        # Check that all units in both timepoints are equivalent
        # We only check units that are mapped in both directions
        for unit in original.keys():
            if unit in {"epoch", "cycle", "step"}:  # Units with human mappings
                assert original[unit] == roundtrip[unit]
```

## Performance Tests

Here's an example of how to implement performance tests.

```python
"""
Performance tests for the Timekeeper framework.
These tests verify that operations meet performance requirements.
"""

import pytest
import time
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.task_scheduler import TaskScheduler
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal


class TestPerformance:
    """Performance tests for the Timekeeper framework."""

    def test_timepoint_creation_performance(self):
        """Test that timepoint creation meets performance requirements."""
        temporal = AgentTemporal()

        # Measure time to create many timepoints
        start_time = time.time()
        for i in range(10000):
            tp = temporal.create_timepoint(epoch=i % 10, cycle=i % 60, step=i % 1000)
        end_time = time.time()

        # Should be able to create at least 100,000 timepoints/second on average hardware
        timepoints_per_second = 10000 / (end_time - start_time)
        assert timepoints_per_second > 100000, f"Only achieved {timepoints_per_second:.2f} timepoints/second"

    def test_scheduling_performance(self):
        """Test that task scheduling meets performance requirements."""
        temporal = AgentTemporal()
        scheduler = TaskScheduler(temporal)

        # Create a large number of tasks with simple dependencies
        for i in range(100):
            deps = [f"T{i-1}"] if i > 0 else []
            scheduler.add_task(f"T{i}", {"step": 10}, deps)

        # Measure scheduling time
        start_time = time.time()
        scheduled = scheduler.schedule()
        end_time = time.time()

        # Scheduling 100 tasks should take less than 100ms
        scheduling_time = (end_time - start_time) * 1000
        assert scheduling_time < 100, f"Scheduling took {scheduling_time:.2f}ms"

    def test_adaptive_system_performance(self):
        """Test that adaptive system operations meet performance requirements."""
        adaptive = AdaptiveAgentTemporal(agent_count=2)

        # Measure adaptation performance
        start_time = time.time()
        for _ in range(1000):
            tp = adaptive.create_timepoint(step=1)
            adaptive.add_time(tp, step=1)
            adaptive.track_operation("add", "step")
        end_time = time.time()

        # 1000 operations with tracking should take less than 1 second
        operation_time = end_time - start_time
        assert operation_time < 1.0, f"1000 operations took {operation_time:.2f}s"

    def test_visualization_performance(self):
        """Test that visualization operations meet performance requirements."""
        import matplotlib.pyplot as plt
        from timekeeper.visualization import (
            visualize_temporal_hierarchy,
            visualize_timepoint,
            visualize_conversions,
            visualize_schedule
        )

        temporal = AgentTemporal()
        scheduler = TaskScheduler(temporal)

        # Add a moderate number of tasks
        for i in range(20):
            deps = [f"T{i-1}"] if i > 0 else []
            scheduler.add_task(f"T{i}", {"step": 10}, deps)

        scheduler.schedule()

        # Measure visualization time
        start_time = time.time()
        fig, ax = visualize_schedule(scheduler)
        plt.close(fig)
        end_time = time.time()

        # Visualizing a 20-task schedule should take less than 500ms
        visualization_time = (end_time - start_time) * 1000
        assert visualization_time < 500, f"Visualization took {visualization_time:.2f}ms"
```

These examples cover the major integration test categories needed for the Timekeeper MVP. They can be used as templates when implementing the actual test files with the Code mode.
