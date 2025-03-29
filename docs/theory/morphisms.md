# Morphisms

## Overview

Morphisms in the Timekeeper framework define mappings between different time representations, particularly between agent time and human time. This document provides the formal definitions, properties, and theorems related to time morphisms and connects them to their implementation in the code.

## Definitions

### Definition 1: Time Morphism

A time morphism $\phi: \mathcal{T}_1 \rightarrow \mathcal{T}_2$ is a function that maps timepoints from one temporal universe $\mathcal{T}_1$ to another temporal universe $\mathcal{T}_2$ while preserving certain temporal properties.

**Implementation**:
The `to_human_time` and `from_human_time` methods in the `AgentTemporal` class implement time morphisms between agent time and human time.

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

### Definition 2: Agent-Human Morphism

The agent-human morphism $\phi: \mathcal{T} \rightarrow \mathcal{H}$ maps timepoints from the agent temporal universe $\mathcal{T}$ to the human temporal universe $\mathcal{H}$.

**Implementation**:
The `to_human_time` method implements this morphism using a mapping between agent time units and human time units.

```python
def to_human_time(self, agent_tp):
    """
    The direct morphism phi: T -> H from the paper (Definition 18).
    """
    known_map = {
        "step": "seconds",
        "cycle": "minutes",
        "epoch": "hours"
    }
    # ...
```

### Definition 3: Human-Agent Morphism

The human-agent morphism $\phi^{-1}: \mathcal{H} \rightarrow \mathcal{T}$ maps timepoints from the human temporal universe $\mathcal{H}$ to the agent temporal universe $\mathcal{T}$.

**Implementation**:
The `from_human_time` method implements this morphism using the inverse mapping.

```python
def from_human_time(self, human_dict):
    """
    This method is the morphism phi^-1: H -> T in the paper.
    """
    known_map = {
        "seconds": "step",
        "minutes": "cycle",
        "hours": "epoch"
    }
    # ...
```

### Definition 4: Property-Preserving Morphism

A morphism $\phi$ is property-preserving if it maintains certain temporal properties such as ordering or duration.

For example, a morphism $\phi$ preserves ordering if for any timepoints $\tau_1, \tau_2 \in \mathcal{T}_1$:

$$\tau_1 < \tau_2 \implies \phi(\tau_1) < \phi(\tau_2)$$

**Implementation**:
The agent-human and human-agent morphisms in the Timekeeper framework preserve ordering and approximate duration.

## Properties

### Property 1: Bidirectional Consistency

For a bidirectional mapping between agent time and human time to be consistent, the composition of the two morphisms should approximate the identity function:

$$\phi^{-1} \circ \phi(\tau) \approx \tau$$
$$\phi \circ \phi^{-1}(h) \approx h$$

**Implementation**:
The implementation ensures bidirectional consistency through careful design of the mappings.

```python
# Converting from agent time to human time and back should be consistent
agent_tp = temporal.create_timepoint(epoch=1, cycle=10, step=30)
human_time = temporal.to_human_time(agent_tp)
agent_tp_round_trip = temporal.from_human_time(human_time)
# agent_tp and agent_tp_round_trip should be approximately equal
```

### Property 2: Normalization Preservation

The agent-human morphism $\phi$ preserves normalization, meaning that if $\tau$ is in canonical form, $\phi(\tau)$ will also have a well-defined representation in the target universe.

**Implementation**:
The `to_human_time` method normalizes the input timepoint before mapping.

```python
def to_human_time(self, agent_tp):
    # Normalize first
    agent_tp = self.normalize(agent_tp)
    # ...
```

### Property 3: Unit Correspondence

The agent-human and human-agent morphisms establish a correspondence between specific time units in the agent and human temporal universes.

**Implementation**:
The mapping dictionaries define the unit correspondence.

```python
known_map = {
    "step": "seconds",
    "cycle": "minutes",
    "epoch": "hours"
}
```

## Theorems

### Theorem 1: Ordering Preservation

The agent-human morphism $\phi$ and human-agent morphism $\phi^{-1}$ preserve ordering:

$$\tau_1 < \tau_2 \implies \phi(\tau_1) < \phi(\tau_2)$$
$$h_1 < h_2 \implies \phi^{-1}(h_1) < \phi^{-1}(h_2)$$

**Proof**:
The morphisms map corresponding units with the same values, which maintains the ordering relationship between timepoints.

**Implementation**:
The implementation of the morphisms ensures that ordering is preserved by mapping corresponding units directly.

### Theorem 2: Approximate Duration Preservation

For timepoints $\tau_1$ and $\tau_2$, the duration between them is approximately preserved:

$$|\phi(\tau_2) - \phi(\tau_1)| \approx \phi(|\tau_2 - \tau_1|)$$

**Proof**:
The morphisms map corresponding units with the same values, which approximately preserves the duration between timepoints. However, exact preservation may not be guaranteed due to differences in the structure of the human and agent temporal universes.

**Implementation**:
The implementation of the morphisms ensures that durations are approximately preserved by mapping corresponding units.

### Theorem 3: Partial Invertibility

For timepoints where all relevant units are mapped, the agent-human and human-agent morphisms are approximately invertible:

$$\phi^{-1}(\phi(\tau)) \approx \tau$$

**Proof**:
For units that have direct mappings in both directions, the composition of the morphisms will preserve the values. However, for units without direct mappings, information may be lost in the conversion process.

**Implementation**:
The implementation ensures approximate invertibility for mapped units.

```python
# Example of approximate invertibility
agent_tp = temporal.create_timepoint(epoch=1, cycle=10, step=30)
human_time = temporal.to_human_time(agent_tp)
agent_tp_round_trip = temporal.from_human_time(human_time)

# For mapped units, the values should be the same
assert agent_tp["epoch"] == agent_tp_round_trip["epoch"]
assert agent_tp["cycle"] == agent_tp_round_trip["cycle"]
assert agent_tp["step"] == agent_tp_round_trip["step"]
```

## Applications

### Human-Readable Time Representation

Morphisms allow agent systems to express time in human-readable formats, which is essential for user interfaces and reporting.

**Example**:

```python
# Convert agent time to human-readable format
agent_time = temporal.create_timepoint(epoch=1, cycle=30, step=45)
human_time = temporal.to_human_time(agent_time)
print(f"The current time is {human_time['hours']} hours, {human_time['minutes']} minutes, and {human_time['seconds']} seconds")
```

### Cross-System Time Coordination

Morphisms enable coordination between agent systems and human-operated systems by providing a common temporal reference.

**Example**:

```python
# Human system provides a deadline in human terms
human_deadline = {"hours": 2, "minutes": 30, "seconds": 0}

# Convert to agent time for scheduling
agent_deadline = temporal.from_human_time(human_deadline)

# Use agent time for internal scheduling
scheduler.add_task("Task", {"step": 100}, deadline=agent_deadline)
```

### Time Unit Translation

Morphisms allow for translation between different time unit systems, which is useful in multi-agent environments or when interfacing with external systems.

**Example**:

```python
# Define a mapping between two agent systems
def translate_time(source_temporal, target_temporal, source_tp):
    # Convert to human time as an intermediate representation
    human_time = source_temporal.to_human_time(source_tp)
    # Convert from human time to the target system
    target_tp = target_temporal.from_human_time(human_time)
    return target_tp
```

## Relationship to Other Concepts

### Temporal Universe

Morphisms operate between temporal universes. See [Temporal Universe](temporal_universe.md) for more details.

### Hierarchical Partition

The structure of hierarchical partitions in each temporal universe affects how morphisms map between them. See [Hierarchical Partition](hierarchical_partition.md) for more details.

### Timepoint Operations

Morphisms should ideally preserve timepoint operations such as addition and comparison. See [Timepoint Operations](timepoint_operations.md) for more details.

## Implementation Notes

The implementation of morphisms in the `AgentTemporal` class focuses on practicality and ease of use:

1. **Simple Mapping**: A direct mapping between corresponding units is used for simplicity.

2. **Normalization**: Input timepoints are normalized before mapping to ensure consistency.

3. **Partial Mapping**: Not all units need to have corresponding mappings; the implementation handles partial mappings gracefully.

4. **Extensibility**: The mapping dictionaries can be customized to support different human time representations.

5. **Bidirectional Support**: Both directions of mapping are supported through separate methods.

The current implementation provides a simple and effective approach to mapping between agent and human time. For more complex scenarios, custom morphisms can be implemented by extending the base functionality.

```python
# Example of customizing the morphisms
class CustomAgentTemporal(AgentTemporal):
    def to_human_time(self, agent_tp):
        custom_map = {
            "step": "milliseconds",
            "cycle": "seconds",
            "epoch": "minutes"
        }
        # ... implementation similar to base method

    def from_human_time(self, human_dict):
        custom_map = {
            "milliseconds": "step",
            "seconds": "cycle",
            "minutes": "epoch"
        }
        # ... implementation similar to base method
```

## References

1. **Mathematical Time Structures for Agent Systems**: Section 5: Time Morphisms
2. **Category Theory**: Morphisms between structured sets
3. **Temporal Logic in Computer Science**: Mappings between temporal domains
