# Complete Workflow Example: Task Scheduling with Adaptive Time

This example demonstrates a complete workflow using the Timekeeper framework, including:

1. Creating custom temporal systems
2. Defining and scheduling tasks
3. Visualizing timepoints and schedules
4. Adapting the temporal system based on usage patterns

## Setup

First, we'll import the necessary components:

```python
from timekeeper.agent_temporal import AgentTemporal
from timekeeper.task_scheduler import TaskScheduler
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal
from timekeeper.visualization import (
    visualize_temporal_hierarchy,
    visualize_timepoint,
    visualize_conversions,
    visualize_schedule
)

import matplotlib.pyplot as plt
```

## Creating a Custom Temporal System

Let's create a custom temporal system for a project management scenario:

```python
# Define a custom hierarchy of time units
custom_config = [
    {"name": "project", "subdivisions": 4},     # 1 project = 4 phases
    {"name": "phase", "subdivisions": 5},       # 1 phase = 5 iterations
    {"name": "iteration", "subdivisions": 10},  # 1 iteration = 10 days
    {"name": "day", "subdivisions": 8},         # 1 day = 8 hours
    {"name": "hour", "subdivisions": None, "is_base": True}  # Base unit
]

# Create the temporal system
project_time = AgentTemporal(custom_config)

# Visualize the temporal hierarchy
fig, ax = visualize_temporal_hierarchy(project_time)
plt.title("Project Management Temporal Hierarchy")
plt.show()

# Visualize conversion factors
fig, ax = visualize_conversions(project_time)
plt.title("Conversion Factors Between Project Time Units")
plt.show()
```

## Creating and Manipulating Timepoints

Now let's create some timepoints and perform operations:

```python
# Create a timepoint: Phase 1, Iteration 3, Day 2, Hour 4
milestone1 = project_time.create_timepoint(phase=1, iteration=3, day=2, hour=4)
print("Milestone 1:", milestone1)

# Create another timepoint
milestone2 = project_time.create_timepoint(phase=2, iteration=1, day=5, hour=2)
print("Milestone 2:", milestone2)

# Calculate the time difference
difference = project_time.time_difference(milestone1, milestone2)
print("Time difference:", difference)

# Visualize the timepoints
fig, ax = visualize_timepoint(project_time, milestone1)
plt.title("Milestone 1 Timepoint")
plt.show()

fig, ax = visualize_timepoint(project_time, milestone2)
plt.title("Milestone 2 Timepoint")
plt.show()

# Add time to a timepoint
milestone3 = project_time.add_time(milestone1, iteration=2, day=3)
print("Milestone 3 (Milestone 1 + 2 iterations and 3 days):", milestone3)
```

## Task Scheduling

Let's define and schedule some project tasks:

```python
# Create a scheduler using our temporal system
scheduler = TaskScheduler(project_time)

# Define tasks with durations and dependencies
scheduler.add_task("Requirements", {"iteration": 1})
scheduler.add_task("Design", {"iteration": 1, "day": 5}, ["Requirements"])
scheduler.add_task("Backend", {"iteration": 2}, ["Design"])
scheduler.add_task("Frontend", {"iteration": 1, "day": 8}, ["Design"])
scheduler.add_task("Integration", {"iteration": 1}, ["Backend", "Frontend"])
scheduler.add_task("Testing", {"day": 8}, ["Integration"])
scheduler.add_task("Deployment", {"day": 2}, ["Testing"])
scheduler.add_task("Documentation", {"iteration": 1}, ["Design"])

# Schedule the tasks with 2 team members (agents)
scheduled_tasks = scheduler.schedule(agent_count=2)

# Print the schedule
print("\nTask Schedule:")
for task in scheduled_tasks:
    print(f"Task: {task['id']}")
    print(f"  Start: {task['start']}")
    print(f"  End: {task['end']}")
    print(f"  Agent: {task['agent']}")

# Visualize the schedule
fig, ax = visualize_schedule(scheduler)
plt.title("Project Schedule")
plt.show()
```

## Adaptive Temporal System

Now let's use an adaptive temporal system that adjusts based on usage patterns:

```python
# Create an adaptive temporal system with the same initial configuration
adaptive_time = AdaptiveAgentTemporal(custom_config, agent_count=2)

# Create a scheduler using our adaptive system
adaptive_scheduler = TaskScheduler(adaptive_time)

# Add the same tasks
adaptive_scheduler.add_task("Requirements", {"iteration": 1})
adaptive_scheduler.add_task("Design", {"iteration": 1, "day": 5}, ["Requirements"])
adaptive_scheduler.add_task("Backend", {"iteration": 2}, ["Design"])
adaptive_scheduler.add_task("Frontend", {"iteration": 1, "day": 8}, ["Design"])
adaptive_scheduler.add_task("Integration", {"iteration": 1}, ["Backend", "Frontend"])
adaptive_scheduler.add_task("Testing", {"day": 8}, ["Integration"])
adaptive_scheduler.add_task("Deployment", {"day": 2}, ["Testing"])
adaptive_scheduler.add_task("Documentation", {"iteration": 1}, ["Design"])

# Generate initial schedule
initial_schedule = adaptive_scheduler.schedule(agent_count=2)

# Visualize the initial schedule
fig, ax = visualize_schedule(adaptive_scheduler)
plt.title("Initial Project Schedule (Adaptive)")
plt.show()

# Simulate many operations with day-focused activities
print("\nSimulating day-focused operations...")
day_tp = adaptive_time.create_timepoint(day=1)
for _ in range(150):
    adaptive_time.add_time(day_tp, day=1)
    adaptive_time.track_operation("add", "day")

# Print the adapted unit configuration
print("\nAdapted Time Unit Configuration:")
for i, unit in enumerate(adaptive_time.units):
    if i < len(adaptive_time.units) - 1:  # Not the last unit
        subdiv = unit["subdivisions"]
        next_unit = adaptive_time.units[i+1]["name"]
        print(f"1 {unit['name']} = {subdiv} {next_unit}s")
    else:
        print(f"{unit['name']} (base unit)")

# Visualize the new temporal hierarchy
fig, ax = visualize_temporal_hierarchy(adaptive_time)
plt.title("Adapted Project Management Temporal Hierarchy")
plt.show()

# Re-schedule with the adapted system
adapted_schedule = adaptive_scheduler.schedule(agent_count=2)

# Visualize the adapted schedule
fig, ax = visualize_schedule(adaptive_scheduler)
plt.title("Adapted Project Schedule")
plt.show()

# Compare the schedules
print("\nImpact of Adaptation on Schedule:")
for i, task in enumerate(initial_schedule):
    adapted_task = adapted_schedule[i]
    initial_duration = adaptive_time.to_base_units(task["end"]) - adaptive_time.to_base_units(task["start"])
    adapted_duration = adaptive_time.to_base_units(adapted_task["end"]) - adaptive_time.to_base_units(adapted_task["start"])
    print(f"Task: {task['id']}")
    print(f"  Initial duration (hours): {initial_duration}")
    print(f"  Adapted duration (hours): {adapted_duration}")
    print(f"  Difference: {adapted_duration - initial_duration} hours")
```

## Converting Between Agent Time and Human Time

Finally, let's demonstrate conversion between agent time and human time:

```python
# Convert project timepoint to human time
project_timepoint = adaptive_time.create_timepoint(project=0, phase=1, iteration=2, day=3, hour=4)
human_time = adaptive_time.to_human_time(project_timepoint)
print("\nProject timepoint:", project_timepoint)
print("Human time equivalent:", human_time)

# Convert human time to project time
human_dict = {"hours": 6, "minutes": 30}
project_time_from_human = adaptive_time.from_human_time(human_dict)
print("\nHuman time:", human_dict)
print("Project time equivalent:", project_time_from_human)
```

## Conclusion

This example has demonstrated:

1. Creating a custom temporal system for project management
2. Creating and manipulating timepoints
3. Scheduling tasks with dependencies
4. Visualizing timepoints, schedules, and temporal hierarchies
5. Using an adaptive temporal system that adjusts based on usage
6. Converting between agent time and human time

The Timekeeper framework provides a mathematically rigorous approach to handling time in agent systems, with powerful tools for scheduling, adaptation, and visualization.
