"""
Temporal Universe Implementation.

This module implements the concept of a Temporal Universe (Definition 1)
from the formal mathematical theory of hierarchical temporal partitions.
"""

from typing import List, Tuple, Dict, Optional, Any
import math


class TemporalUniverse:
    """
    Implementation of a Temporal Universe as defined in the formal theory.

    A Temporal Universe is a mathematical structure consisting of a set of time points
    with a strict total ordering relation, representing the fundamental temporal domain
    for agent operations.

    Theoretical Foundation:
        This class implements Definition 1 (Temporal Universe) from the formal theory.
        A temporal universe is defined as a pair (T, <) where:
            - T is a set of timepoints
            - < is a strict total ordering on T

    References:
        - Definition 1: Temporal Universe
        - Definition 2: Hierarchical Partition (built on top of this)
        - Axiom 1: Time Linearity (implemented by the ordering)
    """

    def __init__(self, units: List[str], subdivisions: List[int]):
        """
        Initialize a temporal universe with hierarchical units.

        Args:
            units: A list of unit names from coarsest to finest
                (e.g., ["epoch", "cycle", "step"])
            subdivisions: A list of subdivision factors between adjacent units
                (e.g., [100, 50] means 100 cycles per epoch, 50 steps per cycle)

        Raises:
            ValueError: If the inputs are invalid

        Theoretical Foundation:
            This constructor establishes the hierarchical structure defined in
            Definition 2 (Hierarchical Partition), built upon the temporal universe.
        """
        if len(units) <= 1:
            raise ValueError("At least two temporal units are required")

        if len(subdivisions) != len(units) - 1:
            raise ValueError(
                f"Expected {len(units)-1} subdivision factors for {len(units)} units"
            )

        for factor in subdivisions:
            if factor <= 1:
                raise ValueError("Subdivision factors must be greater than 1")

        self.units = units
        self.subdivisions = subdivisions
        self._unit_index = {unit: i for i, unit in enumerate(units)}

        # Calculate cumulative subdivision factors for each level
        self.cumulative_factors = [1]
        factor = 1
        for s in reversed(subdivisions):
            factor *= s
            self.cumulative_factors.insert(0, factor)

    def create_timepoint(self, **components) -> Dict[str, int]:
        """
        Create a timepoint in canonical form.

        Args:
            **components: Keyword arguments specifying timepoint components
                (e.g., epoch=1, cycle=5, step=10)

        Returns:
            A dictionary representing the timepoint in canonical form

        Raises:
            ValueError: If invalid components are provided

        Theoretical Foundation:
            This method creates a timepoint as defined in Definition 6 (Timepoint),
            ensuring it adheres to the canonical form specified in Definition 7.
        """
        # Start with zeros for all units
        result = {unit: 0 for unit in self.units}

        # Update with provided components
        for unit, value in components.items():
            if unit not in self._unit_index:
                raise ValueError(f"Unknown temporal unit: {unit}")
            result[unit] = value

        # Normalize to canonical form (Definition 7)
        return self.normalize_timepoint(result)

    def normalize_timepoint(self, timepoint: Dict[str, int]) -> Dict[str, int]:
        """
        Normalize a timepoint to its canonical form.

        Implements the normalization procedure from Definition 7 (Canonical Timepoint Representation)
        in the formal theory. Ensures each component a_i satisfies 0 <= a_i < k_i.

        Args:
            timepoint: A dictionary representation of a timepoint

        Returns:
            The normalized timepoint in canonical form

        References:
            - Definition 7: Canonical Timepoint Representation
            - Used in: Axiom 2 (Temporal Addition), Axiom 3 (Temporal Subtraction)
        """
        result = timepoint.copy()
        carry = 0

        # Process from finest unit to coarsest, applying normalization
        for i in range(len(self.units) - 1, 0, -1):
            current_unit = self.units[i]
            next_coarser_unit = self.units[i - 1]
            subdivision = self.subdivisions[i - 1]

            # Add any carry from finer units
            result[current_unit] += carry

            # Calculate new carry and normalized value
            carry, result[current_unit] = divmod(result[current_unit], subdivision)

        # Handle the coarsest unit
        result[self.units[0]] += carry

        return result

    def compare_timepoints(self, t1: Dict[str, int], t2: Dict[str, int]) -> int:
        """
        Compare two timepoints to determine their ordering.

        Args:
            t1: First timepoint
            t2: Second timepoint

        Returns:
            -1 if t1 < t2, 0 if t1 == t2, 1 if t1 > t2

        Theoretical Foundation:
            This method implements the strict total ordering (<) defined in
            Definition 1 (Temporal Universe), and follows Axiom 1 (Time Linearity).
        """
        # Normalize both timepoints to ensure canonical form
        t1_normalized = self.normalize_timepoint(t1)
        t2_normalized = self.normalize_timepoint(t2)

        # Compare from coarsest to finest
        for unit in self.units:
            if t1_normalized[unit] < t2_normalized[unit]:
                return -1
            elif t1_normalized[unit] > t2_normalized[unit]:
                return 1

        # All components are equal
        return 0

    def timepoint_to_absolute(self, timepoint: Dict[str, int]) -> int:
        """
        Convert a timepoint to an absolute numerical value.

        Args:
            timepoint: A timepoint dictionary

        Returns:
            An integer representing the absolute position in the finest units

        Theoretical Foundation:
            This method implements the bijection between hierarchical timepoints and
            linear timepoints described in Theorem 1 (Hierarchical-Linear Equivalence).
        """
        normalized = self.normalize_timepoint(timepoint)
        absolute = 0

        for i, unit in enumerate(self.units):
            absolute += normalized[unit] * self.cumulative_factors[i + 1]

        return absolute

    def absolute_to_timepoint(self, absolute_value: int) -> Dict[str, int]:
        """
        Convert an absolute value to a canonical timepoint.

        Args:
            absolute_value: An integer representing absolute time in finest units

        Returns:
            A timepoint dictionary in canonical form

        Theoretical Foundation:
            This method implements the inverse of the bijection described in
            Theorem 1 (Hierarchical-Linear Equivalence).
        """
        if absolute_value < 0:
            raise ValueError("Absolute time value cannot be negative")

        timepoint = {}
        remaining = absolute_value

        # Convert from coarsest to finest
        for i, unit in enumerate(self.units[:-1]):
            divisor = self.cumulative_factors[i + 1]
            timepoint[unit], remaining = divmod(remaining, divisor)

        # Handle the finest unit
        timepoint[self.units[-1]] = remaining

        return timepoint

    def add_duration(
        self, timepoint: Dict[str, int], duration: Dict[str, int]
    ) -> Dict[str, int]:
        """
        Add a duration to a timepoint.

        Args:
            timepoint: The starting timepoint
            duration: The duration to add

        Returns:
            The resulting timepoint after adding the duration

        Theoretical Foundation:
            This method implements Axiom 2 (Temporal Addition) from the formal theory.
        """
        result = timepoint.copy()

        for unit, value in duration.items():
            if unit in result:
                result[unit] += value

        return self.normalize_timepoint(result)

    def subtract_timepoints(
        self, t2: Dict[str, int], t1: Dict[str, int]
    ) -> Dict[str, int]:
        """
        Calculate the duration between two timepoints.

        Args:
            t2: The later timepoint
            t1: The earlier timepoint

        Returns:
            A duration representing t2 - t1

        Raises:
            ValueError: If t2 is earlier than t1

        Theoretical Foundation:
            This method implements Axiom 3 (Temporal Subtraction) from the formal theory.
        """
        if self.compare_timepoints(t2, t1) < 0:
            raise ValueError("Cannot subtract a later timepoint from an earlier one")

        # Convert to absolute values, subtract, then convert back
        abs1 = self.timepoint_to_absolute(t1)
        abs2 = self.timepoint_to_absolute(t2)

        return self.absolute_to_timepoint(abs2 - abs1)
