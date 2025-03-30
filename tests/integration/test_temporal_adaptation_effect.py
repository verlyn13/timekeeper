"""
Fixed version of the temporal adaptation test.
"""


def test_temporal_adaptation_effect(self, adaptive_scheduler, adaptive_temporal):
    """Test that adapting temporal granularity affects scheduling consistently across all agents."""
    scheduler = adaptive_scheduler
    temporal = scheduler.temporal

    # Ensure we have at least 2 agents
    assert temporal.agent_count >= 2

    # Add tasks for different agents
    for agent_id in range(temporal.agent_count):
        for i in range(2):
            scheduler.add_task(f"Agent {agent_id} Task {i}", {"cycle": 1})

    # Schedule initial tasks
    before_tasks = scheduler.schedule(agent_count=temporal.agent_count)

    # Group tasks by agent
    before_agent_tasks = {}
    for task in before_tasks:
        agent_id = task["agent"]
        if agent_id not in before_agent_tasks:
            before_agent_tasks[agent_id] = []
        before_agent_tasks[agent_id].append(task)

    # Capture the cycle duration BEFORE adaptation
    cycle_duration_before = temporal.to_base_units({"cycle": 1})

    # Since AdaptiveAgentTemporal doesn't have a per-agent granularity adjustment,
    # we'll use adjust_subdivision which affects all agents
    target_unit = "cycle"
    original_subdiv = temporal.units[temporal.unit_indices[target_unit]]["subdivisions"]
    temporal.adjust_subdivision(target_unit, original_subdiv * 2)

    # Capture the cycle duration AFTER adaptation
    cycle_duration_after = temporal.to_base_units({"cycle": 1})

    # Add more tasks for all agents
    for agent_id in range(temporal.agent_count):
        scheduler.add_task(f"Agent {agent_id} Task After", {"cycle": 1})

    # Re-schedule all tasks
    after_tasks = scheduler.schedule(agent_count=temporal.agent_count)

    # Find the "Task After" for each agent
    after_agent_tasks = {}
    for task in after_tasks:
        if task["id"].endswith("Task After"):
            agent_id = task["agent"]
            after_agent_tasks[agent_id] = task

    # Verify that the adaptation affected tasks for all agents
    # First, check that "Task After" tasks have expected duration
    for agent_id, task in after_agent_tasks.items():
        # Get the task start and end in base units
        start_base = temporal.to_base_units(task["start"])
        end_base = temporal.to_base_units(task["end"])

        # The duration should match the cycle_duration_after measurement
        actual_duration = end_base - start_base
        assert abs(actual_duration - cycle_duration_after) < 1e-6

    # Verify that all agents' tasks follow correct sequence
    for agent_id in range(temporal.agent_count):
        agent_specific_tasks = [t for t in after_tasks if t["agent"] == agent_id]
        for i in range(len(agent_specific_tasks) - 1):
            current = agent_specific_tasks[i]
            next_task = agent_specific_tasks[i + 1]
            assert temporal.compare_timepoints(current["end"], next_task["start"]) <= 0
