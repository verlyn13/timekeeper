"""
Tests for the TaskScheduler class.

These tests validate the scheduling algorithms and constraints defined
in Section 6 of the paper, including dependency enforcement and agent assignment.
"""

import pytest
from src.python.agent_temporal import AgentTemporal
from src.python.task_scheduler import TaskScheduler

class TestTaskScheduler:
    """Test suite for the TaskScheduler class"""
    
    def setup_method(self):
        """Set up a temporal system and scheduler for each test"""
        self.temporal = AgentTemporal()
        self.scheduler = TaskScheduler(self.temporal)
    
    def test_initialization(self):
        """Test that initialization creates the expected structure"""
        assert self.scheduler.temporal == self.temporal
        assert len(self.scheduler.tasks) == 0
    
    def test_add_task(self):
        """Test adding tasks to the scheduler"""
        # Add a simple task
        self.scheduler.add_task("T1", {"step": 100})
        
        # Check that the task was added
        assert len(self.scheduler.tasks) == 1
        assert self.scheduler.tasks[0]["id"] == "T1"
        assert self.scheduler.tasks[0]["duration"] == {"step": 100}
        assert self.scheduler.tasks[0]["dependencies"] == []
        assert self.scheduler.tasks[0]["resources"] == {}
        assert self.scheduler.tasks[0]["start"] is None
        assert self.scheduler.tasks[0]["end"] is None
        
        # Add a task with dependencies
        self.scheduler.add_task("T2", {"cycle": 2}, ["T1"])
        
        # Check that the task was added with dependencies
        assert len(self.scheduler.tasks) == 2
        assert self.scheduler.tasks[1]["id"] == "T2"
        assert self.scheduler.tasks[1]["dependencies"] == ["T1"]
    
    def test_simple_scheduling(self):
        """Test scheduling with one task"""
        # Add a single task
        self.scheduler.add_task("T1", {"step": 100})
        
        # Schedule it
        scheduled = self.scheduler.schedule()
        
        # Check scheduling results
        assert len(scheduled) == 1
        assert scheduled[0]["id"] == "T1"
        
        # Start time should be zero
        start = scheduled[0]["start"]
        assert start["epoch"] == 0
        assert start["cycle"] == 0
        assert start["step"] == 0
        assert start["microstep"] == 0
        
        # End time should be start + duration
        end = scheduled[0]["end"]
        assert end["epoch"] == 0
        assert end["cycle"] == 0
        assert end["step"] == 100
        assert end["microstep"] == 0
    
    def test_scheduling_with_dependencies(self):
        """Test scheduling with dependencies"""
        # Add tasks with dependencies
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 1}, ["T1"])
        self.scheduler.add_task("T3", {"step": 50}, ["T2"])
        
        # Schedule them
        scheduled = self.scheduler.schedule()
        
        # Check scheduling results
        assert len(scheduled) == 3
        
        # Find tasks by ID
        t1 = next(t for t in scheduled if t["id"] == "T1")
        t2 = next(t for t in scheduled if t["id"] == "T2")
        t3 = next(t for t in scheduled if t["id"] == "T3")
        
        # Check dependency enforcement
        # T1 ends at step 100
        # T2 should start at or after T1 ends
        assert self.temporal.compare_timepoints(t1["end"], t2["start"]) <= 0
        
        # T3 should start at or after T2 ends
        assert self.temporal.compare_timepoints(t2["end"], t3["start"]) <= 0
        
        # T2 end should be T2 start + 1 cycle
        t2_expected_end = self.temporal.add_time(t2["start"], cycle=1)
        assert t2["end"] == t2_expected_end
    
    def test_cyclic_dependencies(self):
        """Test that cyclic dependencies raise an error"""
        # Add tasks with cyclic dependencies
        self.scheduler.add_task("T1", {"step": 100}, ["T3"])
        self.scheduler.add_task("T2", {"cycle": 1}, ["T1"])
        self.scheduler.add_task("T3", {"step": 50}, ["T2"])
        
        # Scheduling should fail
        with pytest.raises(ValueError):
            self.scheduler.schedule()
    
    def test_multi_agent_scheduling(self):
        """Test scheduling with multiple agents"""
        # Add independent tasks
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 1})
        self.scheduler.add_task("T3", {"step": 50})
        
        # Schedule with 2 agents
        scheduled = self.scheduler.schedule(agent_count=2)
        
        # Check scheduling results
        assert len(scheduled) == 3
        
        # Verify agent assignments
        agents_used = set(task["agent"] for task in scheduled)
        assert len(agents_used) <= 2  # Should use at most 2 agents
        
        # With no dependencies, tasks with same agent shouldn't overlap
        for i, task1 in enumerate(scheduled):
            for task2 in scheduled[i+1:]:
                if task1["agent"] == task2["agent"]:
                    # Either task1 ends before task2 starts or vice versa
                    comparison = self.temporal.compare_timepoints(task1["end"], task2["start"])
                    comparison2 = self.temporal.compare_timepoints(task2["end"], task1["start"])
                    assert comparison <= 0 or comparison2 <= 0
    
    def test_visualize_schedule(self):
        """Test schedule visualization data generation"""
        # Add some tasks
        self.scheduler.add_task("T1", {"step": 100})
        self.scheduler.add_task("T2", {"cycle": 1}, ["T1"])
        
        # Schedule them
        self.scheduler.schedule()
        
        # Get visualization data
        viz_data = self.scheduler.visualize_schedule()
        
        # Check the data structure
        assert len(viz_data) == 2
        assert "id" in viz_data[0]
        assert "start" in viz_data[0]
        assert "end" in viz_data[0]
        assert "duration" in viz_data[0]
        assert "agent" in viz_data[0]
        
        # First task should start at 0
        assert viz_data[0]["start"] == 0
        
        # Test with unscheduled tasks
        self.scheduler.tasks = []
        self.scheduler.add_task("T1", {"step": 100})  # Not scheduled
        
        with pytest.raises(ValueError):
            self.scheduler.visualize_schedule()