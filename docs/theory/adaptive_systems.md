# Adaptive Systems

## Overview

Adaptive systems in the Timekeeper framework allow for dynamic adjustment of temporal structures based on observed usage patterns. This document provides the formal definitions, properties, and theorems related to adaptive temporal systems and connects them to their implementation in the code.

## Definitions

### Definition 1: Adaptive Temporal Universe

An Adaptive Temporal Universe $\mathcal{T}_A$ extends a Temporal Universe $\mathcal{T}$ with an adaptation mechanism that can modify the subdivision factors $\{k_1, k_2, \ldots, k_n\}$ based on usage patterns.

**Implementation**:
The `AdaptiveAgentTemporal` class implements this concept by extending the `AgentTemporal` class.

```python
class AdaptiveAgentTemporal(AgentTemporal):
    """
    Extension of AgentTemporal that implements dynamic adaptability as described
    in Section 5 of the paper, in particular:

    - Adaptive Subdivision Function Γ(O, A) (Definition 21)
    - Partition Reconfiguration (Axiom 4)
    - Optimal Temporal Granularity (Property 1)
    """
```

### Definition 2: Operation Profile

An operation profile $O$ is a mapping from operations to frequency counts, which captures the pattern of usage of different temporal operations and units.

**Implementation**:
The `operations` dictionary in `AdaptiveAgentTemporal` tracks operation counts.

```python
def __init__(self, unit_config=None, agent_count=1):
    """Initialize the adaptive temporal system."""
    super().__init__(unit_config)

    # Track the number of agents
    self.agent_count = agent_count

    # Operation tracking for adaptation
    self.operations = defaultdict(int)
    self.op_counter = 0
    self.adaptation_threshold = 100  # Adjust after 100 operations
```

### Definition 3: Adaptive Subdivision Function

The adaptive subdivision function $\Gamma(O, A)$ maps an operation profile $O$ and agent count $A$ to a set of subdivision factors that optimize the temporal structure for the given usage pattern.

**Implementation**:
The `_check_for_adjustment` method implements this function by analyzing operation patterns and determining appropriate subdivision factors.

```python
def _check_for_adjustment(self):
    """
    Analyze operation patterns and potentially adjust subdivision factors.

    This implements Γ(O, A) from Definition 21.
    """
    # Build a usage profile for each unit
    unit_usage = defaultdict(int)
    for op_key, count in self.operations.items():
        if ":" in op_key:
            _, unit = op_key.split(":")
            unit_usage[unit] += count

    # Determine if any unit is over/under utilized
    total_ops = sum(unit_usage.values()) or 1  # Avoid division by zero

    # Check each unit for potential adjustment
    adjustments = []

    for i, unit in enumerate(self.units[:-1]):  # Skip base unit
        unit_name = unit["name"]
        usage_pct = unit_usage.get(unit_name, 0) / total_ops

        # Skip units with very low usage
        if usage_pct < 0.05:
            continue

        # Get current subdivision
        current_subdiv = unit["subdivisions"]
        # Get optimal range
        min_val, max_val = self.optimal_ranges[i]

        # If outside optimal range, plan an adjustment
        if current_subdiv < min_val:
            adjustments.append((i, min_val))
        elif current_subdiv > max_val:
            adjustments.append((i, max_val))
        else:
            # If within range but usage is very high, consider adjustment
            if usage_pct > 0.3:  # Over 30% of operations use this unit
                if current_subdiv < max_val:
                    # Increase subdivision for high-usage units
                    new_val = min(current_subdiv * 1.5, max_val)
                    adjustments.append((i, int(new_val)))
            elif usage_pct < 0.1:  # Under 10% usage
                if current_subdiv > min_val:
                    # Decrease subdivision for low-usage units
                    new_val = max(current_subdiv * 0.7, min_val)
                    adjustments.append((i, int(new_val)))
```

### Definition 4: Partition Reconfiguration

Partition reconfiguration is the process of modifying the structure of a temporal universe by changing subdivision factors, adding new partitions, or removing existing partitions.

**Implementation**:
The `adjust_subdivision`, `add_time_unit`, and `remove_time_unit` methods implement different types of partition reconfiguration.

```python
def adjust_subdivision(self, unit_name, new_subdiv):
    """
    Adjust the subdivision factor for a specific unit.

    This implements part of the Partition Reconfiguration axiom.
    """
    if unit_name not in self.unit_indices:
        raise ValueError(f"Unknown unit: {unit_name}")

    idx = self.unit_indices[unit_name]

    # Cannot adjust the base unit's subdivision
    if idx == self.base_unit_index:
        raise ValueError("Cannot adjust subdivision factor of the base unit")

    # Replace the subdivision factor
    self.units[idx]["subdivisions"] = new_subdiv

    # Recompute conversion factors
    self._compute_conversions()

def add_time_unit(self, name, subdivisions, after_unit=None, before_unit=None):
    """
    Add a new time unit to the hierarchy.

    This implements the Refinement operation from the Partition Reconfiguration axiom.
    """
    # Implementation details...

def remove_time_unit(self, unit_name):
    """
    Remove a time unit from the hierarchy.

    This implements the Coarsening operation from the Partition Reconfiguration axiom.
    """
    # Implementation details...
```

### Definition 5: Optimal Temporal Granularity

Optimal temporal granularity is a property that defines ranges of appropriate subdivision factors based on the number of agents and the position of units in the hierarchy.

**Implementation**:
The `_initialize_optimal_ranges` method defines optimal subdivision ranges for different levels of the hierarchy.

```python
def _initialize_optimal_ranges(self):
    """
    Initialize optimal subdivision ranges based on agent count.

    As per Property 1 in the paper:
    - 10 ≤ k_i ≤ 100 for finer units (lower index)
    - 5 ≤ k_i ≤ 24 for intermediate units
    - A ≤ k_i ≤ 5A for coarser units (higher index)
    """
    n = len(self.units)
    self.optimal_ranges = []

    # Set optimal ranges based on unit position in hierarchy
    for i in range(n):
        if i < n/3:  # Coarser units (first third)
            self.optimal_ranges.append((self.agent_count, 5 * self.agent_count))
        elif i < 2*n/3:  # Intermediate units (middle third)
            self.optimal_ranges.append((5, 24))
        else:  # Finer units (last third)
            self.optimal_ranges.append((10, 100))
```

## Properties

### Property 1: Adaptation Convergence

Under consistent usage patterns, an adaptive temporal system will eventually converge to a stable configuration where subdivision factors remain within optimal ranges.

**Implementation**:
The adaptation logic in `_check_for_adjustment` ensures that subdivision factors move toward optimal ranges over time.

```python
# From _check_for_adjustment method
# If outside optimal range, plan an adjustment
if current_subdiv < min_val:
    adjustments.append((i, min_val))
elif current_subdiv > max_val:
    adjustments.append((i, max_val))
```

### Property 2: Usage-Based Optimization

Units that are used more frequently tend to have finer subdivision, while units that are used less frequently tend to have coarser subdivision.

**Implementation**:
The adaptation logic adjusts subdivision factors based on usage frequency.

```python
# From _check_for_adjustment method
# If within range but usage is very high, consider adjustment
if usage_pct > 0.3:  # Over 30% of operations use this unit
    if current_subdiv < max_val:
        # Increase subdivision for high-usage units
        new_val = min(current_subdiv * 1.5, max_val)
        adjustments.append((i, int(new_val)))
elif usage_pct < 0.1:  # Under 10% usage
    if current_subdiv > min_val:
        # Decrease subdivision for low-usage units
        new_val = max(current_subdiv * 0.7, min_val)
        adjustments.append((i, int(new_val)))
```

### Property 3: Agent-Based Scaling

The optimal subdivision factors for coarser units scale with the number of agents in the system, reflecting the increased complexity of multi-agent coordination.

**Implementation**:
The `_initialize_optimal_ranges` method scales optimal ranges based on agent count.

```python
# From _initialize_optimal_ranges method
if i < n/3:  # Coarser units (first third)
    self.optimal_ranges.append((self.agent_count, 5 * self.agent_count))
```

### Property 4: Adaptation Threshold

Adaptation occurs after a sufficient number of operations have been observed, ensuring that changes are based on meaningful patterns rather than transient fluctuations.

**Implementation**:
The `track_operation` method counts operations until an adaptation threshold is reached.

```python
def track_operation(self, op_type, unit_name=None):
    """Track operations to inform adaptive behavior."""
    self.operations[op_type] += 1
    if unit_name:
        self.operations[f"{op_type}:{unit_name}"] += 1

    self.op_counter += 1

    # Check if we should adjust parameters
    if self.op_counter >= self.adaptation_threshold:
        self._check_for_adjustment()

        # Reset counter but keep history
        self.op_counter = 0
```

## Theorems

### Theorem 1: Temporal Consistency Under Adaptation

Time operations (addition, subtraction, comparison) remain consistent before and after adaptation, though the specific representation may change.

**Proof**:
The adaptation process modifies the subdivision factors but maintains the absolute representation in base units. Operations that rely on base unit conversion will produce the same results before and after adaptation.

**Implementation**:
The implementation ensures consistency by recomputing conversion factors after each adaptation.

```python
def adjust_subdivision(self, unit_name, new_subdiv):
    # ...
    # Recompute conversion factors
    self._compute_conversions()
```

### Theorem 2: Adaptability-Efficiency Tradeoff

Adaptive temporal systems achieve better efficiency in time representation at the cost of additional computational overhead for tracking and adaptation.

**Proof**:
The adaptive system requires additional computation for tracking operations and periodically checking for adjustments, but this overhead is justified by the improved efficiency in time representation, especially for frequently used operations.

**Implementation**:
The `track_operation` method adds overhead to each operation, but the benefits in time representation can outweigh this cost.

### Theorem 3: Structural Preservation

Adding or removing time units preserves the fundamental properties of the temporal universe, such as the ability to represent and compare timepoints.

**Proof**:
The implementation ensures that the hierarchical structure is maintained when adding or removing units, and all necessary conversion factors are updated.

**Implementation**:
The `add_time_unit` and `remove_time_unit` methods carefully update the unit indices and base unit index to maintain structural integrity.

```python
def add_time_unit(self, name, subdivisions, after_unit=None, before_unit=None):
    # ...
    # Update base unit index if needed
    if position <= self.base_unit_index:
        self.base_unit_index += 1

    # Rebuild unit indices mapping
    self.unit_indices = {u["name"]: i for i, u in enumerate(self.units)}

    # Recompute conversion factors
    self._compute_conversions()
```

## Applications

### Multi-Agent Time Coordination

Adaptive temporal systems are particularly valuable in multi-agent environments, where the appropriate granularity of time can depend on the number of agents and their coordination patterns.

**Example**:

```python
# Create an adaptive temporal system with 3 agents
adaptive = AdaptiveAgentTemporal(agent_count=3)

# As agents interact, the system adapts to their usage patterns
for _ in range(100):
    # Agents perform operations
    adaptive.add_time(some_timepoint, cycle=5)
    adaptive.track_operation("add", "cycle")

# If the number of agents changes, the system can adapt
adaptive.optimize_for_agent_count(5)
```

### Usage-Optimized Time Representation

The adaptive system can optimize time representation based on the actual usage patterns of an application, rather than requiring a fixed structure that might be inefficient for specific use cases.

**Example**:

```python
# Create an adaptive system with default configuration
adaptive = AdaptiveAgentTemporal()

# Simulate a pattern of usage focused on fine-grained operations
for _ in range(200):
    tp = adaptive.create_timepoint(step=10)
    adaptive.add_time(tp, step=5)
    adaptive.track_operation("add", "step")

# The system will adapt to increase subdivision for step units
# and possibly decrease subdivision for less-used units
```

### Time Representation Evolution

As an application evolves over time, its temporal needs may change. Adaptive systems can evolve with the application without requiring manual reconfiguration.

**Example**:

```python
# Start with a simple temporal structure
adaptive = AdaptiveAgentTemporal([
    {"name": "task", "subdivisions": 10},
    {"name": "subtask", "subdivisions": None, "is_base": True}
])

# As the application becomes more complex, add new time units
adaptive.add_time_unit("project", 5, before_unit="task")

# And let the system adapt the subdivision factors based on usage
# ...
```

## Relationship to Other Concepts

### Temporal Universe

Adaptive systems extend the concept of a Temporal Universe with dynamic adaptation capabilities. See [Temporal Universe](temporal_universe.md) for more details.

### Hierarchical Partition

The adaptation process modifies the structure of the hierarchical partition. See [Hierarchical Partition](hierarchical_partition.md) for more details.

### Task Scheduling

Adaptive temporal systems can improve task scheduling efficiency by optimizing the temporal structure for the specific scheduling patterns of an application. The `TaskScheduler` class can work with adaptive temporal systems without modification.

## Implementation Notes

The implementation of adaptive systems in the `AdaptiveAgentTemporal` class focuses on practical adaptability while maintaining the mathematical foundations of the Timekeeper framework:

1. **Operation Tracking**: Operations are tracked with their associated time units to build a usage profile.

2. **Threshold-Based Adaptation**: Adaptation occurs after a threshold number of operations, balancing responsiveness with stability.

3. **Optimal Ranges**: Optimal subdivision ranges are defined based on empirical considerations and theoretical principles.

4. **Agent-Based Scaling**: The optimal ranges for coarser units scale with the number of agents in the system.

5. **Structural Flexibility**: The implementation supports adding and removing time units, allowing for more radical restructuring when needed.

The adaptation logic is designed to be conservative, making incremental adjustments rather than dramatic changes, which helps maintain temporal consistency while gradually optimizing the structure.

```python
# Example of incremental adjustment logic
new_val = min(current_subdiv * 1.5, max_val)  # Increase by at most 50%
new_val = max(current_subdiv * 0.7, min_val)  # Decrease by at most 30%
```

## References

1. **Mathematical Time Structures for Agent Systems**: Section 7: Adaptive Temporal Systems
2. **Dynamic Data Structures**: Adaptation mechanisms in computer science
3. **Multi-Agent Coordination**: Temporal requirements in multi-agent systems
