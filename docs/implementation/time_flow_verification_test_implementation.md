# Time Flow Verification Test Implementation Plan

## Overview

This document provides a detailed implementation plan for the Time Flow Verification test suite, which is a critical component of the Timekeeper framework's integration testing strategy. These tests will verify that time operations work correctly, maintain mathematical properties, and ensure proper interaction between components.

## Test Objectives

The Time Flow Verification tests aim to verify:

1. Basic timepoint creation and manipulation
2. Consistency of timepoint operations (addition, subtraction, comparison)
3. Mathematical properties of operations (associativity, commutativity, identity)
4. Hierarchical navigation between time units
5. Correct handling of canonical forms
6. Bidirectional consistency in human-agent time conversion

## Implementation Details

### File Structure

Create a new file in the tests directory with the following path:

```
tests/integration/test_time_flow.py
```

### Dependencies

The test file should import the following dependencies:

```python
import pytest
from hypothesis import given, strategies as st
import math

from timekeeper.agent_temporal import AgentTemporal
from timekeeper.adaptive_agent_temporal import AdaptiveAgentTemporal
```

### Test Fixtures

Define the following fixtures for the tests:

```python
@pytest.fixture
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
        {"name": "step", "subdivisions": None, "is_base": True}
    ]
    return AgentTemporal(custom_config)

@pytest.fixture
def adaptive_temporal():
    """Fixture providing an AdaptiveAgentTemporal instance."""
    return AdaptiveAgentTemporal(agent_count=2)
```

### Basic Time Operations Tests

Implement tests for basic time operations:

```python
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
        tp3 = standard_temporal.create_timepoint(cycle=70)  # > max of 60
        assert tp3["epoch"] == 1  # Carried over
        assert tp3["cycle"] == 10  # 70 % 60

    def test_timepoint_addition(self, standard_temporal):
        """Test addition of timepoints."""
        # Create initial timepoint
        tp1 = standard_temporal.create_timepoint(epoch=1, cycle=10, step=30)

        # Add time
        tp2 = standard_temporal.add_time(tp1, cycle=5, step=50)

        # Verify result
        assert tp2["epoch"] == 1
        assert tp2["cycle"] == 15
        assert tp2["step"] == 80

        # Test addition with carry-over
        tp3 = standard_temporal.add_time(tp1, cycle=55, step=980)
        assert tp3["epoch"] == 2  # Carry over from cycle -> epoch
        assert tp3["cycle"] == 5  # 10 + 55 = 65, 65 % 60 = 5
        assert tp3["step"] == 10  # 30 + 980 = 1010, 1010 % 1000 = 10

    def test_timepoint_subtraction(self, standard_temporal):
        """Test subtraction of timepoints."""
        # Create initial timepoint
        tp1 = standard_temporal.create_timepoint(epoch=2, cycle=20, step=500)

        # Subtract time
        tp2 = standard_temporal.subtract_time(tp1, cycle=10, step=200)

        # Verify result
        assert tp2["epoch"] == 2
        assert tp2["cycle"] == 10
        assert tp2["step"] == 300

        # Test subtraction with borrow
        tp3 = standard_temporal.subtract_time(tp1, cycle=21)  # Need to borrow from epoch
        assert tp3["epoch"] == 1
        assert tp3["cycle"] == 59  # Borrowed 60 cycles from 1 epoch
        assert tp3["step"] == 500

        # Test subtraction that would result in negative time
        with pytest.raises(ValueError):
            standard_temporal.subtract_time(tp1, epoch=3)

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

        # Test with different unit configurations
        t4 = standard_temporal.create_timepoint(epoch=0, cycle=59, step=1000)  # Needs normalization
        t5 = standard_temporal.create_timepoint(epoch=1, cycle=0, step=0)  # Equivalent after normalization
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
```

### Mathematical Properties Tests

Implement tests for mathematical properties using property-based testing:

```python
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
```

### Time Unit Conversion Tests

Implement tests for time unit conversions:

```python
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
        original = standard_temporal.create_timepoint(epoch=2, cycle=15, step=42, microstep=500)

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
```

### Human-Agent Time Conversion Tests

Implement tests for human-agent time conversion:

```python
class TestHumanAgentTimeConversion:
    """Tests for conversion between agent time and human time."""

    def test_to_human_time(self, standard_temporal):
        """Test conversion from agent time to human time."""
        # Create agent timepoint
        agent_tp = standard_temporal.create_timepoint(epoch=1, cycle=30, step=45)

        # Convert to human time
        human_time = standard_temporal.to_human_time(agent_tp)

        # Verify mapping based on known mapping in implementation:
        # epoch -> hours, cycle -> minutes, step -> seconds
        assert "hours" in human_time
        assert human_time["hours"] == 1
        assert "minutes" in human_time
        assert human_time["minutes"] == 30
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

        # Verify result
        assert agent_tp["epoch"] == 0  # Default value
        assert agent_tp["cycle"] == 30  # From minutes
        assert agent_tp["step"] == 0  # Default value

        # Convert back to human time
        human_time_roundtrip = standard_temporal.to_human_time(agent_tp)

        # Verify result
        assert "hours" in human_time_roundtrip
        assert human_time_roundtrip["hours"] == 0
        assert "minutes" in human_time_roundtrip
        assert human_time_roundtrip["minutes"] == 30
        assert "seconds" in human_time_roundtrip
        assert human_time_roundtrip["seconds"] == 0
```

### Custom Time Units Tests

Implement tests for custom time unit configurations:

```python
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

        # Test addition
        result = custom_temporal.add_time(tp, phase=1, task=2)
        assert result["project"] == 1
        assert result["phase"] == 3
        assert result["task"] == 5
        assert result["step"] == 4

        # Test with values that need normalization
        result2 = custom_temporal.add_time(tp, phase=3, task=4)  # phase=2+3=5 > 4, should carry to project
        assert result2["project"] == 2  # Carried over
        assert result2["phase"] == 1  # 2+3=5, 5%4=1
        assert result2["task"] == 7  # 3+4=7
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
```

## Expected Outcomes

When these tests are implemented and run, they should:

1. Verify that all timepoint operations work correctly
2. Confirm that mathematical properties like associativity and commutativity are maintained
3. Ensure that conversions between time representations are consistent
4. Validate that custom time unit configurations work as expected

## Implementation Steps

1. Create the `tests/integration` directory if it doesn't exist
2. Create the `test_time_flow.py` file with the provided test code
3. Run the tests with pytest to verify functionality
4. Address any failures by fixing the implementation or test code
5. Document the test results in the project documentation

## Verification

After implementing the tests, verify that:

1. All tests pass with the current implementation
2. The tests cover all the key functionality of the temporal system
3. The tests verify the theoretical properties defined in the documentation

## Next Steps

After implementing and verifying these time flow tests, the next step would be to implement the other integration test categories:

1. Adaptive Time Adjustments tests
2. Task Scheduling Integration tests
3. Visualization Integration tests
4. End-to-End Workflow tests

These tests will build on the time flow verification tests and ensure that all components of the Timekeeper framework work together correctly.
