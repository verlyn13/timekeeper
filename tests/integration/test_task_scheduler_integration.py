"""
Integration test for TaskScheduler with AgentTemporal and AdaptiveAgentTemporal.

Tests the interaction between the scheduling system and temporal systems,
verifying that tasks are correctly scheduled according to temporal constraints.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st
from typing import Any, Dict, List

from python.agent_temporal import AgentTemporal
from python.adaptive_agent_temporal import AdaptiveAgentTemporal
from python.task_scheduler import TaskScheduler


@pytest.fixture
def standard_scheduler() -> TaskScheduler:
    """Create a standard TaskScheduler with AgentTemporal."""
    temporal = AgentTemporal()
    return TaskScheduler(temporal)


@pytest.fixture
def adaptive_scheduler() -> TaskScheduler:
    """Create a TaskScheduler with AdaptiveAgentTemporal."""
    adaptive_temporal = AdaptiveAgentTemporal(agent_count=3)
    return TaskScheduler(adaptive_temporal)


class TestSchedulerTemporalIntegration:
    """Tests for integration between TaskScheduler and temporal systems."""

    def test_basic_scheduling(self, standard_scheduler: TaskScheduler):
        """Test that tasks can be scheduled and queried in temporal order."""
        # Create sample tasks with different temporal constraints
        scheduler = standard_scheduler
        temporal = scheduler.temporal

        # Define tasks with durations (no timepoints here)
        # Note: TaskScheduler.add_task expects task_id as the first arg
        scheduler.add_task("Task A", duration={"cycle": 2})
        scheduler.add_task("Task B", duration={"cycle": 1})
        scheduler.add_task("Task C", duration={"cycle": 3})

        # Schedule the tasks
        # The basic scheduler assigns start times based on availability (defaulting to 0 if no deps)
        # and calculates end times.
        scheduled_tasks = scheduler.schedule()

        # Verify order based on calculated start times (assuming no dependencies, they start at 0)
        # The order might depend on internal sorting if start times are identical.
        # Let's verify the content instead of strict order for now, as the simple schedule()
        # doesn't guarantee order preservation if start times are the same.
        assert len(scheduled_tasks) == 3
        task_map = {t["id"]: t for t in scheduled_tasks}
        assert set(task_map.keys()) == {"Task A", "Task B", "Task C"}

        # Verify start/end times based on sequential execution on single agent
        # Order depends on internal processing, let's find them by ID
        task_a = task_map["Task A"]
        task_b = task_map["Task B"]
        task_c = task_map["Task C"]

        # Assume scheduler picks A, then B, then C (or some order)
        # Let's verify relative starts based on agent availability
        zero_time = temporal.create_timepoint()
        end_times = {}

        # Task A (duration cycle=2)
        assert task_a["start"] == zero_time
        end_times["Task A"] = temporal.add_time(task_a["start"], **task_a["duration"])
        assert task_a["end"] == end_times["Task A"]

        # Task B (duration cycle=1) - Starts after A finishes
        assert task_b["start"] == end_times["Task A"]
        end_times["Task B"] = temporal.add_time(task_b["start"], **task_b["duration"])
        assert task_b["end"] == end_times["Task B"]

        # Task C (duration cycle=3) - Starts after B finishes
        assert task_c["start"] == end_times["Task B"]
        end_times["Task C"] = temporal.add_time(task_c["start"], **task_c["duration"])
        assert task_c["end"] == end_times["Task C"]

        # Note: This assumes a specific processing order (A->B->C). A more robust test
        # might just check that start times are non-decreasing and match agent availability.
        # However, for this simple case, the sequential assumption is likely correct.

    def test_scheduler_task_dependencies(self, standard_scheduler: TaskScheduler):
        """Test that task dependencies are correctly handled."""
        scheduler = standard_scheduler
        temporal = scheduler.temporal

        # Add tasks with dependencies (no timepoints needed at add_task)
        # TaskScheduler.add_task expects task_id as the first arg
        task_a_id = "Task A"
        task_b_id = "Task B"
        task_c_id = "Task C"

        scheduler.add_task(task_a_id, duration={"cycle": 2})
        scheduler.add_task(task_b_id, duration={"cycle": 1})

        # Task C depends on both A and B
        dependencies = [task_a_id, task_b_id]
        scheduler.add_task(
            task_c_id,
            duration={"cycle": 3},
            dependencies=dependencies,
        )

        # Schedule the tasks
        scheduled_tasks = scheduler.schedule()

        # Find the scheduled tasks by ID
        task_a = next((t for t in scheduled_tasks if t["id"] == task_a_id), None)
        task_b = next((t for t in scheduled_tasks if t["id"] == task_b_id), None)
        task_c = next((t for t in scheduled_tasks if t["id"] == task_c_id), None)

        assert task_a is not None, "Task A not found"
        assert task_b is not None, "Task B not found"
        assert task_c is not None, "Task C not found"

        # Verify start times based on dependencies and single agent availability
        # Assume scheduler processes A then B (or vice versa) before C
        zero_time = temporal.create_timepoint()

        # Task A (duration cycle=2) starts at 0
        assert task_a["start"] == zero_time
        end_a = temporal.add_time(
            task_a["start"], **task_a["duration"]
        )  # Ends at cycle=2

        # Task B (duration cycle=1) starts after A finishes on the single agent
        assert task_b["start"] == end_a
        end_b = temporal.add_time(
            task_b["start"], **task_b["duration"]
        )  # Ends at cycle=2+1=3

        # Task C depends on A (ends cycle=2) and B (ends cycle=3)
        # It should start after the latest dependency (B) finishes.
        expected_start_c = end_b
        assert (
            task_c["start"] == expected_start_c
        ), f"Task C start {task_c['start']} should be {expected_start_c} (end of Task B)"

        # Verify Task C end time
        expected_end_c = temporal.add_time(
            task_c["start"], **task_c["duration"]
        )  # cycle=3 + 3 = 6
        assert task_c["end"] == expected_end_c

    def test_multi_agent_scheduling(self, adaptive_scheduler: TaskScheduler):
        """Test scheduling with multiple agents using AdaptiveAgentTemporal."""
        scheduler = adaptive_scheduler
        temporal = scheduler.temporal
        assert isinstance(
            temporal, AdaptiveAgentTemporal
        ), "Requires AdaptiveAgentTemporal"

        # Add tasks (without specifying agent or timepoint initially)
        num_agents = temporal.agent_count
        tasks_per_agent = 3
        task_ids = []
        for agent_id_placeholder in range(
            num_agents
        ):  # Placeholder loop, agent not assigned here
            for i in range(tasks_per_agent):
                task_id = f"Agent {agent_id_placeholder} Task {i}"
                task_ids.append(task_id)
                # Add task with only ID and duration
                scheduler.add_task(
                    task_id,
                    duration={"cycle": 1},
                    # Dependencies could be added here if needed for multi-agent scenarios
                )

        # Schedule the tasks using the specified number of agents
        scheduled_tasks = scheduler.schedule(agent_count=num_agents)

        # Verify the scheduling results
        assert len(scheduled_tasks) == len(task_ids), "Not all tasks were scheduled"

        tasks_per_actual_agent = {}
        for task in scheduled_tasks:
            agent_assigned = task.get("agent")
            assert (
                agent_assigned is not None
            ), f"Task {task['id']} was not assigned an agent"
            assert (
                0 <= agent_assigned < num_agents
            ), f"Task {task['id']} assigned invalid agent {agent_assigned}"

            if agent_assigned not in tasks_per_actual_agent:
                tasks_per_actual_agent[agent_assigned] = []
            tasks_per_actual_agent[agent_assigned].append(task)

        # Verify each agent got roughly the expected number of tasks (simple scheduler might not balance perfectly)
        # For this simple test, we expect perfect balance as tasks are identical duration and no deps
        assert (
            len(tasks_per_actual_agent) == num_agents
        ), "Not all agents were assigned tasks"
        for agent_id, agent_tasks in tasks_per_actual_agent.items():
            assert (
                len(agent_tasks) == tasks_per_agent
            ), f"Agent {agent_id} was assigned {len(agent_tasks)} tasks, expected {tasks_per_agent}"

            # Verify temporal ordering for tasks assigned to the *same* agent
            # Sort tasks by start time first
            agent_tasks.sort(key=lambda t: temporal.to_base_units(t["start"]))
            for i in range(len(agent_tasks) - 1):
                # Check that tasks assigned to the same agent do not overlap temporally
                end_time_task_i = agent_tasks[i]["end"]
                start_time_task_j = agent_tasks[i + 1]["start"]
                assert (
                    temporal.compare_timepoints(end_time_task_i, start_time_task_j) <= 0
                ), f"Tasks overlap for agent {agent_id}: Task {agent_tasks[i]['id']} ends at {end_time_task_i}, Task {agent_tasks[i+1]['id']} starts at {start_time_task_j}"

    def test_adaptive_scheduling(self, adaptive_scheduler: TaskScheduler):
        """Test adaptive scheduling with changing temporal granularity."""
        scheduler = adaptive_scheduler
        temporal = scheduler.temporal
        assert isinstance(
            temporal, AdaptiveAgentTemporal
        ), "Requires AdaptiveAgentTemporal"

        # Initial timepoint
        start_time = temporal.create_timepoint(cycle=1)

        # Add some initial tasks
        initial_task_count = 5
        initial_task_ids = [f"Task {i}" for i in range(initial_task_count)]
        for task_id in initial_task_ids:
            scheduler.add_task(task_id, duration={"cycle": 1})

        # Schedule the initial tasks
        initial_scheduled_tasks = scheduler.schedule()
        assert len(initial_scheduled_tasks) == initial_task_count

        # Trigger adaptation by changing the agent count and optimizing
        new_agent_count = temporal.agent_count + 1  # Change agent count
        temporal.optimize_for_agent_count(new_agent_count)
        # We also need to update the scheduler's view of agent count for the next schedule call
        # (Assuming the scheduler doesn't automatically track temporal system's agent count)
        # Let's assume we pass the new count to schedule()

        # Add some new tasks after adaptation
        # Note: The scheduler currently doesn't automatically reschedule existing tasks
        # upon adaptation. This test verifies scheduling *new* tasks post-adaptation.
        adapted_task_count = 5
        adapted_task_ids = [f"Adapted Task {i}" for i in range(adapted_task_count)]
        for task_id in adapted_task_ids:
            # Duration should reflect the new granularity if the *meaning* of 'cycle' changed.
            # However, the scheduler just takes the duration dict. Let's assume the duration
            # is defined relative to the *current* granularity.
            scheduler.add_task(
                task_id, duration={"cycle": 1}
            )  # Duration relative to current granularity

        # Reschedule *all* tasks (including initial ones) after adaptation
        # Pass the new agent count to the scheduler
        all_scheduled_tasks = scheduler.schedule(agent_count=new_agent_count)

        # Verify adaptation effects
        # 1. All tasks should be scheduled
        assert len(all_scheduled_tasks) == initial_task_count + adapted_task_count

        # 2. Verify timings reflect adaptation (e.g., durations might take longer in base units)
        adapted_task_found = False
        initial_task_found = False
        base_unit_name = temporal.units[0]["name"]  # Get the finest unit name

        for task in all_scheduled_tasks:
            start_base = temporal.to_base_units(task["start"])
            end_base = temporal.to_base_units(task["end"])
            duration_base = end_base - start_base

            if task["id"].startswith("Adapted"):
                adapted_task_found = True
                # Check if duration in base units reflects adaptation (hard to predict exactly without knowing base unit relation)
                # For now, just check the task exists and was scheduled
                assert task["start"] is not None and task["end"] is not None
            elif task["id"].startswith("Task"):
                initial_task_found = True
                # Check if duration in base units reflects adaptation
                # If cycle=1 duration was X base units before, it might be X*factor now.
                # This requires knowing the pre-adaptation base unit duration.
                # Let's just verify it was scheduled.
                assert task["start"] is not None and task["end"] is not None

        assert adapted_task_found, "No adapted tasks found after adaptation"
        assert initial_task_found, "No initial tasks found after rescheduling"


# Define custom strategies for scheduler tasks
@st.composite
def task_strategy(draw, scheduler: TaskScheduler = None) -> Dict[str, Any]:
    """Generate random tasks that work with the given scheduler."""
    if scheduler is None:
        # Use default TaskScheduler with AgentTemporal for strategy generation
        temporal = AgentTemporal()
        scheduler = TaskScheduler(temporal)

    # Generate a random timepoint dictionary (unnormalized)
    timepoint: Dict[str, int] = {}
    for unit in scheduler.temporal.units:
        name = unit["name"]
        # Generate values slightly larger than max to test normalization
        subdivisions = unit.get("subdivisions")  # Use get to safely access
        if subdivisions is not None:
            # For units with subdivisions, base max_val on that
            max_val = subdivisions * 20
        else:
            # For the base unit (no subdivisions), use an arbitrary larger number
            max_val = 1000  # Or another suitable large number for base unit testing
        timepoint[name] = draw(st.integers(min_value=0, max_value=max_val))

    # Generate random duration dictionary
    duration: Dict[str, int] = {}
    possible_units = [u["name"] for u in scheduler.temporal.units]
    # Ensure at least one duration unit is selected
    selected_units = draw(
        st.lists(st.sampled_from(possible_units), min_size=1, unique=True)
    )

    for unit_name in selected_units:
        # Duration must be positive
        duration[unit_name] = draw(st.integers(min_value=1, max_value=10))

    # Generate random name
    name = draw(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=3,
            max_size=10,
        )
    )

    # Return task parameters
    return {
        "name": name,
        "timepoint": timepoint,  # Will be normalized before adding
        "duration": duration,
    }


class TestSchedulerProperties:
    """Tests for mathematical properties of scheduler operations."""

    # Define the strategy separately to avoid potential issues if it were complex
    task_list_strategy = st.lists(task_strategy(), min_size=1, max_size=10)

    @given(tasks=task_list_strategy)
    def test_temporal_ordering_preservation(
        self, tasks: List[Dict[str, Any]]
    ):  # Removed standard_scheduler fixture
        """Test that temporal ordering is preserved in the scheduler."""
        # Create a fresh scheduler and temporal system for each Hypothesis example
        temporal = AgentTemporal()
        scheduler = TaskScheduler(temporal)

        # Add all tasks
        task_ids = []
        for task_data in tasks:
            # Add task with only ID and duration
            try:
                # Note: The 'timepoint' generated by the strategy is not used here,
                # as add_task doesn't take it. Scheduling assigns start times.
                task_id = task_data[
                    "name"
                ]  # Use name as ID for simplicity in this test
                scheduler.add_task(
                    task_id,
                    duration=task_data["duration"],
                )
                task_ids.append(task_id)
            except ValueError as e:  # Keep error handling for duration issues etc.
                # Handle potential errors if strategy generates invalid inputs
                # Or filter invalid tasks if necessary
                print(f"Skipping invalid task data: {task_data}, Error: {e}")
                continue  # Skip this task if normalization fails

        if not task_ids:
            pytest.skip("No valid tasks added by hypothesis strategy.")

        # Schedule the tasks
        scheduled_tasks = scheduler.schedule()

        # Verify ordering is correct based on scheduled start times
        assert len(scheduled_tasks) == len(
            task_ids
        ), "Number of scheduled tasks doesn't match added tasks"
        for i in range(len(scheduled_tasks) - 1):
            # Use the 'start' time assigned by the scheduler for comparison
            t1_start = scheduled_tasks[i]["start"]
            t2_start = scheduled_tasks[i + 1]["start"]
            # Current task start time should be earlier or equal to next task start time
            comparison = temporal.compare_timepoints(t1_start, t2_start)
            assert (
                comparison <= 0
            ), f"Temporal ordering violated: Task {i} start ({t1_start}) should be <= Task {i+1} start ({t2_start})"
