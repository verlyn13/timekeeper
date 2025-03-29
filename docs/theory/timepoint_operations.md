# Timepoint Operations

## Overview

Timepoint operations define the algebraic structure of operations on timepoints within the Timekeeper framework. This document provides the formal definitions, properties, and theorems related to timepoint operations and connects them to their implementation in the code.

## Definitions

### Definition 1: Timepoint Addition

Given timepoints $\tau_1$ and $\tau_2$ in a Temporal Universe $\mathcal{T}$, the addition operation $\oplus$ is defined as:

$$\tau_1 \oplus \tau_2 = \mathcal{N}(\tau_1 + \tau_2)$$

where $\mathcal{N}$ is the normalization function that converts a timepoint to its canonical form, and $+$ represents the coordinate-wise addition of timepoint components.

**Implementation**:
The `add_time` method in the `AgentTemporal` class implements timepoint addition.

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

### Definition 2: Timepoint Subtraction

Given timepoints $\tau_1$ and $\tau_2$ in a Temporal Universe $\mathcal{T}$, the subtraction operation $\ominus$ is defined as:

$$\tau_1 \ominus \tau_2 = \mathcal{N}(\tau_1 - \tau_2)$$

provided that $|\tau_1|_{U_n} \geq |\tau_2|_{U_n}$, where $|\tau|_{U_n}$ is the absolute representation of $\tau$ in base units, ensuring that the result is non-negative.

**Implementation**:
The `subtract_time` method in the `AgentTemporal` class implements timepoint subtraction.

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

### Definition 3: Timepoint Comparison

Given timepoints $\tau_1$ and $\tau_2$ in a Temporal Universe $\mathcal{T}$, the comparison operation is defined based on their absolute representations:

$$\tau_1 < \tau_2 \iff |\tau_1|_{U_n} < |\tau_2|_{U_n}$$
$$\tau_1 = \tau_2 \iff |\tau_1|_{U_n} = |\tau_2|_{U_n}$$
$$\tau_1 > \tau_2 \iff |\tau_1|_{U_n} > |\tau_2|_{U_n}$$

**Implementation**:
The `compare_timepoints` method in the `AgentTemporal` class implements timepoint comparison.

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

### Definition 4: Time Difference

The time difference between timepoints $\tau_1$ and $\tau_2$ is defined as the absolute value of their difference in base units, converted back to a timepoint:

$$\Delta(\tau_1, \tau_2) = \mathcal{N}(||\tau_1|_{U_n} - |\tau_2|_{U_n}|)$$

**Implementation**:
The `time_difference` method in the `AgentTemporal` class implements this operation.

```python
def time_difference(self, t1, t2):
    """
    Returns |t2 - t1| as a timepoint dict.
    In the math doc, this is basically (t2 ⊖ t1) in absolute value sense.
    """
    b1 = self.to_base_units(t1)
    b2 = self.to_base_units(t2)
    diff = abs(b2 - b1)
    return self.from_base_units(diff)
```

## Properties

### Property 1: Associativity of Addition

For timepoints $\tau_1$, $\tau_2$, and $\tau_3$, the addition operation $\oplus$ is associative:

$$(\tau_1 \oplus \tau_2) \oplus \tau_3 = \tau_1 \oplus (\tau_2 \oplus \tau_3)$$

**Proof**:
This follows from the associativity of addition in the base unit representation. When timepoints are converted to base units, added, and then normalized back, the associativity property is preserved.

**Implementation**:
The implementation of `add_time` ensures associativity by working with absolute representations.

### Property 2: Commutativity of Addition

For timepoints $\tau_1$ and $\tau_2$, the addition operation $\oplus$ is commutative:

$$\tau_1 \oplus \tau_2 = \tau_2 \oplus \tau_1$$

**Proof**:
This follows from the commutativity of addition in the base unit representation. When timepoints are converted to base units, added, and then normalized back, the commutativity property is preserved.

**Implementation**:
The implementation of `add_time` ensures commutativity by working with absolute representations.

### Property 3: Identity Element for Addition

There exists a timepoint $\tau_0$ (the zero timepoint) such that for any timepoint $\tau$:

$$\tau \oplus \tau_0 = \tau_0 \oplus \tau = \tau$$

**Proof**:
The timepoint where all coordinates are zero serves as the identity element. When added to any other timepoint, it does not change the value.

**Implementation**:
The `create_timepoint` method without arguments creates the zero timepoint.

```python
# Creating the zero timepoint
zero = temporal.create_timepoint()  # All units set to 0
```

### Property 4: Non-Negative Time

The temporal system enforces non-negative time, which means that timepoint subtraction is only defined when the result is non-negative.

**Implementation**:
The `subtract_time` method checks that the result will be non-negative before performing the operation.

```python
def subtract_time(self, tp, **kwargs):
    # ...
    if base_sub > base_main:
        raise ValueError("Subtraction would produce a negative time result.")
    # ...
```

### Property 5: Total Ordering

The comparison operation defines a total ordering on timepoints, which means that for any two timepoints $\tau_1$ and $\tau_2$, exactly one of the following holds:

- $\tau_1 < \tau_2$
- $\tau_1 = \tau_2$
- $\tau_1 > \tau_2$

**Proof**:
This follows from the total ordering of real numbers, as timepoints are compared based on their absolute representations as real numbers.

**Implementation**:
The `compare_timepoints` method implements this total ordering by comparing base unit representations.

### Property 6: Transitivity of Comparison

For timepoints $\tau_1$, $\tau_2$, and $\tau_3$, if $\tau_1 < \tau_2$ and $\tau_2 < \tau_3$, then $\tau_1 < \tau_3$.

**Proof**:
This follows from the transitivity of the less-than relation on real numbers, as timepoints are compared based on their absolute representations.

**Implementation**:
The `compare_timepoints` method inherits transitivity from the comparison of base unit values.

## Theorems

### Theorem 1: Addition Preserves Canonical Form

For timepoints $\tau_1$ and $\tau_2$ in canonical form, $\tau_1 \oplus \tau_2$ is also in canonical form.

**Proof**:
The addition operation explicitly includes normalization, which ensures that the result is in canonical form regardless of whether the inputs are in canonical form.

**Implementation**:
The `add_time` method calls `from_base_units`, which produces timepoints in canonical form.

### Theorem 2: Subtraction Preserves Canonical Form

For timepoints $\tau_1$ and $\tau_2$ in canonical form, if $\tau_1 \geq \tau_2$, then $\tau_1 \ominus \tau_2$ is also in canonical form.

**Proof**:
Similar to addition, the subtraction operation includes normalization, which ensures that the result is in canonical form.

**Implementation**:
The `subtract_time` method calls `from_base_units`, which produces timepoints in canonical form.

### Theorem 3: Uniqueness of Representation

For any two timepoints $\tau_1$ and $\tau_2$ in canonical form, $\tau_1 = \tau_2$ if and only if they have identical coordinate values.

**Proof**:
The canonical form provides a unique representation for each point in time. If two timepoints have the same canonical form, they represent the same point in time, and vice versa.

**Implementation**:
The `normalize` method ensures that timepoints are in canonical form, which guarantees uniqueness of representation.

## Applications

### Time Advancement

Timepoint addition can be used to advance time by specific increments, which is useful in simulations and scheduling.

**Example**:

```python
# Advance time by 5 cycles and 10 steps
current_time = temporal.create_timepoint(epoch=1, cycle=20, step=50)
advanced_time = temporal.add_time(current_time, cycle=5, step=10)
```

### Time Intervals

Timepoint subtraction and time difference can be used to calculate the duration between two timepoints.

**Example**:

```python
# Calculate the interval between two timepoints
start_time = temporal.create_timepoint(epoch=1, cycle=10, step=0)
end_time = temporal.create_timepoint(epoch=1, cycle=15, step=30)
interval = temporal.time_difference(start_time, end_time)
```

### Scheduling

The comparison operation is essential for scheduling tasks in order and ensuring that dependencies are respected.

**Example**:

```python
# Check if a task can start after its dependency ends
if temporal.compare_timepoints(dependency_end_time, task_start_time) <= 0:
    # Task can start
else:
    # Task must wait
```

## Relationship to Other Concepts

### Temporal Universe

Timepoint operations are defined within the context of a Temporal Universe. See [Temporal Universe](temporal_universe.md) for more details.

### Hierarchical Partition

The structure of the hierarchical partition determines how timepoint operations work. See [Hierarchical Partition](hierarchical_partition.md) for more details.

### Task Scheduling

Timepoint operations are foundational for the task scheduling functionality. The `TaskScheduler` class uses these operations to determine task start and end times and to respect dependencies.

```python
# Example from TaskScheduler.schedule method
def schedule(self, agent_count=1):
    # ...
    # Find the earliest time this task can start
    # ...
    if self.temporal.compare_timepoints(earliest_agent_time, earliest_start) > 0:
        task_start = earliest_agent_time
    else:
        task_start = earliest_start

    # Calculate end time
    task_end = self.temporal.add_time(task_start, **task["duration"])
    # ...
```

## Implementation Notes

The implementation of timepoint operations in the `AgentTemporal` class focuses on correctness and efficiency:

1. **Base Unit Conversion**: Operations convert timepoints to base units, perform the operation, and then convert back to canonical form. This approach ensures mathematical correctness.

2. **Error Handling**: The `subtract_time` method checks that the result will be non-negative before performing the operation, which enforces the non-negative time property.

3. **Efficiency**: Precomputed conversion factors are used to make the operations more efficient, especially for complex temporal hierarchies.

4. **Flexibility**: The operations work with any valid hierarchy of time units, allowing for customization to different application domains.

## References

1. **Mathematical Time Structures for Agent Systems**: Section 4: Timepoint Operations
2. **Algebra of Time**: Formal operations on temporal structures
3. **Temporal Logic in Computer Science**: Ordering relations in time
