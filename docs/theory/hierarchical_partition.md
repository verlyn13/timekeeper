# Hierarchical Partition

## Overview

A hierarchical partition is a fundamental mathematical structure in the Timekeeper framework that organizes time into nested, uniform partitions. This document provides the formal definitions, properties, and theorems related to hierarchical partitions and connects them to their implementation in the code.

## Definitions

### Definition 1: Partition

A partition $\Pi$ of a set $T$ is a collection of non-empty, disjoint subsets of $T$ whose union is $T$. That is, $\Pi = \{B_1, B_2, \ldots, B_m\}$ where:

- For all $i$, $B_i \neq \emptyset$
- For all $i \neq j$, $B_i \cap B_j = \emptyset$
- $\bigcup_{i=1}^{m} B_i = T$

For any $t \in T$, we denote by $\Pi(t)$ the unique subset $B_i \in \Pi$ such that $t \in B_i$.

**Implementation**:
In the Timekeeper framework, partitions correspond to time units in the `AgentTemporal` class. Each unit represents a level of granularity in the time hierarchy.

```python
# Each entry in the units list corresponds to a partition level
self.units = unit_config if unit_config else self.default_config
```

### Definition 2: Refinement

A partition $\Pi_j$ is a refinement of partition $\Pi_i$ if for all $B \in \Pi_i$, there exists a collection $\{C_1, C_2, \ldots, C_k\} \subset \Pi_j$ such that $B = \bigcup_{l=1}^{k} C_l$.

In other words, each subset in $\Pi_i$ is the union of one or more subsets in $\Pi_j$.

**Implementation**:
The refinement relationship is implicit in the structure of the `units` list, where each unit is a refinement of the units that come before it.

```python
# Example: In the default configuration
# "cycle" (Pi_1) is a refinement of "epoch" (Pi_0)
# "step" (Pi_2) is a refinement of "cycle" (Pi_1)
# "microstep" (Pi_3) is a refinement of "step" (Pi_2)
self.default_config = [
    {"name": "epoch", "subdivisions": 24},   # Pi_0
    {"name": "cycle", "subdivisions": 60},   # Pi_1
    {"name": "step",  "subdivisions": 1000}, # Pi_2
    {"name": "microstep", "subdivisions": None, "is_base": True}  # Pi_3
]
```

### Definition 3: Hierarchical Partition Sequence

A sequence of partitions $\{\Pi_0, \Pi_1, \ldots, \Pi_n\}$ is a hierarchical partition sequence if for all $i < j$, $\Pi_j$ is a refinement of $\Pi_i$.

**Implementation**:
The hierarchical relationship is established through the `subdivisions` property, which defines how many units at level $i+1$ fit into one unit at level $i$.

```python
# The subdivisions property defines the refinement relationship
# For example, 1 epoch contains 24 cycles
{"name": "epoch", "subdivisions": 24}
```

### Definition 4: Uniform Subdivision

A refinement $\Pi_j$ of $\Pi_i$ has uniform subdivision if for all $B \in \Pi_i$, the number of subsets in $\Pi_j$ that union to form $B$ is constant. We denote this constant as $k_{i,j}$.

For a hierarchical partition sequence, we define $k_{i+1} = k_{i,i+1}$ as the subdivision factor between adjacent levels.

**Implementation**:
The uniform subdivision property is enforced by the `subdivisions` value, which is constant for each level in the hierarchy.

```python
# Each level has a fixed subdivision factor
# e.g., each epoch uniformly contains exactly 24 cycles
def _compute_conversions(self):
    # ...
    for i in range(self.base_unit_index - 1, -1, -1):
        subdiv = self.units[i]["subdivisions"]
        current_factor *= subdiv
        to_base[i] = current_factor
    # ...
```

### Definition 5: Canonical Coordinates

Given a hierarchical partition sequence $\{\Pi_0, \Pi_1, \ldots, \Pi_n\}$ with uniform subdivision factors $\{k_1, k_2, \ldots, k_n\}$, a point $t \in T$ can be represented by canonical coordinates $(a_0, a_1, \ldots, a_{n-1})$ where:

- $a_0$ identifies which subset in $\Pi_0$ contains $t$
- For $i > 0$, $a_i$ identifies which subset in $\Pi_i$ contains $t$ relative to the subset in $\Pi_{i-1}$, with $0 \leq a_i < k_i$

**Implementation**:
Canonical coordinates are represented as values in a timepoint dictionary, and the `normalize` method ensures they are within the correct ranges.

```python
def normalize(self, timepoint):
    """
    Canonical normalization (Definition 7). This ensures that for each unit i,
    the value is in [0, subdivisions_i), by carrying over to the coarser unit
    if necessary.
    """
    # Convert to the base unit measure
    total_base = self.to_base_units(timepoint)
    # Convert back from base to hierarchical
    return self.from_base_units(total_base)
```

### Definition 6: Isomorphic Partitions

Two hierarchical partition sequences $\{\Pi_0, \Pi_1, \ldots, \Pi_n\}$ and $\{\Pi'_0, \Pi'_1, \ldots, \Pi'_n\}$ are isomorphic if they have the same sequence of subdivision factors $\{k_1, k_2, \ldots, k_n\}$.

**Implementation**:
The `AgentTemporal` class allows for custom configurations with different unit names but identical subdivision structures, which would be isomorphic partition sequences.

```python
# These two configurations are isomorphic if they have the same subdivision values
custom_config_1 = [
    {"name": "project", "subdivisions": 4},
    {"name": "phase", "subdivisions": 5},
    {"name": "task", "subdivisions": None, "is_base": True}
]

custom_config_2 = [
    {"name": "book", "subdivisions": 4},
    {"name": "chapter", "subdivisions": 5},
    {"name": "page", "subdivisions": None, "is_base": True}
]
```

## Properties

### Property 1: Canonical Form Uniqueness

For any hierarchical partition sequence with uniform subdivision, every point $t \in T$ has a unique canonical coordinate representation $(a_0, a_1, \ldots, a_{n-1})$ where $0 \leq a_i < k_{i+1}$ for $i < n-1$.

**Implementation**:
The `normalize` method ensures that timepoints are in canonical form, and the implementation guarantees uniqueness.

```python
def from_base_units(self, base_value):
    """
    The inverse of to_base_units, i.e. given an absolute measure in the base partition,
    reconstruct the hierarchical representation (a_0, a_1, ..., a_{n-1}).
    """
    # We proceed from the coarsest to the base.
    # We'll produce integer "digits" in each partition's base.
    # That is the direct analog of the canonical form described in the paper.
    result = {}
    remainder = base_value
    for i, u in enumerate(self.units):
        # ...
        if conv != 0:
            # integer portion of remainder / conv
            count = int(remainder // conv)
            result[u["name"]] = count
            # subtract that from remainder
            remainder -= count * conv
        # ...
    return result
```

### Property 2: Base Unit Conversion

For a timepoint with canonical coordinates $(a_0, a_1, \ldots, a_{n-1})$, its absolute representation in base units is:

$$|τ|_{U_n} = \sum_{i=0}^{n-1} a_i \cdot \prod_{j=i+1}^{n} k_j$$

**Implementation**:
The `to_base_units` method implements this conversion using precomputed factors for efficiency.

```python
def to_base_units(self, timepoint):
    """
    = |tau|_{U_n} in the paper (Definition 9).
    Sums up each a_i * conversion_factor to the base partition.
    """
    total = 0
    for unit_name, amount in timepoint.items():
        factor = self.conversion_factors[(unit_name, self.units[self.base_unit_index]["name"])]
        total += amount * factor
    return total
```

### Property 3: Hierarchical Navigation

Within a hierarchical partition sequence, it is possible to navigate between different levels of granularity while preserving the temporal semantics.

**Implementation**:
The conversion factors computed in `_compute_conversions` enable efficient navigation between different levels of the hierarchy.

```python
# Precompute conversion factors for efficient navigation
self.conversion_factors = {}
self._compute_conversions()
```

## Theorems

### Theorem 1: Conversion Consistency

For any two timepoints $\tau_1$ and $\tau_2$ in a hierarchical partition sequence, if they represent the same point in time, then $|\tau_1|_{U_n} = |\tau_2|_{U_n}$.

**Proof**:
If $\tau_1$ and $\tau_2$ represent the same point in time, they must have the same canonical form. The canonical form uniquely determines the absolute representation, so $|\tau_1|_{U_n} = |\tau_2|_{U_n}$.

**Implementation**:
The `to_base_units` method guarantees consistent conversion to base units, which is used for comparing timepoints.

```python
def compare_timepoints(self, t1, t2):
    """
    Lexicographical order in the math doc is effectively a base-unit comparison.
    Return:
      -1 if t1 < t2
       0 if t1 == t2
       1 if t1 > t2
    """
    b1 = self.to_base_units(t1)
    b2 = self.to_base_units(t2)
    # ...
```

### Theorem 2: Normalization Stability

The normalization process always converts a timepoint to its canonical form in a single step, and applying normalization to an already normalized timepoint does not change it.

**Proof**:
The normalization process converts a timepoint to its absolute representation and then rebuilds the canonical coordinates. If a timepoint is already in canonical form, its absolute representation will produce the same canonical coordinates when converted back.

**Implementation**:
The implementation of `normalize` ensures this property.

```python
def normalize(self, timepoint):
    # Convert to the base unit measure
    total_base = self.to_base_units(timepoint)
    # Convert back from base to hierarchical
    return self.from_base_units(total_base)
```

## Applications

### Custom Time Hierarchies

The hierarchical partition framework allows for the creation of custom time hierarchies tailored to specific application domains.

**Implementation**:
The `AgentTemporal` constructor accepts a custom configuration of units and their subdivision factors.

```python
# Custom project management time hierarchy
project_time = AgentTemporal([
    {"name": "project", "subdivisions": 4},     # 1 project = 4 phases
    {"name": "phase", "subdivisions": 5},       # 1 phase = 5 iterations
    {"name": "iteration", "subdivisions": 10},  # 1 iteration = 10 days
    {"name": "day", "subdivisions": 8},         # 1 day = 8 hours
    {"name": "hour", "subdivisions": None, "is_base": True}  # Base unit
])
```

### Adaptive Hierarchies

The hierarchical partition framework can be extended to support dynamic adaptation of subdivision factors based on usage patterns.

**Implementation**:
The `AdaptiveAgentTemporal` class extends `AgentTemporal` to provide adaptive capabilities.

```python
class AdaptiveAgentTemporal(AgentTemporal):
    """
    Extension of AgentTemporal that implements dynamic adaptability as described
    in Section 5 of the paper, in particular:

    - Adaptive Subdivision Function Γ(O, A) (Definition 21)
    - Partition Reconfiguration (Axiom 4)
    - Optimal Temporal Granularity (Property 1)
    """

    def adjust_subdivision(self, unit_name, new_subdiv):
        """
        Adjust the subdivision factor for a specific unit.

        This implements part of the Partition Reconfiguration axiom.
        """
        # ...
```

### Visualization of Hierarchies

The hierarchical structure can be visualized to provide intuitive understanding of the temporal organization.

**Implementation**:
The `visualize_temporal_hierarchy` function in the visualization module provides this capability.

```python
def visualize_temporal_hierarchy(temporal_system, figsize=(10, 6)):
    """
    Visualize the hierarchical partitioning of time.
    """
    # ...
    for i, unit in enumerate(temporal_system.units[:-1]):  # All except base
        # Get subdivision factor
        subdiv = unit["subdivisions"]

        # Draw horizontal line for this unit
        ax.axhline(y=i+0.5, color='gray', linestyle='-', alpha=0.3)

        # Draw subdivision markers
        for j in range(1, subdiv+1):
            if subdiv <= 24 or j % (subdiv//10) == 0:  # Draw fewer lines for large subdivisions
                x = j / subdiv
                ax.axvline(x=x, ymin=(i/len(units)), ymax=((i+1)/len(units)),
                          color='blue', linestyle='-', alpha=0.3)
    # ...
```

## Relationship to Other Concepts

### Temporal Universe

The hierarchical partition is a key component of the Temporal Universe. See [Temporal Universe](temporal_universe.md) for more details.

### Morphisms

The structure of hierarchical partitions enables the definition of morphisms between different time representations. See [Morphisms](morphisms.md) for more details.

### Adaptive Systems

The hierarchical structure can be adapted dynamically based on usage patterns. See [Adaptive Systems](adaptive_systems.md) for more details on how the hierarchy can be reconfigured.

## Implementation Notes

The hierarchical partition is implemented in the `AgentTemporal` class, which provides methods for creating, manipulating, and converting between different levels of the hierarchy.

The implementation focuses on efficiency by precomputing conversion factors between all pairs of units, which allows for fast navigation between different levels of granularity.

```python
# Precomputing conversion factors
def _compute_conversions(self):
    # Step 1: define how to convert each unit to the base unit
    to_base = [1.0] * len(self.units)

    # Going from the 'finest' index up to coarser indices:
    # We'll multiply subdivisions as we go up the chain from base to coarser.

    # Start from the base unit:
    current_factor = 1.0
    # Move outward from base_unit_index to the "left" in the list
    for i in range(self.base_unit_index - 1, -1, -1):
        # Example: if self.units[i] has subdivisions = 1000,
        # it means 1 of self.units[i] = 1000 of self.units[i+1]
        subdiv = self.units[i]["subdivisions"]
        current_factor *= subdiv
        to_base[i] = current_factor

    # Move outward from base_unit_index to the "right" in the list
    current_factor = 1.0
    for i in range(self.base_unit_index + 1, len(self.units)):
        subdiv = self.units[i]["subdivisions"]
        if subdiv is not None:  # should not be None except for base itself
            current_factor /= subdiv
        to_base[i] = current_factor

    # Step 2: fill in conversion_factors[(unitA, unitB)]
    # using the ratio of to_base[A]/to_base[B]
    for i, uA in enumerate(self.units):
        for j, uB in enumerate(self.units):
            factor = to_base[i] / to_base[j]
            self.conversion_factors[(uA["name"], uB["name"])] = factor
```

## References

1. **Mathematical Time Structures for Agent Systems**: Section 3: Hierarchical Partitions
2. **Discrete Mathematics for Computer Science**: Partitions and Equivalence Relations
3. **Temporal Logic in Computer Science**: Hierarchical Time Structures
