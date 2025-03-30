"""
Tests for the AgentTemporal class.

These tests validate that the implementation correctly follows the mathematical
definitions and axioms from the paper.
"""

import pytest
from src.python.agent_temporal import AgentTemporal


class TestAgentTemporal:
    """Test suite for the AgentTemporal class"""

    def setup_method(self):
        """Set up a temporal system for each test"""
        self.temporal = AgentTemporal()

    def test_initialization(self):
        """Test that initialization creates the expected structure"""
        assert len(self.temporal.units) == 4
        assert self.temporal.units[0]["name"] == "epoch"
        assert self.temporal.units[1]["name"] == "cycle"
        assert self.temporal.units[2]["name"] == "step"
        assert self.temporal.units[3]["name"] == "microstep"

        # Check the subdivision factors
        assert self.temporal.units[0]["subdivisions"] == 24
        assert self.temporal.units[1]["subdivisions"] == 60
        assert self.temporal.units[2]["subdivisions"] == 1000

        # Verify the base unit
        assert self.temporal.base_unit_index == 3
        assert self.temporal.units[self.temporal.base_unit_index]["name"] == "microstep"

    def test_create_timepoint(self):
        """Test timepoint creation"""
        # Create with partial specification
        tp = self.temporal.create_timepoint(epoch=1, cycle=2)
        assert tp["epoch"] == 1
        assert tp["cycle"] == 2
        assert tp["step"] == 0
        assert tp["microstep"] == 0

        # Create with full specification
        tp2 = self.temporal.create_timepoint(epoch=1, cycle=2, step=3, microstep=4)
        assert tp2["epoch"] == 1
        assert tp2["cycle"] == 2
        assert tp2["step"] == 3
        assert tp2["microstep"] == 4

        # Test invalid unit
        with pytest.raises(ValueError):
            self.temporal.create_timepoint(invalid_unit=5)

    def test_normalization(self):
        """Test canonical normalization of timepoints (Definition 7)"""
        # Create an out-of-range timepoint
        tp = {"epoch": 1, "cycle": 25, "step": 60, "microstep": 1500}
        normalized = self.temporal.normalize(tp)

        # Check that values have been normalized to their ranges
        # Base units = 1*1.44M + 25*60k + 60*1k + 1500 = 3,001,500
        # From Base: epoch=2, cycle=2, step=1, microstep=500
        assert normalized["epoch"] == 2
        assert normalized["cycle"] == 2  # Corrected expectation
        assert normalized["step"] == 1  # Corrected expectation
        assert normalized["microstep"] == 500

    def test_to_base_units(self):
        """Test conversion to absolute representation (Definition 9)"""
        # Create a timepoint
        tp = self.temporal.create_timepoint(epoch=2, cycle=12, step=30, microstep=500)

        # Calculate expected base units
        # 2 epochs * 24 cycles/epoch * 60 steps/cycle * 1000 microsteps/step = 2,880,000 microsteps
        # + 12 cycles * 60 steps/cycle * 1000 microsteps/step = 720,000 microsteps
        # + 30 steps * 1000 microsteps/step = 30,000 microsteps
        # + 500 microsteps = 500 microsteps
        # Total: 3,630,500 microsteps
        expected = 2880000 + 720000 + 30000 + 500

        # Convert to base units
        base_units = self.temporal.to_base_units(tp)

        # Check the result
        assert base_units == expected

    def test_from_base_units(self):
        """Test conversion from absolute to hierarchical (inverse of Definition 9)"""
        # Convert a known number of base units to a timepoint
        base_units = 3630500  # Same as in test_to_base_units

        tp = self.temporal.from_base_units(base_units)

        # Check the result matches our expectation
        assert tp["epoch"] == 2
        assert tp["cycle"] == 12
        assert tp["step"] == 30
        assert tp["microstep"] == 500

    def test_addition(self):
        """Test temporal addition (Axiom: Temporal Addition)"""
        # Create timepoints
        t1 = self.temporal.create_timepoint(epoch=1, cycle=12, step=30)

        # Add some time
        t2 = self.temporal.add_time(t1, cycle=15, step=40)

        # Expected result: (1e, 12c, 30s) + (0e, 15c, 40s) -> (2e, 4c, 10s) after normalization
        assert t2["epoch"] == 2
        assert t2["cycle"] == 4  # Corrected expectation
        assert t2["step"] == 10  # Corrected expectation
        assert t2["microstep"] == 0

    def test_subtraction(self):
        """Test temporal subtraction (Axiom: Temporal Subtraction)"""
        # Create timepoints
        t1 = self.temporal.create_timepoint(epoch=2, cycle=3, step=70)

        # Subtract some time
        t2 = self.temporal.subtract_time(t1, cycle=1, step=30)

        # Expected result: Normalize(2 epochs, 2 cycles, 40 steps, 0 microsteps)
        assert t2["epoch"] == 2
        assert t2["cycle"] == 2
        assert t2["step"] == 40
        assert t2["microstep"] == 0

        # Test error on negative result
        with pytest.raises(ValueError):
            self.temporal.subtract_time(t2, epoch=3)

    def test_comparison(self):
        """Test timepoint comparison (Definition: Lexicographical Order)"""
        t1 = self.temporal.create_timepoint(epoch=1, cycle=2, step=3)
        t2 = self.temporal.create_timepoint(epoch=1, cycle=2, step=4)
        t3 = self.temporal.create_timepoint(epoch=1, cycle=3, step=1)
        t4 = self.temporal.create_timepoint(epoch=1, cycle=2, step=3)

        # t1 < t2
        assert self.temporal.compare_timepoints(t1, t2) < 0

        # t2 < t3
        assert self.temporal.compare_timepoints(t2, t3) < 0

        # t1 == t4
        assert self.temporal.compare_timepoints(t1, t4) == 0

        # t3 > t1
        assert self.temporal.compare_timepoints(t3, t1) > 0

    def test_time_difference(self):
        """Test computing time difference between timepoints"""
        t1 = self.temporal.create_timepoint(epoch=1, cycle=10, step=0)
        t2 = self.temporal.create_timepoint(epoch=1, cycle=15, step=30)

        diff = self.temporal.time_difference(t1, t2)

        # Expected: 5 cycles, 30 steps
        assert diff["epoch"] == 0
        assert diff["cycle"] == 5
        assert diff["step"] == 30
        assert diff["microstep"] == 0

    def test_human_time_conversion(self):
        """Test the morphisms between agent and human time (Definitions 16-19)"""
        # Agent to human time
        agent_time = self.temporal.create_timepoint(epoch=2, cycle=15, step=30)
        human_time = self.temporal.to_human_time(agent_time)

        assert human_time["hours"] == 2
        assert human_time["minutes"] == 15
        assert human_time["seconds"] == 30

        # Human to agent time
        human_time = {"hours": 3, "minutes": 45, "seconds": 20}
        agent_time = self.temporal.from_human_time(human_time)

        # Verify result after normalization:
        # Input: {'hours': 3, 'minutes': 45, 'seconds': 20} -> {'epoch': 3, 'cycle': 45, 'step': 20}
        # Normalized: {'epoch': 4, 'cycle': 21, 'step': 20}
        assert agent_time["epoch"] == 4  # Corrected expectation
        assert agent_time["cycle"] == 21  # Corrected expectation
        assert agent_time["step"] == 20
        assert agent_time["microstep"] == 0
