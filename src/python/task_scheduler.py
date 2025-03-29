"""
Implementation of the Task Scheduling component of the AgentTemporal framework.

This module implements the task scheduling definitions and algorithms
described in Section 6 of the paper.
"""

class TaskScheduler:
    """
    Demonstrates the scheduling concepts from the paper:
      - Tasks T_i with durations δ_i, dependency sets D_i, etc. (Definition 26)
      - Creates a schedule S that respects the constraints. (Definition 28)
    """
    def __init__(self, temporal_system):
        """
        Initialize the task scheduler with a temporal system.
        
        Args:
            temporal_system: An AgentTemporal instance to use for time operations
        """
        self.temporal = temporal_system  # an AgentTemporal instance
        self.tasks = []

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
        # Make a copy of tasks to work with
        scheduled = []
        unscheduled = self.tasks[:]
        
        # Track per-agent availability
        # Each agent's entry is the timepoint when they become available
        agent_availability = [
            self.temporal.create_timepoint() for _ in range(agent_count)
        ]
        
        # Loop until all tasks are scheduled
        while unscheduled:
            # Find tasks whose dependencies are all in scheduled
            ready = [
                t for t in unscheduled
                if all(dep in [s["id"] for s in scheduled] for dep in t["dependencies"])
            ]
            
            if not ready:
                raise ValueError("Dependency cycle detected or unsatisfiable dependencies.")
            
            for task in ready:
                # Find the earliest time this task can start
                # This is the maximum of:
                # 1. The completion time of its dependencies
                # 2. The availability of any agent
                
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
                
                # Find the earliest available agent
                earliest_agent_idx = 0
                earliest_agent_time = agent_availability[0]
                
                for i, availability in enumerate(agent_availability):
                    if self.temporal.compare_timepoints(availability, earliest_agent_time) < 0:
                        earliest_agent_idx = i
                        earliest_agent_time = availability
                
                # Final start time is the later of dependency-based and agent-based times
                if self.temporal.compare_timepoints(earliest_agent_time, earliest_start) > 0:
                    task_start = earliest_agent_time
                else:
                    task_start = earliest_start
                
                # Calculate end time
                task_end = self.temporal.add_time(task_start, **task["duration"])
                
                # Update task with scheduling info
                task["start"] = task_start
                task["end"] = task_end
                task["agent"] = earliest_agent_idx
                
                # Update agent availability
                agent_availability[earliest_agent_idx] = task_end
                
                # Move task from unscheduled to scheduled
                scheduled.append(task)
                unscheduled.remove(task)
        
        # Return the tasks in scheduled order
        return scheduled
    
    def visualize_schedule(self):
        """
        Returns data for visualizing the schedule.
        
        Returns:
            Dict with tasks and their timing information
        """
        if not all(t.get("start") and t.get("end") for t in self.tasks):
            raise ValueError("Not all tasks have been scheduled. Run schedule() first.")
            
        # Convert to a format suitable for visualization
        viz_data = []
        for task in self.tasks:
            # Convert timepoints to base units for easier plotting
            start_base = self.temporal.to_base_units(task["start"])
            end_base = self.temporal.to_base_units(task["end"])
            
            viz_data.append({
                "id": task["id"],
                "start": start_base,
                "end": end_base,
                "duration": end_base - start_base,
                "agent": task["agent"],
                "dependencies": task["dependencies"]
            })
            
        return viz_data
"""
Example usage:

from agent_temporal import AgentTemporal
from task_scheduler import TaskScheduler

# Create the temporal system
agent_temporal = AgentTemporal()

# Create a scheduler
scheduler = TaskScheduler(agent_temporal)

# Add some tasks
scheduler.add_task("T1", {"step": 100})
scheduler.add_task("T2", {"cycle": 2}, ["T1"])
scheduler.add_task("T3", {"epoch": 1, "step": 500}, ["T2"])

# Schedule them
scheduled_tasks = scheduler.schedule()

# Print the schedule
for task in scheduled_tasks:
    print(f"Task {task['id']}:")
    print(f"  Start: {task['start']}")
    print(f"  End:   {task['end']}")
    print(f"  Agent: {task['agent']}")
"""