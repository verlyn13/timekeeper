"""
Integration test suite for time flow verification in the Timekeeper framework.

This test suite verifies that time operations work correctly, maintain mathematical
properties, and ensure proper interaction between components.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings, HealthCheck
import math

# Use direct imports for the unit tests
from src.python.agent_temporal import AgentTemporal
from src.python.adaptive_agent_temporal import AdaptiveAgentTemporal


@pytest.fixture(scope="module")
def standard_temporal():
    """Fixture providing a standard AgentTemporal instance."""
    return AgentTemporal()


@pytest.fixture
def custom_temporal():
    """Fixture providing an AgentTemporal with custom units."""
    custom_config = [
        {"name": "project", "subdivisions": 3},
        {"name": "phase", "subdivisions": 4},
        {"name": "task", "subdivisions": 5},
        {"name": "step", "subdivisions": None, "is_base": True},
    ]
    return AgentTemporal(custom_config)


class TestBasicTimeOperations:
    """Tests for basic timepoint creation and operations."""

    def test_timepoint_creation(self, standard_temporal):
        """Test that timepoints can be created with different specifications."""
        # Test creating with explicit values
        tp1 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)
        assert tp1["epoch"] == 1
        assert tp1["cycle"] == 10
        assert tp1["step"] == 30
        assert tp1["microstep"] == 0  # Default value

        # Test creating with partial values
        tp2 = standard_temporal.create_timepoint(cycle=15)
        assert tp2["epoch"] == 0  # Default value
        assert tp2["cycle"] == 15
        assert tp2["step"] == 0  # Default value
        assert tp2["microstep"] == 0  # Default value

        # Test creating with out-of-range values (should normalize)
        # Default: 1 epoch = 24 cycles
        tp3 = standard_temporal.create_timepoint(
            cycle=70
        )  # 70 cycles = 2 epochs + 22 cycles
        assert tp3["epoch"] == 2  # Carried over
        assert (
            tp3["cycle"] == 22
        )  # 70 % 24 = 22 (Incorrect assumption in original test)

    def test_timepoint_addition(self, standard_temporal):
        """Test addition of timepoints."""
        # Create initial timepoint
        tp1 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)

        # Add time
        tp2 = standard_temporal.add_time(tp1, cycle=5, step=50)

        # Verify result (1e, 10c, 30s) + (0e, 5c, 50s) -> (1e, 16c, 20s) after normalization
        assert tp2["epoch"] == 1
        assert tp2["cycle"] == 16  # Corrected expectation
        assert tp2["step"] == 20  # Corrected expectation

        # Test addition with carry-over (1e, 10c, 30s) + (0e, 55c, 980s)
        # Base: 2,070,000 + (55*60*1000 + 980*1000) = 2,070,000 + 3,300,000 + 980,000 = 6,350,000
        # From Base:
        # epoch = 6350000 // 1440000 = 4
        # rem = 6350000 - 4*1440000 = 590000
        # cycle = 590000 // 60000 = 9
        # rem = 590000 - 9*60000 = 50000
        # step = 50000 // 1000 = 50
        # rem = 50000 - 50*1000 = 0
        # microstep = 0
        # Expected: epoch=4, cycle=9, step=50
        tp3 = standard_temporal.add_time(tp1, cycle=55, step=980)
        assert tp3["epoch"] == 4  # Corrected expectation
        assert tp3["cycle"] == 9  # Corrected expectation
        assert tp3["step"] == 50  # Corrected expectation

    def test_timepoint_subtraction(self, standard_temporal):
        """Test subtraction of timepoints."""
        # Create initial timepoint
        tp1 = standard_temporal.create_timepoint(epoch=2, cycle=20, step=500)

        # Subtract time
        tp2 = standard_temporal.subtract_time(tp1, cycle=10, step=200)

        # Verify result: (2e, 20c, 500s) - (0e, 10c, 200s) -> (2e, 15c, 0s) after normalization
        assert tp2["epoch"] == 2
        assert tp2["cycle"] == 15  # Corrected expectation
        assert tp2["step"] == 0  # Corrected expectation

        # Test subtraction with borrow: (2e, 20c, 500s) - (0e, 21c, 0s) -> (2e, 7c, 20s) after normalization
        tp3 = standard_temporal.subtract_time(tp1, cycle=21)
        assert tp3["epoch"] == 2  # Corrected expectation
        assert tp3["cycle"] == 7  # Corrected expectation
        assert tp3["step"] == 20  # Corrected expectation

        # Test subtraction that would result in negative time
        with pytest.raises(
            ValueError, match="Subtraction would produce a negative time result."
        ):
            # Subtracting epoch=4 (base=5,760,000) from tp1 (base=4,580,000) should fail
            standard_temporal.subtract_time(tp1, epoch=4)

    def test_timepoint_comparison(self, standard_temporal):
        """Test comparison of timepoints."""
        # Create timepoints to compare
        t1 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)
        t2 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=40)
        t3 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)

        # Test less than
        assert standard_temporal.compare_timepoints(t1, t2) < 0

        # Test equal
        assert standard_temporal.compare_timepoints(t1, t3) == 0

        # Test greater than
        assert standard_temporal.compare_timepoints(t2, t1) > 0

        # Test with different unit configurations that should normalize to the same value
        # t5 = 1 epoch = 1,440,000 base units
        # Let's make t4 = 24 cycles = 24 * 60 * 1000 = 1,440,000 base units
        t4 = standard_temporal.create_timepoint(
            epoch=0, cycle=24, step=0
        )  # Normalizes to epoch=1, cycle=0, step=0
        t5 = standard_temporal.create_timepoint(epoch=1, cycle=0, step=0)
        # Now they should be equal after normalization during comparison
        assert standard_temporal.compare_timepoints(t4, t5) == 0

    def test_time_difference(self, standard_temporal):
        """Test calculation of time difference."""
        # Create timepoints for difference calculation
        t1 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)
        t2 = standard_temporal.create_timepoint(epoch=1, cycle=15, step=40)

        # Calculate difference
        diff = standard_temporal.time_difference(t1, t2)

        # Verify result
        assert diff["epoch"] == 0
        assert diff["cycle"] == 5
        assert diff["step"] == 10

        # Test difference in reverse order (should be the same due to absolute value)
        diff_rev = standard_temporal.time_difference(t2, t1)
        assert diff_rev["epoch"] == 0
        assert diff_rev["cycle"] == 5
        assert diff_rev["step"] == 10


# Define custom strategies for timepoints
@st.composite
def timepoint_strategy(draw, temporal_system=None):
    """Generate random timepoints that work with the given temporal system."""
    if temporal_system is None:
        # Use default AgentTemporal for strategy generation
        temporal_system = AgentTemporal()

    # Get unit names
    units = [u["name"] for u in temporal_system.units]

    # Generate values for each unit
    tp = {}
    for i, unit in enumerate(temporal_system.units):
        name = unit["name"]
        # For all except base unit, respect subdivision limits
        if i < len(temporal_system.units) - 1:
            subdiv = unit["subdivisions"]
            # Generate values that might need normalization (0 to 2*subdiv)
            tp[name] = draw(st.integers(min_value=0, max_value=subdiv * 2))
        else:
            # Base unit can have a wider range
            tp[name] = draw(st.integers(min_value=0, max_value=1000))

    return tp


class TestMathematicalProperties:
    """Tests for mathematical properties of temporal operations."""

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy(), tp3=timepoint_strategy())
    def test_addition_associativity(self, standard_temporal, tp1, tp2, tp3):
        """Test that (a + b) + c = a + (b + c) for timepoint addition."""
        # Normalize inputs to ensure valid timepoints
        t1 = standard_temporal.normalize(tp1)
        t2 = standard_temporal.normalize(tp2)
        t3 = standard_temporal.normalize(tp3)

        # Calculate (t1 + t2) + t3
        t1_plus_t2 = standard_temporal.add_time(t1, **t2)
        result1 = standard_temporal.add_time(t1_plus_t2, **t3)

        # Calculate t1 + (t2 + t3)
        t2_plus_t3 = standard_temporal.add_time(t2, **t3)
        result2 = standard_temporal.add_time(t1, **t2_plus_t3)

        # Compare results - they should be the same
        assert standard_temporal.compare_timepoints(result1, result2) == 0

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy())
    def test_addition_commutativity(self, standard_temporal, tp1, tp2):
        """Test that a + b = b + a for timepoint addition."""
        # Normalize inputs
        t1 = standard_temporal.normalize(tp1)
        t2 = standard_temporal.normalize(tp2)

        # Calculate t1 + t2
        result1 = standard_temporal.add_time(t1, **t2)

        # Calculate t2 + t1
        result2 = standard_temporal.add_time(t2, **t1)

        # Compare results - they should be the same
        assert standard_temporal.compare_timepoints(result1, result2) == 0

    @given(tp=timepoint_strategy())
    def test_addition_identity(self, standard_temporal, tp):
        """Test that a + 0 = a for timepoint addition."""
        # Normalize input
        t = standard_temporal.normalize(tp)

        # Create zero timepoint
        zero = standard_temporal.create_timepoint()

        # Calculate t + 0
        result = standard_temporal.add_time(t, **zero)

        # Result should equal original timepoint
        assert standard_temporal.compare_timepoints(result, t) == 0

    @given(tp=timepoint_strategy())
    def test_normalization_idempotence(self, standard_temporal, tp):
        """Test that normalizing an already normalized timepoint has no effect."""
        # Normalize once
        t1 = standard_temporal.normalize(tp)

        # Normalize again
        t2 = standard_temporal.normalize(t1)

        # Should be the same
        assert standard_temporal.compare_timepoints(t1, t2) == 0
        # Direct comparison of dictionaries should also work
        assert t1 == t2

    @given(tp1=timepoint_strategy(), tp2=timepoint_strategy())
    def test_subtraction_addition_inverse(self, standard_temporal, tp1, tp2):
        """Test that (a + b) - b = a for timepoint operations."""
        # Normalize inputs
        t1 = standard_temporal.normalize(tp1)
        t2 = standard_temporal.normalize(tp2)

        # Skip if t2 would be greater than t1
        t1_base = standard_temporal.to_base_units(t1)
        t2_base = standard_temporal.to_base_units(t2)
        if t2_base > t1_base:
            return  # Skip this test case

        # Calculate t1 + t2
        sum_result = standard_temporal.add_time(t1, **t2)

        # Calculate (t1 + t2) - t2
        final_result = standard_temporal.subtract_time(sum_result, **t2)

        # Should equal t1
        assert standard_temporal.compare_timepoints(final_result, t1) == 0


class TestTimeUnitConversions:
    """Tests for conversion between different time units."""

    def test_to_base_units(self, standard_temporal):
        """Test conversion to base units."""
        # Create timepoint
        tp = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)

        # Convert to base units - should be:
        # 1 epoch = 24 cycles = 24*60 steps = 24*60*1000 microsteps = 1,440,000 microsteps
        # 10 cycles = 10*60 steps = 10*60*1000 microsteps = 600,000 microsteps
        # 30 steps = 30*1000 microsteps = 30,000 microsteps
        # Total: 1,440,000 + 600,000 + 30,000 = 2,070,000 microsteps
        expected_base = 1 * 24 * 60 * 1000 + 10 * 60 * 1000 + 30 * 1000
        actual_base = standard_temporal.to_base_units(tp)

        assert actual_base == expected_base

    def test_from_base_units(self, standard_temporal):
        """Test conversion from base units."""
        # Start with base units value
        base_value = 2_070_000  # Same as the previous test

        # Convert to timepoint
        tp = standard_temporal.from_base_units(base_value)

        # Verify result
        assert tp["epoch"] == 1
        assert tp["cycle"] == 10
        assert tp["step"] == 30
        assert tp["microstep"] == 0

    def test_roundtrip_conversion(self, standard_temporal):
        """Test that conversion to base units and back preserves the timepoint."""
        # Create original timepoint
        original = standard_temporal.create_timepoint(
            epoch=2, cycle=15, step=42, microstep=500
        )

        # Convert to base units and back
        base_value = standard_temporal.to_base_units(original)
        roundtrip = standard_temporal.from_base_units(base_value)

        # Verify result
        assert roundtrip["epoch"] == original["epoch"]
        assert roundtrip["cycle"] == original["cycle"]
        assert roundtrip["step"] == original["step"]
        assert roundtrip["microstep"] == original["microstep"]

        # Also verify using compare_timepoints
        assert standard_temporal.compare_timepoints(original, roundtrip) == 0


class TestHumanAgentTimeConversion:
    """Tests for conversion between agent time and human time."""

    def test_to_human_time(self, standard_temporal):
        """Test conversion from agent time to human time."""
        # Create agent timepoint
        agent_tp = standard_temporal.create_timepoint(epoch=1, cycle=30, step=45)

        # Convert to human time
        human_time = standard_temporal.to_human_time(agent_tp)

        # Verify mapping based on known mapping in implementation AFTER normalization:
        # Input: {'epoch': 1, 'cycle': 30, 'step': 45}
        # Normalized: {'epoch': 2, 'cycle': 6, 'step': 45}
        # epoch -> hours, cycle -> minutes, step -> seconds
        assert "hours" in human_time
        assert human_time["hours"] == 2  # Corrected expectation after normalization
        assert "minutes" in human_time
        assert human_time["minutes"] == 6  # Corrected expectation after normalization
        assert "seconds" in human_time
        assert human_time["seconds"] == 45

    def test_from_human_time(self, standard_temporal):
        """Test conversion from human time to agent time."""
        # Create human time
        human_time = {"hours": 2, "minutes": 15, "seconds": 30}

        # Convert to agent time
        agent_tp = standard_temporal.from_human_time(human_time)

        # Verify mapping based on known mapping in implementation
        assert agent_tp["epoch"] == 2
        assert agent_tp["cycle"] == 15
        assert agent_tp["step"] == 30
        assert agent_tp["microstep"] == 0  # Default value

    def test_human_time_roundtrip(self, standard_temporal):
        """Test that conversion to human time and back preserves the timepoint."""
        # Create original agent timepoint
        original = standard_temporal.create_timepoint(epoch=3, cycle=45, step=10)

        # Convert to human time and back
        human_time = standard_temporal.to_human_time(original)
        roundtrip = standard_temporal.from_human_time(human_time)

        # Verify result - should match for units that have mappings
        assert roundtrip["epoch"] == original["epoch"]
        assert roundtrip["cycle"] == original["cycle"]
        assert roundtrip["step"] == original["step"]

        # May not match for units without mappings (like microstep)
        # But should still represent the same point in time
        assert standard_temporal.compare_timepoints(original, roundtrip) == 0

    def test_partial_human_time(self, standard_temporal):
        """Test conversion with partial human time specifications."""
        # Create human time with only some units specified
        human_time = {"minutes": 30}  # No hours or seconds

        # Convert to agent time
        agent_tp = standard_temporal.from_human_time(human_time)

        # Verify result after normalization:
        # Input: {'minutes': 30} -> {'epoch': 0, 'cycle': 30, 'step': 0}
        # Normalized: {'epoch': 1, 'cycle': 6, 'step': 0}
        assert agent_tp["epoch"] == 1  # Corrected expectation after normalization
        assert agent_tp["cycle"] == 6  # Corrected expectation after normalization
        assert agent_tp["step"] == 0

        # Convert back to human time
        human_time_roundtrip = standard_temporal.to_human_time(
            agent_tp
        )  # Uses normalized agent_tp

        # Verify result - should match the normalized agent time converted back
        # Normalized agent_tp was {'epoch': 1, 'cycle': 6, 'step': 0}
        assert "hours" in human_time_roundtrip
        assert human_time_roundtrip["hours"] == 1  # Corrected expectation
        assert "minutes" in human_time_roundtrip
        assert human_time_roundtrip["minutes"] == 6  # Corrected expectation
        assert "seconds" in human_time_roundtrip
        assert human_time_roundtrip["seconds"] == 0


class TestCustomTimeUnits:
    """Tests for custom time unit configurations."""

    def test_custom_units_operations(self, custom_temporal):
        """Test operations with custom time units."""
        # Create timepoint with custom units
        tp = custom_temporal.create_timepoint(project=1, phase=2, task=3, step=4)

        # Verify creation
        assert tp["project"] == 1
        assert tp["phase"] == 2
        assert tp["task"] == 3
        assert tp["step"] == 4

        # Test addition: (1p, 2ph, 3t, 4s) + (0p, 1ph, 2t, 0s) -> (2p, 1ph, 1t, 4s) after normalization
        result = custom_temporal.add_time(tp, phase=1, task=2)
        assert result["project"] == 2  # Corrected expectation
        assert result["phase"] == 1  # Corrected expectation
        assert result["task"] == 1  # Corrected expectation
        assert result["step"] == 4

        # Test with values that need normalization: (1p, 2ph, 3t, 4s) + (0p, 3ph, 4t, 0s) -> (3p, 0ph, 3t, 4s) after normalization
        result2 = custom_temporal.add_time(tp, phase=3, task=4)
        assert result2["project"] == 3  # Corrected expectation
        assert result2["phase"] == 0  # Corrected expectation
        assert result2["task"] == 3  # Corrected expectation
        assert result2["step"] == 4

    def test_custom_units_conversion(self, custom_temporal):
        """Test base unit conversion with custom units."""
        # Create timepoint
        tp = custom_temporal.create_timepoint(project=1, phase=2, task=3, step=4)

        # Calculate expected base units:
        # 1 project = 3 phases = 3*4 tasks = 3*4*5 steps = 60 steps
        # 2 phases = 2*4 tasks = 2*4*5 steps = 40 steps
        # 3 tasks = 3*5 steps = 15 steps
        # 4 steps = 4 steps
        # Total: 60 + 40 + 15 + 4 = 119 steps
        expected_base = 1 * 3 * 4 * 5 + 2 * 4 * 5 + 3 * 5 + 4
        actual_base = custom_temporal.to_base_units(tp)

        assert actual_base == expected_base

        # Test roundtrip
        roundtrip = custom_temporal.from_base_units(actual_base)
        assert roundtrip["project"] == 1
        assert roundtrip["phase"] == 2
        assert roundtrip["task"] == 3
        assert roundtrip["step"] == 4
