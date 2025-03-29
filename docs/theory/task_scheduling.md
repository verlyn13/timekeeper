# Task Scheduling

## Overview

Task scheduling in the Timekeeper framework provides a mechanism for organizing and sequencing tasks with temporal dependencies. This document provides the formal definitions, properties, and theorems related to task scheduling and connects them to their implementation in the code.

## Definitions

### Definition 1: Task

A task $T_i$ is a 4-tuple $(id_i, \delta_i, D_i, R_i)$ where:

- $id_i$ is a unique identifier for the task
- $\delta_i$ is the duration of the task, represented as a timepoint
- $D_i$ is a set of task identifiers that represent dependencies
- $R_i$ is a set of resource requirements

**Implementation**:
Tasks are represented as dictionaries in the `TaskScheduler` class.

```python
def add_task(self, task_id, duration, dependencies=None, resources=None):
    """
    Add a task to the scheduler.

    Args:
        task_id: Unique identifier for the task
        duration: Dictionary of the form: {'epoch': X, 'cycle': Y, 'step': Z, ...}
                   or partial (zeros will be filled in as needed)
        dependencies: List of task_ids that must complete before this task can start
        resources: Dictionary of resource requirements
    """
    if dependencies is None:
        dependencies = []
    if resources is None:
        resources = {}

    self.tasks.append({
        "id": task_id,
        "duration": duration,
        "dependencies": dependencies,
        "resources": resources,
        "start": None,
        "end": None,
        "agent": None  # Assigned agent, if applicable
    })
```

### Definition 2: Task Dependency

A task $T_j$ depends on task $T_i$ if $id_i \in D_j$, meaning that $T_j$ cannot start until $T_i$ is completed.

**Implementation**:
Dependencies are represented as a list of task IDs in the `dependencies` field of each task.

```python
# A task with dependencies
scheduler.add_task("T2", {"cycle": 2}, ["T1"])  # T2 depends on T1
```

### Definition 3: Schedule

A schedule $S$ is a mapping from tasks to timepoints, assigning a start time $s_i$ and end time $e_i$ to each task $T_i$ such that:

1. $e_i = s_i \oplus \delta_i$ (end time is start time plus duration)
2. For all $j$ where $id_i \in D_j$, $e_i \leq s_j$ (dependencies are satisfied)
3. Resource constraints are satisfied

**Implementation**:
The `schedule` method in the `TaskScheduler` class computes a schedule by assigning start and end times to each task.

```python
def schedule(self, agent_count=1):
    """
    A simple topological order + earliest start approach:
      - For tasks with no unsatisfied deps, schedule them as soon as possible
      - The 'end' time is start + duration (Theorem 29 about schedule feasibility).

    Args:
        agent_count: Number of agents available for task execution

    Returns:
        List of scheduled tasks with start and end times assigned
    """
    # ...
```

### Definition 4: Agent Assignment

In a multi-agent system, an agent assignment $A$ is a mapping from tasks to agents, assigning each task $T_i$ to an agent $a_i$ such that no agent is assigned overlapping tasks.

**Implementation**:
Agent assignments are represented by the `agent` field in each task, and the scheduling algorithm ensures that no agent is assigned overlapping tasks.

```python
# Find the earliest available agent
earliest_agent_idx = 0
earliest_agent_time = agent_availability[0]

for i, availability in enumerate(agent_availability):
    if self.temporal.compare_timepoints(availability, earliest_agent_time) < 0:
        earliest_agent_idx = i
        earliest_agent_time = availability

# ...

# Update task with scheduling info
task["start"] = task_start
task["end"] = task_end
task["agent"] = earliest_agent_idx

# Update agent availability
agent_availability[earliest_agent_idx] = task_end
```

### Definition 5: Earliest Start Time

The earliest start time $EST(T_i)$ for a task $T_i$ is the earliest time at which the task can begin execution, considering its dependencies and resource constraints.

**Implementation**:
The `schedule` method computes the earliest start time for each task based on its dependencies and agent availability.

```python
# Calculate earliest start based on dependencies
dep_end_times = []
for dep_id in task["dependencies"]:
    dep_task = next(s for s in scheduled if s["id"] == dep_id)
    dep_end_times.append(dep_task["end"])

# If there are dependencies, find latest end time
earliest_start = self.temporal.create_timepoint()  # Default to time 0
if dep_end_times:
    earliest_start = max(
        dep_end_times,
        key=lambda t: self.temporal.to_base_units(t)
    )
```

## Properties

### Property 1: Temporal Consistency

A valid schedule maintains temporal consistency, meaning that all timepoints in the schedule are related according to the rules of the temporal universe.

**Implementation**:
The `schedule` method uses the temporal operations from the `AgentTemporal` class to ensure temporal consistency.

```python
# Calculate end time
task_end = self.temporal.add_time(task_start, **task["duration"])
```

### Property 2: Dependency Satisfaction

A valid schedule satisfies all dependencies, meaning that if task $T_j$ depends on task $T_i$, then $e_i \leq s_j$.

**Implementation**:
The scheduling algorithm ensures that tasks are only scheduled after all their dependencies have been completed.

```python
# Find tasks whose dependencies are all in scheduled
ready = [
    t for t in unscheduled
    if all(dep in [s["id"] for s in scheduled] for dep in t["dependencies"])
]
```

### Property 3: Resource Feasibility

A valid schedule respects resource constraints, meaning that the total resource usage at any time does not exceed the available resources.

**Implementation**:
The current implementation focuses on agent resources, ensuring that no agent is assigned overlapping tasks.

```python
# Track per-agent availability
# Each agent's entry is the timepoint when they become available
agent_availability = [
    self.temporal.create_timepoint() for _ in range(agent_count)
]
```

### Property 4: Schedule Optimality

An optimal schedule minimizes the overall completion time or other objective functions while satisfying all constraints.

**Implementation**:
The current implementation uses a simple earliest-start heuristic, which may not always produce optimal schedules but is efficient and produces reasonable results.

## Theorems

### Theorem 1: Schedule Existence

For any set of tasks with acyclic dependencies, there exists at least one valid schedule.

**Proof**:
If the dependency graph is acyclic, a topological sort of the tasks will provide a valid execution order. By scheduling each task as early as possible in this order, a valid schedule is guaranteed to exist.

**Implementation**:
The `schedule` method checks for cycles in the dependency graph and raises an error if they are detected.

```python
if not ready:
    raise ValueError("Dependency cycle detected or unsatisfiable dependencies.")
```

### Theorem 2: Earliest Start Optimality

For a single-agent system with no resource constraints beyond the agent itself, scheduling each task at its earliest possible start time produces an optimal schedule with respect to overall completion time.

**Proof**:
In a single-agent system, delaying any task can only increase the overall completion time. Therefore, scheduling each task as early as possible produces an optimal schedule.

**Implementation**:
The `schedule` method implements the earliest-start policy.

```python
# Final start time is the later of dependency-based and agent-based times
if self.temporal.compare_timepoints(earliest_agent_time, earliest_start) > 0:
    task_start = earliest_agent_time
else:
    task_start = earliest_start
```

### Theorem 3: Multi-Agent Scheduling Complexity

Finding an optimal schedule for a multi-agent system with arbitrary task dependencies is an NP-hard problem.

**Proof**:
The problem can be reduced to the multiprocessor scheduling problem, which is known to be NP-hard.

**Implementation**:
The current implementation uses a greedy heuristic for multi-agent scheduling, which may not produce optimal schedules but is computationally efficient.

```python
# Find the earliest available agent
earliest_agent_idx = 0
earliest_agent_time = agent_availability[0]

for i, availability in enumerate(agent_availability):
    if self.temporal.compare_timepoints(availability, earliest_agent_time) < 0:
        earliest_agent_idx = i
        earliest_agent_time = availability
```

## Applications

### Project Management

Task scheduling can be used for project management, allowing for the organization of project tasks with dependencies and resource constraints.

**Example**:

```python
# Create a project management scheduler
temporal = AgentTemporal()
scheduler = TaskScheduler(temporal)

# Define project tasks
scheduler.add_task("Requirements", {"cycle": 1})
scheduler.add_task("Design", {"cycle": 2}, ["Requirements"])
scheduler.add_task("Implementation", {"cycle": 3}, ["Design"])
scheduler.add_task("Testing", {"cycle": 2}, ["Implementation"])
scheduler.add_task("Deployment", {"cycle": 1}, ["Testing"])

# Schedule the project
project_schedule = scheduler.schedule()
```

### Workflow Optimization

Task scheduling can be used to optimize workflows by identifying critical paths and parallelization opportunities.

**Example**:

```python
# Create a workflow scheduler with multiple agents
scheduler = TaskScheduler(temporal)

# Define workflow tasks with parallel opportunities
scheduler.add_task("T1", {"step": 100})
scheduler.add_task("T2", {"step": 150}, ["T1"])
scheduler.add_task("T3", {"step": 120}, ["T1"])  # Can run in parallel with T2
scheduler.add_task("T4", {"step": 80}, ["T2", "T3"])  # Requires both T2 and T3

# Schedule with multiple agents to exploit parallelism
workflow_schedule = scheduler.schedule(agent_count=2)
```

### Resource Allocation

Task scheduling can be used for resource allocation, ensuring that limited resources are used efficiently.

**Example**:

```python
# Create a resource-constrained scheduler
scheduler = TaskScheduler(temporal)

# Define tasks with resource requirements
scheduler.add_task("T1", {"step": 100}, resources={"CPU": 2, "Memory": 4})
scheduler.add_task("T2", {"step": 150}, resources={"CPU": 1, "Memory": 8})

# In a more advanced implementation, resource constraints would be considered
# during scheduling to ensure that resource usage does not exceed availability
```

## Relationship to Other Concepts

### Temporal Universe

Task scheduling operates within a Temporal Universe, using its operations for timepoint manipulation. See [Temporal Universe](temporal_universe.md) for more details.

### Timepoint Operations

Task scheduling relies on timepoint operations such as addition and comparison. See [Timepoint Operations](timepoint_operations.md) for more details.

### Adaptive Systems

Task scheduling can benefit from adaptive temporal systems, which can optimize the temporal structure for the specific scheduling patterns. See [Adaptive Systems](adaptive_systems.md) for more details.

## Implementation Notes

The implementation of task scheduling in the `TaskScheduler` class focuses on practical scheduling capabilities:

1. **Dependency Management**: The implementation carefully handles task dependencies to ensure that tasks are only scheduled after their dependencies are completed.

2. **Multi-Agent Support**: The implementation supports scheduling tasks across multiple agents, which allows for parallelization of independent tasks.

3. **Visualization Support**: The implementation includes methods for generating visualization data, which can be used to create Gantt charts or other visual representations of the schedule.

4. **Flexibility**: The implementation works with any valid temporal system, including adaptive systems, which allows for customization to different application domains.

The current implementation uses a simple greedy algorithm for scheduling, which may not produce optimal schedules for complex scenarios. Future enhancements could include more sophisticated scheduling algorithms, such as:

1. **Critical Path Analysis**: Identifying and prioritizing tasks on the critical path.

2. **Resource-Constrained Scheduling**: Handling more complex resource constraints beyond agent availability.

3. **Priority-Based Scheduling**: Allowing tasks to have priorities that influence scheduling decisions.

4. **Deadline-Aware Scheduling**: Taking task deadlines into account during scheduling.

```python
# Example of how the current implementation might be extended with priorities
def add_task(self, task_id, duration, dependencies=None, resources=None, priority=0):
    # Add priority to the task representation
    self.tasks.append({
        "id": task_id,
        "duration": duration,
        "dependencies": dependencies or [],
        "resources": resources or {},
        "priority": priority,  # Higher values indicate higher priority
        "start": None,
        "end": None,
        "agent": None
    })

# The schedule method would then consider priorities when selecting which ready task to schedule next
```

## References

1. **Mathematical Time Structures for Agent Systems**: Section 6: Task Scheduling
2. **Operations Research**: Scheduling algorithms and optimization
3. **Project Management**: Critical path method and resource allocation
