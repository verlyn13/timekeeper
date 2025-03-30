"""
Tests for the AdaptiveAgentTemporal class.

These tests validate the dynamic adaptability features described in Section 5
of the paper, including subdivision adjustments and partition reconfiguration.
"""

import pytest
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal


class TestAdaptiveAgentTemporal:
    """Test suite for the AdaptiveAgentTemporal class"""

    def setup_method(self):
        """Set up an adaptive temporal system for each test"""
        self.adaptive = AdaptiveAgentTemporal(agent_count=2)

    def test_initialization(self):
        """Test that initialization creates the expected structure"""
        assert len(self.adaptive.units) == 4
        assert self.adaptive.agent_count == 2
        assert self.adaptive.op_counter == 0

        # Check optimal ranges based on agent count
        # For agent_count=2, coarser units should be in range (2, 10)
        assert self.adaptive.optimal_ranges[0][0] == 2
        assert self.adaptive.optimal_ranges[0][1] == 10

    def test_operation_tracking(self):
        """Test that operations are properly tracked"""
        # Create some timepoints
        t1 = self.adaptive.create_timepoint(epoch=1, cycle=12, step=30)
        t2 = self.adaptive.create_timepoint(epoch=0, cycle=10, step=45)

        # Perform some operations
        self.adaptive.add_time(t1, cycle=5)
        self.adaptive.subtract_time(t2, step=10)
        self.adaptive.compare_timepoints(t1, t2)

        # Check operation counts
        assert self.adaptive.operations["add"] == 1
        assert self.adaptive.operations["subtract"] == 1
        assert self.adaptive.operations["compare"] == 1
        assert self.adaptive.op_counter == 3

    def test_adjust_subdivision(self):
        """Test adjusting subdivision factors"""
        # Initial subdivision for cycle is 60
        assert self.adaptive.units[1]["subdivisions"] == 60

        # Adjust to a new value
        self.adaptive.adjust_subdivision("cycle", 30)

        # Check the new value
        assert self.adaptive.units[1]["subdivisions"] == 30

        # Verify conversion factors were updated
        cycle_to_base = self.adaptive.conversion_factors[("cycle", "microstep")]
        step_to_base = self.adaptive.conversion_factors[("step", "microstep")]

        # Now 1 cycle = 30 steps = 30,000 microsteps
        assert cycle_to_base == 30 * 1000
        assert step_to_base == 1000

        # Test invalid unit
        with pytest.raises(ValueError):
            self.adaptive.adjust_subdivision("invalid", 10)

        # Test adjusting base unit
        with pytest.raises(ValueError):
            self.adaptive.adjust_subdivision("microstep", 10)

    def test_add_time_unit(self):
        """Test adding a new time unit"""
        # Initial unit count
        initial_count = len(self.adaptive.units)

        # Add a new unit between epoch and cycle
        self.adaptive.add_time_unit("megacycle", 4, after_unit="epoch")

        # Check the new structure
        assert len(self.adaptive.units) == initial_count + 1
        assert self.adaptive.units[1]["name"] == "megacycle"
        assert self.adaptive.units[1]["subdivisions"] == 4

        # Verify unit indices were updated
        assert self.adaptive.unit_indices["megacycle"] == 1
        assert self.adaptive.unit_indices["cycle"] == 2  # Shifted by 1

        # Test with timepoints to verify conversion factors
        # New hierarchy: epoch(24) -> megacycle(4) -> cycle(60) -> step(1000) -> microstep
        tp = self.adaptive.create_timepoint(epoch=1)
        base_units = self.adaptive.to_base_units(tp)
        # Expected: 1 epoch = 24 megacycles = 24*4 cycles = 96 cycles
        # = 96 * 60 steps = 5760 steps
        # = 5760 * 1000 microsteps = 5,760,000 microsteps
        expected = 1 * 24 * 4 * 60 * 1000
        assert abs(base_units - expected) < 1e-9  # Use approx comparison for floats

        # Test adding duplicate unit
        with pytest.raises(ValueError):
            self.adaptive.add_time_unit("megacycle", 5, after_unit="epoch")

    def test_remove_time_unit(self):
        """Test removing a time unit"""
        # Initial unit count
        initial_count = len(self.adaptive.units)

        # Remove the cycle unit
        self.adaptive.remove_time_unit("cycle")

        # Check the new structure
        assert len(self.adaptive.units) == initial_count - 1
        assert self.adaptive.units[1]["name"] == "step"  # Cycle was at index 1

        # Verify unit indices were updated
        assert "cycle" not in self.adaptive.unit_indices
        assert self.adaptive.unit_indices["step"] == 1  # Shifted by -1

        # Test with timepoints to verify conversion factors
        # New hierarchy: epoch(24) -> step(1000) -> microstep
        tp = self.adaptive.create_timepoint(epoch=1)
        base_units = self.adaptive.to_base_units(tp)
        # Expected: 1 epoch = 24 steps = 24 * 1000 microsteps = 24,000 microsteps
        expected = 1 * 24 * 1000
        assert abs(base_units - expected) < 1e-9  # Use approx comparison for floats

        # Test removing non-existent unit
        with pytest.raises(ValueError):
            self.adaptive.remove_time_unit("cycle")  # Already removed

        # Test removing base unit
        with pytest.raises(ValueError):
            self.adaptive.remove_time_unit("microstep")

    def test_optimize_for_agent_count(self):
        """Test optimizing for different agent counts"""
        # Initial agent count is 2
        assert self.adaptive.agent_count == 2

        # Change to 3 agents
        self.adaptive.optimize_for_agent_count(3)

        # Check that agent count was updated
        assert self.adaptive.agent_count == 3

        # Check that optimal ranges were updated
        # For agent_count=3, coarser units should be in range (3, 15)
        assert self.adaptive.optimal_ranges[0][0] == 3
        assert self.adaptive.optimal_ranges[0][1] == 15

        # Invalid agent count
        with pytest.raises(ValueError):
            self.adaptive.optimize_for_agent_count(0)

    def test_adaptive_behavior(self):
        """Test the automatic adjustment of subdivision factors"""
        # Set a very low threshold for testing
        self.adaptive.adaptation_threshold = 5

        # Create timepoints
        t1 = self.adaptive.create_timepoint(epoch=1, cycle=12, step=30)
        t2 = self.adaptive.create_timepoint(epoch=0, cycle=10, step=45)

        # Perform operations concentrated on a particular unit
        for _ in range(10):
            # Heavy usage of cycle operations
            self.adaptive.add_time(t1, cycle=1)
            self.adaptive.subtract_time(t2, cycle=1)

        # The system should have tried to adapt cycle subdivision by now
        assert self.adaptive.op_counter == 0  # Reset after adaptation
        assert self.adaptive.operations["add"] == 10

        # For real tests, we'd check that subdivisions were adjusted,
        # but this would require mocking random factors or internal thresholds
