# AgentTemporal Docstring Enhancement Plan

## Overview

This document provides a detailed implementation plan for enhancing the docstrings in the `AgentTemporal` class with LaTeX formulas and cross-references to theoretical documentation. This implementation follows the guidelines in the [Docstring Enhancement Guide](docstring_enhancement_guide.md).

## Current State

The current docstrings in `AgentTemporal` provide basic information about the class and its methods, with references to mathematical concepts but without formal LaTeX notation or detailed cross-references.

## Enhancement Goals

1. Add formal mathematical definitions using LaTeX notation
2. Include cross-references to theoretical documentation
3. Clearly connect implementation details with mathematical concepts
4. Provide comprehensive examples for methods
5. Document mathematical properties and theorems

## Implementation Details

### Class Docstring Enhancement

Current:

```python
class AgentTemporal:
    """
    Maps directly to the fundamental time system described in the paper, covering:
      - The 'Temporal Universe' T (Definition 1)
      - Hierarchical partitions {Pi_0, Pi_1, ..., Pi_n} (Definitions 2-4)
      - Subdivision factors k_{i+1} (Definition 5)
      - Timepoints (Definition 6), plus canonical normalization (Definition 7)
      - Operations: addition, subtraction, compare, etc. (Axioms of temporal addition/subtraction)
      - Absolute representation in base units (Definition 9)

    NOTE: The dictionary-based representation of timepoints is the software analog
    to the tuple (a_0, a_1, ..., a_{n-1}) in the math doc.
    """
```

Enhanced:

```python
class AgentTemporal:
    """
    A comprehensive implementation of a hierarchical temporal system for agents.

    Mathematical Foundation:
    -----------------------
    This class implements the Temporal Universe (𝒯) defined as:

    \[ 𝒯 = (T, \{\Pi_0, \Pi_1, \ldots, \Pi_n\}, \{k_1, k_2, \ldots, k_n\}) \]

    where:
    - $T$ is the time domain (Definition 1)
    - $\Pi_i$ are hierarchical partitions of $T$ (Definitions 2-4)
    - $k_i$ are subdivision factors: $|\Pi_{i-1}(t)| = k_i \cdot |\Pi_i(t)|$ (Definition 5)

    Timepoints are represented as tuples $(a_0, a_1, \ldots, a_{n-1})$ where $a_i$
    represents a coordinate in partition $\Pi_i$ (Definition 6). The dictionary-based
    implementation maps unit names to these coordinates.

    Key Mathematical Properties:
    --------------------------
    1. Canonical Form: Every timepoint has a unique canonical representation
       where $0 \leq a_i < k_{i+1}$ for $0 \leq i < n-1$ (Definition 7)

    2. Temporal Addition (⊕): Defined as coordinate-wise addition followed by
       normalization to canonical form (Axiom 1)

    3. Temporal Subtraction (⊖): Inverse of addition, defined only when the
       result remains non-negative (Axiom 2)

    4. Absolute Representation: Every timepoint can be represented as an
       absolute value in the base units: $|\\tau|_{U_n}$ (Definition 9)

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md) for complete theory.
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md) for details on partitions.
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md) for operation definitions.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10)
    >>> t2 = temporal.add_time(t1, cycle=5)
    >>> comparison = temporal.compare_timepoints(t1, t2)  # Returns -1 (t1 < t2)
    """
```

### `__init__` Method Enhancement

Current:

```python
def __init__(self, unit_config=None):
    """
    Args:
        unit_config: Optional custom specification of the hierarchy of time units.
                     If None, a default set of partitions is used.
    """
```

Enhanced:

```python
def __init__(self, unit_config=None):
    """
    Initialize a new temporal universe with the specified hierarchy of time units.

    Mathematical Definition:
    ----------------------
    This constructor establishes a Temporal Universe 𝒯 with the given hierarchical
    partitions and subdivision factors:

    \[ 𝒯 = (T, \{\Pi_0, \Pi_1, \ldots, \Pi_n\}, \{k_1, k_2, \ldots, k_n\}) \]

    The hierarchical structure is defined by the `unit_config` parameter, which
    specifies the names and subdivision factors for each level of the hierarchy.

    Parameters:
    ----------
    unit_config : list of dict, optional
        Custom specification of the hierarchy of time units. Each dictionary should
        contain:
        - "name": The name of the time unit (string)
        - "subdivisions": How many units of the next finer level fit into one unit
                         of this level (int), or None for the base unit
        - "is_base": True if this is the base (finest) unit, False otherwise

        If None, a default set of partitions is used:
        - epoch (24 cycles per epoch)
        - cycle (60 steps per cycle)
        - step (1000 microsteps per step)
        - microstep (base unit)

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md#definitions) for
      details on temporal universe structure.

    Examples:
    --------
    >>> # Using default configuration
    >>> temporal = AgentTemporal()
    >>>
    >>> # Using custom configuration
    >>> custom_config = [
    ...     {"name": "project", "subdivisions": 3},
    ...     {"name": "phase", "subdivisions": 4},
    ...     {"name": "task", "subdivisions": 5},
    ...     {"name": "step", "subdivisions": None, "is_base": True}
    ... ]
    >>> custom_temporal = AgentTemporal(custom_config)
    """
```

### `_compute_conversions` Method Enhancement

Current:

```python
def _compute_conversions(self):
    """
    For each pair (unit_i, unit_j), store how many 'unit_j' in one 'unit_i',
    i.e. a factor for converting from i -> j.  This parallels the ratio
    of partition sizes in the math doc.
    """
```

Enhanced:

```python
def _compute_conversions(self):
    """
    Compute conversion factors between all pairs of time units.

    Mathematical Definition:
    ----------------------
    This method precomputes the conversion factors $c_{i,j}$ where $c_{i,j}$ represents
    how many units of $\Pi_j$ fit into one unit of $\Pi_i$:

    \[ c_{i,j} = \frac{|\Pi_j(t)|}{|\Pi_i(t)|} = \begin{cases}
       \prod_{l=i+1}^{j} k_l & \text{if } i < j \\
       1 & \text{if } i = j \\
       \frac{1}{\prod_{l=j+1}^{i} k_l} & \text{if } i > j
    \end{cases} \]

    where $|\Pi_i(t)|$ is the size of the partition $\Pi_i$ containing $t$, and
    $k_l$ are the subdivision factors.

    These conversion factors are used to efficiently perform operations like
    addition, subtraction, and comparison by providing a quick way to convert
    between different levels of the temporal hierarchy.

    References:
    ----------
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#properties) for
      details on conversion between partition levels.

    Notes:
    -----
    This is an internal method called during initialization and after any
    structural changes to the temporal hierarchy.
    """
```

### `create_timepoint` Method Enhancement

Current:

```python
def create_timepoint(self, **kwargs):
    """
    Creates a timepoint dictionary, e.g. (a_0, ..., a_{n-1}) in the paper,
    from the user-specified partial info. Missing units default to 0.
    """
```

Enhanced:

```python
def create_timepoint(self, **kwargs):
    """
    Create a timepoint with specified unit values.

    Mathematical Definition:
    ----------------------
    This method creates a timepoint $\tau = (a_0, a_1, \ldots, a_{n-1})$ where
    each $a_i$ represents a coordinate in partition $\Pi_i$. The implementation
    represents this as a dictionary mapping unit names to values.

    The timepoint is automatically normalized to canonical form, where
    $0 \leq a_i < k_{i+1}$ for $0 \leq i < n-1$.

    Parameters:
    ----------
    **kwargs : dict
        Unit values specified as keyword arguments (e.g., epoch=1, cycle=10).
        Units not specified default to 0.

    Returns:
    -------
    dict
        A dictionary mapping unit names to values, representing a timepoint
        in canonical form.

    Raises:
    ------
    ValueError
        If an unknown unit name is provided.

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md#definition-3-timepoint) for
      details on timepoint representation.
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#definition-5-canonical-coordinates) for
      details on canonical coordinates.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Create with specific values
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> # Create with partial specification
    >>> t2 = temporal.create_timepoint(cycle=15)  # epoch=0, step=0, microstep=0 by default
    >>> # Create with values that need normalization
    >>> t3 = temporal.create_timepoint(cycle=70)  # Normalized to epoch=1, cycle=10
    """
```

### `normalize` Method Enhancement

Current:

```python
def normalize(self, timepoint):
    """
    Canonical normalization (Definition 7).  This ensures that for each unit i,
    the value is in [0, subdivisions_i), by carrying over to the coarser unit
    if necessary.
    """
```

Enhanced:

```python
def normalize(self, timepoint):
    """
    Normalize a timepoint to its canonical form.

    Mathematical Definition:
    ----------------------
    This method implements the normalization function $\mathcal{N}$ that
    converts a timepoint to its canonical form:

    \[ \mathcal{N}(\tau) = (b_0, b_1, \ldots, b_{n-1}) \]

    where:
    - $\tau = (a_0, a_1, \ldots, a_{n-1})$ is the input timepoint
    - For all $i \in \{0, 1, \ldots, n-2\}$, $0 \leq b_i < k_{i+1}$
    - $|\tau|_{U_n} = |\mathcal{N}(\tau)|_{U_n}$ (absolute representation is preserved)

    The normalization process ensures that each coordinate is within the
    appropriate range for its position in the hierarchy, carrying excess
    values to coarser units when necessary.

    Parameters:
    ----------
    timepoint : dict
        A dictionary mapping unit names to values, representing a timepoint
        that may not be in canonical form.

    Returns:
    -------
    dict
        A dictionary mapping unit names to values, representing the input
        timepoint in canonical form.

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md#definition-4-canonical-form) for
      details on canonical form.
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#property-1-canonical-form-uniqueness) for
      details on canonical form uniqueness.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Normalize a timepoint with out-of-range values
    >>> non_canonical = {'epoch': 1, 'cycle': 70, 'step': 30, 'microstep': 0}
    >>> canonical = temporal.normalize(non_canonical)
    >>> # Result: {'epoch': 2, 'cycle': 10, 'step': 30, 'microstep': 0}
    """
```

### `to_base_units` Method Enhancement

Current:

```python
def to_base_units(self, timepoint):
    """
    = |tau|_{U_n} in the paper (Definition 9).
    Sums up each a_i * conversion_factor to the base partition.
    """
```

Enhanced:

```python
def to_base_units(self, timepoint):
    """
    Convert a timepoint to its absolute representation in base units.

    Mathematical Definition:
    ----------------------
    This method implements the absolute representation function $|\cdot|_{U_n}$
    that maps a timepoint to a scalar value in the base units:

    \[ |\tau|_{U_n} = \sum_{i=0}^{n-1} a_i \cdot \prod_{j=i+1}^{n} k_j \]

    where:
    - $\tau = (a_0, a_1, \ldots, a_{n-1})$ is the timepoint
    - $k_j$ are the subdivision factors
    - $U_n$ is the base (finest) partition

    This absolute representation provides a common basis for comparing
    and manipulating timepoints.

    Parameters:
    ----------
    timepoint : dict
        A dictionary mapping unit names to values, representing a timepoint.

    Returns:
    -------
    float
        The absolute representation of the timepoint in the base units.

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md#definition-5-absolute-representation) for
      details on absolute representation.
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#property-2-base-unit-conversion) for
      details on base unit conversion.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Convert a timepoint to base units (microsteps)
    >>> tp = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> # For default config: 1 epoch = 24*60*1000 microsteps, 10 cycles = 10*60*1000 microsteps, etc.
    >>> base_units = temporal.to_base_units(tp)
    >>> # Result is 1*24*60*1000 + 10*60*1000 + 30*1000 = 2,070,000
    """
```

### `from_base_units` Method Enhancement

Current:

```python
def from_base_units(self, base_value):
    """
    The inverse of to_base_units, i.e. given an absolute measure in the base partition,
    reconstruct the hierarchical representation (a_0, a_1, ..., a_{n-1}).
    """
```

Enhanced:

```python
def from_base_units(self, base_value):
    """
    Convert an absolute base unit value to a timepoint.

    Mathematical Definition:
    ----------------------
    This method is the inverse of the absolute representation function,
    reconstructing a timepoint $\tau = (a_0, a_1, \ldots, a_{n-1})$ from
    its absolute representation $|\tau|_{U_n}$ in the base units:

    \[ a_i = \lfloor \frac{|\tau|_{U_n} - \sum_{j=0}^{i-1} a_j \cdot \prod_{l=j+1}^{n} k_l}{\prod_{l=i+1}^{n} k_l} \rfloor \mod k_{i+1} \]

    for $i < n-1$, and $a_{n-1} = |\tau|_{U_n} - \sum_{j=0}^{n-2} a_j \cdot \prod_{l=j+1}^{n} k_l$.

    The resulting timepoint is always in canonical form.

    Parameters:
    ----------
    base_value : float
        An absolute value in the base units.

    Returns:
    -------
    dict
        A dictionary mapping unit names to values, representing a timepoint
        in canonical form with the given absolute value.

    References:
    ----------
    - See [Temporal Universe](/docs/theory/temporal_universe.md#definition-5-absolute-representation) for
      details on absolute representation.
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#property-2-base-unit-conversion) for
      details on base unit conversion.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Convert a base unit value to a timepoint
    >>> base_value = 2_070_000  # 1 epoch, 10 cycles, 30 steps, 0 microsteps
    >>> tp = temporal.from_base_units(base_value)
    >>> # Result: {'epoch': 1, 'cycle': 10, 'step': 30, 'microstep': 0}
    """
```

### `add_time` Method Enhancement

Current:

```python
def add_time(self, tp, **kwargs):
    """
    Implementation of Tau ⊕ Tau' (Temporal Addition, Axiom in the paper).
    1) Convert both to base
    2) sum
    3) re-normalize
    """
```

Enhanced:

```python
def add_time(self, tp, **kwargs):
    """
    Add time to a timepoint.

    Mathematical Definition:
    ----------------------
    This method implements the temporal addition operation $\oplus$ defined as:

    \[ \tau_1 \oplus \tau_2 = \mathcal{N}(\tau_1 + \tau_2) \]

    where:
    - $\tau_1$ and $\tau_2$ are timepoints
    - $\mathcal{N}$ is the normalization function
    - $+$ represents the coordinate-wise addition

    The operation satisfies these properties:
    1. Associativity: $(\tau_1 \oplus \tau_2) \oplus \tau_3 = \tau_1 \oplus (\tau_2 \oplus \tau_3)$
    2. Commutativity: $\tau_1 \oplus \tau_2 = \tau_2 \oplus \tau_1$
    3. Identity: $\tau \oplus \mathbf{0} = \tau$ where $\mathbf{0}$ is the zero timepoint

    Parameters:
    ----------
    tp : dict
        The timepoint to which time will be added.
    **kwargs : dict
        Time to add, specified as keyword arguments (e.g., cycle=5, step=10).

    Returns:
    -------
    dict
        A new timepoint resulting from the addition, in canonical form.

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#definition-1-timepoint-addition) for
      details on timepoint addition.
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#property-1-associativity-of-addition) for
      properties of addition.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> # Add 5 cycles and 50 steps
    >>> t2 = temporal.add_time(t1, cycle=5, step=50)
    >>> # Result: {'epoch': 1, 'cycle': 15, 'step': 80, 'microstep': 0}
    >>>
    >>> # Addition with carry-over
    >>> t3 = temporal.add_time(t1, cycle=55)  # 10+55=65 cycles, normalized to 1 epoch, 5 cycles
    >>> # Result: {'epoch': 2, 'cycle': 5, 'step': 30, 'microstep': 0}
    """
```

### `subtract_time` Method Enhancement

Current:

```python
def subtract_time(self, tp, **kwargs):
    """
    Implementation of Tau ⊖ Tau' (Temporal Subtraction, Axiom in the paper).
    """
```

Enhanced:

```python
def subtract_time(self, tp, **kwargs):
    """
    Subtract time from a timepoint.

    Mathematical Definition:
    ----------------------
    This method implements the temporal subtraction operation $\ominus$ defined as:

    \[ \tau_1 \ominus \tau_2 = \mathcal{N}(\tau_1 - \tau_2) \]

    where:
    - $\tau_1$ and $\tau_2$ are timepoints
    - $\mathcal{N}$ is the normalization function
    - $-$ represents the coordinate-wise subtraction

    The operation is only defined when the result is non-negative, i.e.,
    when $|\tau_1|_{U_n} \geq |\tau_2|_{U_n}$.

    Parameters:
    ----------
    tp : dict
        The timepoint from which time will be subtracted.
    **kwargs : dict
        Time to subtract, specified as keyword arguments (e.g., cycle=5, step=10).

    Returns:
    -------
    dict
        A new timepoint resulting from the subtraction, in canonical form.

    Raises:
    ------
    ValueError
        If the subtraction would result in a negative time.

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#definition-2-timepoint-subtraction) for
      details on timepoint subtraction.
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#property-4-non-negative-time) for
      the non-negative time property.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=2, cycle=20, step=500)
    >>> # Subtract 10 cycles and 200 steps
    >>> t2 = temporal.subtract_time(t1, cycle=10, step=200)
    >>> # Result: {'epoch': 2, 'cycle': 10, 'step': 300, 'microstep': 0}
    >>>
    >>> # Subtraction with borrowing
    >>> t3 = temporal.subtract_time(t1, cycle=21)  # Need to borrow from epoch
    >>> # Result: {'epoch': 1, 'cycle': 59, 'step': 500, 'microstep': 0}
    """
```

### `compare_timepoints` Method Enhancement

Current:

```python
def compare_timepoints(self, t1, t2):
    """
    Lexicographical order in the math doc is effectively a base-unit comparison.
    Return:
      -1 if t1 < t2
       0 if t1 == t2
       1 if t1 > t2
    """
```

Enhanced:

```python
def compare_timepoints(self, t1, t2):
    """
    Compare two timepoints.

    Mathematical Definition:
    ----------------------
    This method implements the comparison of timepoints based on their
    absolute representations:

    \[ \tau_1 < \tau_2 \iff |\tau_1|_{U_n} < |\tau_2|_{U_n} \]
    \[ \tau_1 = \tau_2 \iff |\tau_1|_{U_n} = |\tau_2|_{U_n} \]
    \[ \tau_1 > \tau_2 \iff |\tau_1|_{U_n} > |\tau_2|_{U_n} \]

    This defines a total ordering on timepoints.

    Parameters:
    ----------
    t1 : dict
        The first timepoint to compare.
    t2 : dict
        The second timepoint to compare.

    Returns:
    -------
    int
        -1 if t1 < t2, 0 if t1 == t2, 1 if t1 > t2.

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#definition-3-timepoint-comparison) for
      details on timepoint comparison.
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#property-5-total-ordering) for
      the total ordering property.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> t2 = temporal.create_timepoint(epoch=1, cycle=10, step=40)
    >>> t3 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>>
    >>> temporal.compare_timepoints(t1, t2)  # Returns -1 (t1 < t2)
    >>> temporal.compare_timepoints(t1, t3)  # Returns 0 (t1 == t3)
    >>> temporal.compare_timepoints(t2, t1)  # Returns 1 (t2 > t1)
    """
```

### `time_difference` Method Enhancement

Current:

```python
def time_difference(self, t1, t2):
    """
    Returns |t2 - t1| as a timepoint dict.
    In the math doc, this is basically (t2 ⊖ t1) in absolute value sense.
    """
```

Enhanced:

```python
def time_difference(self, t1, t2):
    """
    Calculate the absolute time difference between two timepoints.

    Mathematical Definition:
    ----------------------
    This method calculates the absolute difference between two timepoints:

    \[ \Delta(\tau_1, \tau_2) = \mathcal{N}(||\tau_1|_{U_n} - |\tau_2|_{U_n}|) \]

    where:
    - $\tau_1$ and $\tau_2$ are timepoints
    - $|\tau|_{U_n}$ is the absolute representation in base units
    - $\mathcal{N}$ is the normalization function

    Parameters:
    ----------
    t1 : dict
        The first timepoint.
    t2 : dict
        The second timepoint.

    Returns:
    -------
    dict
        A timepoint representing the absolute difference between t1 and t2.

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#definition-4-time-difference) for
      details on time difference calculation.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> t2 = temporal.create_timepoint(epoch=1, cycle=15, step=40)
    >>>
    >>> # Calculate difference
    >>> diff = temporal.time_difference(t1, t2)
    >>> # Result: {'epoch': 0, 'cycle': 5, 'step': 10, 'microstep': 0}
    >>>
    >>> # Order doesn't matter for absolute difference
    >>> diff_rev = temporal.time_difference(t2, t1)
    >>> # Result is the same: {'epoch': 0, 'cycle': 5, 'step': 10, 'microstep': 0}
    """
```

### `from_human_time` Method Enhancement

Current:

```python
def from_human_time(self, human_dict):
    """
    Suppose human_dict = {"seconds": 30, "minutes": 2},
    and we've decided to map e.g. "step" -> "seconds", "cycle" -> "minutes", etc.
    This method is the morphism phi^-1: H -> T in the paper.
    For simplicity, we assume the keys match some known mapping in code.
    """
```

Enhanced:

```python
def from_human_time(self, human_dict):
    """
    Convert human time to agent time.

    Mathematical Definition:
    ----------------------
    This method implements the inverse morphism $\phi^{-1}: \mathcal{H} \rightarrow \mathcal{T}$
    from human time to agent time:

    \[ \phi^{-1}(h) = \mathcal{N}(\sum_{i \in I_h} h_i \cdot e_{\mu(i)}) \]

    where:
    - $h = (h_i)_{i \in I_h}$ is the human time representation
    - $\mu: I_h \rightarrow I_{\tau}$ is the mapping from human time units to agent time units
    - $e_j$ is the unit vector with 1 in position $j$ and 0 elsewhere
    - $\mathcal{N}$ is the normalization function

    Parameters:
    ----------
    human_dict : dict
        A dictionary mapping human time units to values
        (e.g., {"hours": 1, "minutes": 30, "seconds": 45}).

    Returns:
    -------
    dict
        A timepoint in the agent temporal universe equivalent to the given human time.

    Raises:
    ------
    ValueError
        If a human time unit is not recognized.

    References:
    ----------
    - See [Morphisms](/docs/theory/morphisms.md#definition-3-human-agent-morphism) for
      details on the human-agent morphism.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Convert human time to agent time
    >>> human_time = {"hours": 2, "minutes": 15, "seconds": 30}
    >>> agent_time = temporal.from_human_time(human_time)
    >>> # Result: {'epoch': 2, 'cycle': 15, 'step': 30, 'microstep': 0}
    >>>
    >>> # Convert partial human time
    >>> partial_time = {"minutes": 30}
    >>> agent_partial = temporal.from_human_time(partial_time)
    >>> # Result: {'epoch': 0, 'cycle': 30, 'step': 0, 'microstep': 0}
    """
```

### `to_human_time` Method Enhancement

Current:

```python
def to_human_time(self, agent_tp):
    """
    The direct morphism phi: T -> H from the paper (Definition 18).
    We reverse the mapping above, e.g. step->seconds, cycle->minutes, ...
    """
```

Enhanced:

```python
def to_human_time(self, agent_tp):
    """
    Convert agent time to human time.

    Mathematical Definition:
    ----------------------
    This method implements the morphism $\phi: \mathcal{T} \rightarrow \mathcal{H}$
    from agent time to human time:

    \[ \phi(\tau) = (h_i)_{i \in I_h} \text{ where } h_i = \tau_{\mu^{-1}(i)} \]

    where:
    - $\tau = (\tau_j)_{j \in I_{\tau}}$ is the agent timepoint
    - $\mu^{-1}: I_{\tau} \rightarrow I_h$ is the inverse mapping from agent time units to human time units

    Parameters:
    ----------
    agent_tp : dict
        A timepoint in the agent temporal universe.

    Returns:
    -------
    dict
        A dictionary mapping human time units to values.

    References:
    ----------
    - See [Morphisms](/docs/theory/morphisms.md#definition-2-agent-human-morphism) for
      details on the agent-human morphism.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> # Convert agent time to human time
    >>> agent_tp = temporal.create_timepoint(epoch=1, cycle=30, step=45)
    >>> human_time = temporal.to_human_time(agent_tp)
    >>> # Result: {'hours': 1, 'minutes': 30, 'seconds': 45}
    """
```

## Implementation Steps

To implement these docstring enhancements, follow these steps:

1. **Create a Backup**:

   ```bash
   cp src/python/agent_temporal.py src/python/agent_temporal.py.backup
   ```

2. **Open the File**:

   ```bash
   nano src/python/agent_temporal.py
   ```

3. **Replace Docstrings**:

   - Replace each docstring with its enhanced version
   - Start with the class docstring
   - Proceed through each method
   - Be careful not to modify any code, only the docstrings

4. **Verify LaTeX Syntax**:

   - Ensure all LaTeX formulas use proper syntax
   - Check for balanced delimiters: `\[...\]`, `$...$`
   - Verify escape sequences for backslashes in string literals

5. **Check Cross-References**:

   - Verify that all links to theory documentation use correct paths
   - Ensure anchors in the URLs match the actual headings in the target documents

6. **Test Documentation Generation**:
   - Run the documentation generation tools to verify that the LaTeX renders correctly
   - Check that cross-references resolve properly

## Validation Criteria

After implementation, the docstring enhancements should:

1. **Provide Mathematical Rigor**:

   - Formal definitions with proper LaTeX notation
   - Clear connection between mathematical concepts and implementation

2. **Support Bidirectional Traceability**:

   - Links from code to theory documentation
   - References to specific definitions, properties, and theorems

3. **Improve Documentation Quality**:

   - Clear examples for all methods
   - Consistent formatting and structure
   - Comprehensive parameter and return value documentation

4. **Maintain Readability**:
   - LaTeX should enhance, not hinder, understanding
   - Code examples should be clear and instructive
   - References should be helpful and relevant

## Next Steps

After enhancing the `AgentTemporal` class docstrings, proceed to:

1. **Test Documentation Generation**: Verify that Sphinx correctly renders the LaTeX formulas
2. **Enhance `TaskScheduler` Docstrings**: Apply similar enhancements to the `TaskScheduler` class
3. **Enhance `AdaptiveAgentTemporal` Docstrings**: Apply similar enhancements to the `AdaptiveAgentTemporal` class
4. **Update Examples**: Ensure the documentation examples are consistent with the enhanced docstrings
