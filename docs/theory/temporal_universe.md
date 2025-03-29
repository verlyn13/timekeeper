# Temporal Universe

## Overview

The Temporal Universe is the foundational mathematical concept that defines the structure of time in the Timekeeper framework. This document provides the formal definitions, properties, and theorems related to the Temporal Universe and connects them to their implementation in the code.

## Definitions

### Definition 1: Temporal Universe

A Temporal Universe $\mathcal{T}$ is a triple $(T, \{\Pi_0, \Pi_1, \ldots, \Pi_n\}, \{k_1, k_2, \ldots, k_n\})$ where:

- $T$ is the time domain, a set of all possible time points
- $\{\Pi_0, \Pi_1, \ldots, \Pi_n\}$ is a sequence of partitions of $T$, with $\Pi_0$ being the coarsest and $\Pi_n$ being the finest
- $k_i$ are subdivision factors such that $|\Pi_{i-1}(t)| = k_i \cdot |\Pi_i(t)|$ for all $t \in T$ and $i \in \{1, 2, \ldots, n\}$

**Implementation**:

- The `AgentTemporal` class implements the Temporal Universe.
- The time domain $T$ is implicitly represented by the set of all possible timepoints.
- The partitions are represented by the `units` list, where each unit corresponds to a level in the partition hierarchy.
- The subdivision factors are stored in the `subdivisions` field of each unit.

```python
class AgentTemporal:
    def __init__(self, unit_config=None):
        # Default configuration defines the partitions and subdivision factors
        self.default_config = [
            {"name": "epoch", "subdivisions": 24},   # Pi_0 with k_1 = 24
            {"name": "cycle", "subdivisions": 60},   # Pi_1 with k_2 = 60
            {"name": "step",  "subdivisions": 1000}, # Pi_2 with k_3 = 1000
            {"name": "microstep", "subdivisions": None, "is_base": True}  # Pi_3 (finest)
        ]
        # ...
```

### Definition 2: Hierarchical Partition

A sequence of partitions $\{\Pi_0, \Pi_1, \ldots, \Pi_n\}$ is hierarchical if for all $i < j$ and all $t \in T$, there exists a $t' \in T$ such that $\Pi_i(t) = \Pi_i(t')$ and $\Pi_j(t) \neq \Pi_j(t')$.

In other words, each partition $\Pi_i$ is a refinement of all coarser partitions $\Pi_j$ where $j < i$.

**Implementation**:

- The hierarchical structure is enforced by the organization of the `units` list and the conversion factors between units.
- The `_compute_conversions` method calculates how many units of one level correspond to units of another level.

```python
def _compute_conversions(self):
    # Step 1: define how to convert each unit to the base unit
    to_base = [1.0] * len(self.units)

    # Going from the base unit up to coarser units
    current_factor = 1.0
    for i in range(self.base_unit_index - 1, -1, -1):
        subdiv = self.units[i]["subdivisions"]
        current_factor *= subdiv
        to_base[i] = current_factor
    # ...
```

### Definition 3: Timepoint

A timepoint $\tau$ in a Temporal Universe $\mathcal{T}$ is represented as an $n$-tuple $(a_0, a_1, \ldots, a_{n-1})$ where each $a_i$ represents a coordinate in partition $\Pi_i$.

**Implementation**:

- Timepoints are represented as dictionaries that map unit names to values.
- The `create_timepoint` method constructs timepoints from user input.

```python
def create_timepoint(self, **kwargs):
    """
    Creates a timepoint dictionary, e.g. (a_0, ..., a_{n-1}) in the paper,
    from the user-specified partial info. Missing units default to 0.
    """
    # Initialize with 0 for all units
    tp = {u["name"]: 0 for u in self.units}
    # Fill any user-provided values
    for k, v in kwargs.items():
        if k not in tp:
            raise ValueError(f"Unknown unit '{k}' in create_timepoint(...)")
        tp[k] = v
    # We'll let normalizing or user calls handle out-of-range values, if any
    return self.normalize(tp)
```

### Definition 4: Canonical Form

A timepoint $\tau = (a_0, a_1, \ldots, a_{n-1})$ is in canonical form if for all $i \in \{0, 1, \ldots, n-2\}$, we have $0 \leq a_i < k_{i+1}$.

**Implementation**:

- The `normalize` method ensures timepoints are in canonical form.
- It works by converting to base units and then rebuilding the hierarchical representation.

```python
def normalize(self, timepoint):
    """
    Canonical normalization (Definition 7).  This ensures that for each unit i,
    the value is in [0, subdivisions_i), by carrying over to the coarser unit
    if necessary.
    """
    # Convert to the base unit measure
    total_base = self.to_base_units(timepoint)
    # Convert back from base to hierarchical
    return self.from_base_units(total_base)
```

### Definition 5: Absolute Representation

The absolute representation of a timepoint $\tau = (a_0, a_1, \ldots, a_{n-1})$ in the base units (partition $\Pi_n$) is defined as:

$$|\tau|_{U_n} = \sum_{i=0}^{n-1} a_i \cdot \prod_{j=i+1}^{n} k_j$$

**Implementation**:

- The `to_base_units` method computes the absolute representation of a timepoint.
- It uses the precomputed conversion factors to efficiently calculate the total.

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

## Operations

### Axiom 1: Temporal Addition

For timepoints $\tau_1$ and $\tau_2$, the temporal addition operation $\oplus$ is defined as:

$$\tau_1 \oplus \tau_2 = \mathcal{N}(\tau_1 + \tau_2)$$

where $\mathcal{N}$ is the normalization function and addition is performed by converting to absolute representation, adding, and then converting back.

**Properties**:

1. Associativity: $(\tau_1 \oplus \tau_2) \oplus \tau_3 = \tau_1 \oplus (\tau_2 \oplus \tau_3)$
2. Commutativity: $\tau_1 \oplus \tau_2 = \tau_2 \oplus \tau_1$
3. Identity: $\tau \oplus \mathbf{0} = \tau$ where $\mathbf{0}$ is the zero timepoint

**Implementation**:

- The `add_time` method implements temporal addition.
- It converts timepoints to base units, adds them, and then normalizes the result.

```python
def add_time(self, tp, **kwargs):
    """
    Implementation of Tau ⊕ Tau' (Temporal Addition, Axiom in the paper).
    1) Convert both to base
    2) sum
    3) re-normalize
    """
    base_main = self.to_base_units(tp)
    # Build an additive timepoint from kwargs, e.g. step=5
    addition_tp = self.create_timepoint(**kwargs)
    base_add = self.to_base_units(addition_tp)
    summed = base_main + base_add
    return self.from_base_units(summed)
```

### Axiom 2: Temporal Subtraction

For timepoints $\tau_1$ and $\tau_2$, the temporal subtraction operation $\ominus$ is defined as:

$$\tau_1 \ominus \tau_2 = \mathcal{N}(\tau_1 - \tau_2)$$

provided that $|\tau_1|_{U_n} \geq |\tau_2|_{U_n}$, i.e., the result is non-negative.

**Implementation**:

- The `subtract_time` method implements temporal subtraction.
- It checks that the result will be non-negative before performing the operation.

```python
def subtract_time(self, tp, **kwargs):
    """
    Implementation of Tau ⊖ Tau' (Temporal Subtraction, Axiom in the paper).
    """
    base_main = self.to_base_units(tp)
    sub_tp = self.create_timepoint(**kwargs)
    base_sub = self.to_base_units(sub_tp)
    if base_sub > base_main:
        raise ValueError("Subtraction would produce a negative time result.")
    result = base_main - base_sub
    return self.from_base_units(result)
```

### Definition 6: Timepoint Comparison

For timepoints $\tau_1$ and $\tau_2$, the comparison is defined based on their absolute representations:

$$\tau_1 < \tau_2 \iff |\tau_1|_{U_n} < |\tau_2|_{U_n}$$
$$\tau_1 = \tau_2 \iff |\tau_1|_{U_n} = |\tau_2|_{U_n}$$
$$\tau_1 > \tau_2 \iff |\tau_1|_{U_n} > |\tau_2|_{U_n}$$

**Implementation**:

- The `compare_timepoints` method implements timepoint comparison.
- It returns -1, 0, or 1 depending on whether the first timepoint is less than, equal to, or greater than the second.

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
    if b1 < b2:
        return -1
    elif b1 > b2:
        return 1
    else:
        return 0
```

## Human-Agent Time Mapping

### Definition 7: Human Time Morphism

A morphism $\phi: T \rightarrow H$ maps timepoints in the agent Temporal Universe $T$ to their representation in human time $H$.

**Implementation**:

- The `to_human_time` method implements the morphism from agent time to human time.
- It maps each unit to its corresponding human time unit based on a predefined mapping.

```python
def to_human_time(self, agent_tp):
    """
    The direct morphism phi: T -> H from the paper (Definition 18).
    We reverse the mapping above, e.g. step->seconds, cycle->minutes, ...
    """
    known_map = {
        "step": "seconds",
        "cycle": "minutes",
        "epoch": "hours"
        # microstep could map to "milliseconds" if you like
    }
    # Normalize first
    agent_tp = self.normalize(agent_tp)
    human_dict = {}
    for u_name, amount in agent_tp.items():
        if u_name in known_map:
            h_key = known_map[u_name]
            human_dict[h_key] = amount
    return human_dict
```

### Definition 8: Human Time Inverse Morphism

An inverse morphism $\phi^{-1}: H \rightarrow T$ maps human time representations to timepoints in the agent Temporal Universe.

**Implementation**:

- The `from_human_time` method implements the inverse morphism from human time to agent time.
- It converts human time units to their corresponding agent time units based on the mapping.

```python
def from_human_time(self, human_dict):
    """
    Suppose human_dict = {"seconds": 30, "minutes": 2},
    and we've decided to map e.g. "step" -> "seconds", "cycle" -> "minutes", etc.
    This method is the morphism phi^-1: H -> T in the paper.
    For simplicity, we assume the keys match some known mapping in code.
    """
    # Example: you can define your own mapping. For demonstration:
    known_map = {
        "seconds": "step",
        "minutes": "cycle",
        "hours": "epoch"
    }
    agent_tp = {u["name"]: 0 for u in self.units}
    for h_key, val in human_dict.items():
        if h_key not in known_map:
            raise ValueError(f"Human unit {h_key} not recognized.")
        agent_unit = known_map[h_key]
        agent_tp[agent_unit] = val
    return self.normalize(agent_tp)
```

## Theorems

### Theorem 1: Canonical Form Uniqueness

For any timepoint $\tau$ in a Temporal Universe $\mathcal{T}$, there exists a unique canonical form representation.

**Proof**:
The canonical form is obtained by the normalization process, which converts a timepoint to its absolute representation and then rebuilds the hierarchical representation with values in the canonical ranges. This process is deterministic and always produces the same result for equivalent timepoints.

**Implementation**:

- The uniqueness is guaranteed by the implementation of the `normalize` method.
- It always produces the same canonical form for timepoints that represent the same point in time.

### Theorem 2: Operation Consistency

For timepoints $\tau_1$ and $\tau_2$ in canonical form, the operations $\oplus$ and $\ominus$ preserve the temporal semantics, i.e., the operations correctly reflect the intended time manipulation.

**Proof**:
The operations are implemented by converting to absolute representation, performing the arithmetic operation, and then converting back to canonical form. This ensures that the operations work with the actual time values and produce correct results.

**Implementation**:

- The consistency is ensured by the implementation of `add_time` and `subtract_time`.
- They operate on the absolute representation to ensure correct temporal semantics.

## Relationship to Other Concepts

### Hierarchical Partition

The Temporal Universe relies on the concept of hierarchical partitions of time. See [Hierarchical Partition](hierarchical_partition.md) for more details.

### Timepoint Operations

The operations defined on timepoints (addition, subtraction, comparison) form an algebraic structure. See [Timepoint Operations](timepoint_operations.md) for more details.

### Morphisms

The mapping between agent time and human time is defined using morphisms. See [Morphisms](morphisms.md) for more details.

## Implementation Notes

The `AgentTemporal` class implements the Temporal Universe and provides methods for creating and manipulating timepoints. The hierarchical structure is represented by the `units` list, and conversion factors are precomputed for efficiency.

The class provides a default configuration with common time units (epoch, cycle, step, microstep), but users can define custom hierarchies as needed.

```python
# Example: Creating a custom temporal hierarchy
custom_config = [
    {"name": "project", "subdivisions": 4},     # 1 project = 4 phases
    {"name": "phase", "subdivisions": 5},       # 1 phase = 5 iterations
    {"name": "iteration", "subdivisions": 10},  # 1 iteration = 10 days
    {"name": "day", "subdivisions": 8},         # 1 day = 8 hours
    {"name": "hour", "subdivisions": None, "is_base": True}  # Base unit
]

project_time = AgentTemporal(custom_config)
```

The operations on timepoints are implemented with consideration for mathematical correctness and computational efficiency. The use of precomputed conversion factors allows for fast conversion between different levels of the hierarchy.

## References

1. **Mathematical Time Structures for Agent Systems**: Section 2: Temporal Universe
2. **Discrete Time Hierarchies**: Foundational concepts in computer science and discrete mathematics
3. **Category Theory for Time Representations**: Morphisms between temporal structures
