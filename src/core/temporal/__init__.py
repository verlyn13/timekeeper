"""
Core Temporal System.

This module implements the core temporal system based on the hierarchical
temporal partitioning framework defined in the formal theory.

Theoretical Foundation:
    - Definition 1: Temporal Universe
    - Definition 2: Hierarchical Partition
    - Definitions 6-8: Timepoint and Operations
"""

from core.temporal.universe import TemporalUniverse
from core.temporal.timepoint import Timepoint
from core.temporal.partition import Partition
from core.temporal.operations import (
    add_timepoints,
    subtract_timepoints,
    compare_timepoints,
)

__all__ = [
    "TemporalUniverse",
    "Timepoint",
    "Partition",
    "add_timepoints",
    "subtract_timepoints",
    "compare_timepoints",
]
