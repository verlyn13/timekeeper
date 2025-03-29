# Docstring Enhancement Guide

## Overview

This document provides guidelines for enhancing docstrings in the Timekeeper framework to better connect implementation to mathematical theory. The goal is to create a bidirectional traceability between code and mathematical concepts.

## Key Principles

1. **Mathematical Rigor**: All docstrings should include the precise mathematical definitions using LaTeX.
2. **Cross-Referencing**: Docstrings should reference relevant theory documentation.
3. **Complete Coverage**: All classes, methods, and functions should have enhanced docstrings.
4. **Consistency**: Format and style should be consistent across all docstrings.

## Template Structure

Each class docstring should follow this structure:

```python
class ExampleClass:
    """
    Short description of the class.

    Mathematical Foundation:
    -----------------------
    This class implements the mathematical concept of X, defined as:

    \[ X = \{x \in U \mid P(x)\} \]

    where $U$ is the universal set and $P(x)$ is a property that elements of $X$ satisfy.

    Key Mathematical Properties:
    --------------------------
    1. Property A: $\forall x,y \in X: x \oplus y \in X$
    2. Property B: $\forall x \in X: x \odot x = x$

    References:
    ----------
    - See [TemporalUniverse](/docs/theory/temporal_universe.md) for the complete theoretical foundation.
    - Definition 3.2 in the Timekeeper Mathematical Framework.

    Examples:
    --------
    >>> example = ExampleClass()
    >>> result = example.method()
    """
```

Method docstrings should follow this structure:

```python
def example_method(self, arg1, arg2):
    """
    Short description of the method.

    Mathematical Definition:
    ----------------------
    This method implements the operation $\otimes: X \times Y \rightarrow Z$ defined as:

    \[ x \otimes y = \{x_i \cdot y_i \mid x_i \in x, y_i \in y\} \]

    Parameters:
    ----------
    arg1 : type
        Description of arg1. Corresponds to $x$ in the definition.
    arg2 : type
        Description of arg2. Corresponds to $y$ in the definition.

    Returns:
    -------
    return_type
        Description of the return value. Corresponds to $x \otimes y$ in the definition.

    Raises:
    ------
    ExceptionType
        When the operation is invalid (e.g., when $x \notin X$).

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md) for details.
    - Theorem 4.1 in the Timekeeper Mathematical Framework.

    Examples:
    --------
    >>> result = obj.example_method(arg1, arg2)
    """
```

## Specific Enhancement Examples

### Example 1: AgentTemporal Class

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
    This class implements the Temporal Universe (𝒯) and associated structures:

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

### Example 2: add_time Method

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
    Performs temporal addition of two timepoints.

    Mathematical Definition:
    ----------------------
    This method implements the temporal addition operation $\tau \oplus \tau'$ defined as:

    \[ \tau \oplus \tau' = \mathcal{N}(\tau + \tau') \]

    where:
    - $\tau$ and $\tau'$ are timepoints
    - $\mathcal{N}$ is the normalization function that converts to canonical form
    - Addition is first performed by converting to base units, summing, then converting back

    The operation satisfies these properties:
    1. Associativity: $(\tau_1 \oplus \tau_2) \oplus \tau_3 = \tau_1 \oplus (\tau_2 \oplus \tau_3)$
    2. Commutativity: $\tau_1 \oplus \tau_2 = \tau_2 \oplus \tau_1$
    3. Identity: $\tau \oplus \mathbf{0} = \tau$ where $\mathbf{0}$ is the zero timepoint

    Parameters:
    ----------
    tp : dict
        The timepoint to which time will be added. Dictionary mapping unit names to values.
    **kwargs : dict
        Time units to add, specified as keyword arguments (e.g., cycle=5, step=10).

    Returns:
    -------
    dict
        A new timepoint resulting from the addition, in canonical form.

    References:
    ----------
    - See [Timepoint Operations](/docs/theory/timepoint_operations.md#temporal-addition) for details.
    - Axiom 1 (Temporal Addition) in the Timekeeper Mathematical Framework.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> t1 = temporal.create_timepoint(epoch=1, cycle=10, step=30)
    >>> t2 = temporal.add_time(t1, cycle=5, step=50)
    >>> print(t2)
    {'epoch': 1, 'cycle': 15, 'step': 80, 'microstep': 0}
    """
```

## Implementation Guidelines

1. **Start with Core Classes**: Begin with the core classes (AgentTemporal, TaskScheduler, AdaptiveAgentTemporal) as they form the foundation.

2. **Markdown Links**: Use Markdown-style links to reference theory documentation files.

3. **LaTeX Format**:

   - Use `\[ ... \]` for standalone equations
   - Use `$...$` for inline math
   - Use `\begin{align} ... \end{align}` for multi-line equations

4. **Reference Format**: Include explicit references to:

   - Theory documentation files
   - Definition/Theorem numbers from the mathematical framework
   - Section numbers from the paper

5. **Validation**:
   - Ensure all LaTeX formulas are valid
   - Verify that all links to documentation files are correct
   - Check that all mathematical properties are accurately described

## Implementation Process

1. **Inventory**: Create an inventory of all classes, methods, and functions that need enhanced docstrings.

2. **Prioritize**: Start with the most important and most used components.

3. **Enhance**: Update docstrings according to the templates.

4. **Validate**: Verify LaTeX syntax and cross-references.

5. **Review**: Have docstrings reviewed for mathematical accuracy.

6. **Build**: Ensure Sphinx correctly processes the enhanced docstrings.

## Example Workflow

```python
# Before
def normalize(self, timepoint):
    """
    Canonical normalization (Definition 7). This ensures that for each unit i,
    the value is in [0, subdivisions_i), by carrying over to the coarser unit
    if necessary.
    """

# After
def normalize(self, timepoint):
    """
    Transforms a timepoint into its canonical form.

    Mathematical Definition:
    ----------------------
    This method implements the normalization function $\mathcal{N}$ from Definition 7:

    \[ \mathcal{N}(\tau) = (b_0, b_1, \ldots, b_{n-1}) \]

    where:
    - $\tau = (a_0, a_1, \ldots, a_{n-1})$ is the input timepoint
    - $b_i$ values satisfy $0 \leq b_i < k_{i+1}$ for all $0 \leq i < n-1$
    - The absolute value $|\tau|_{U_n} = |\mathcal{N}(\tau)|_{U_n}$

    The normalization process converts to base units and then rebuilds the
    hierarchical representation with values in the canonical ranges.

    Parameters:
    ----------
    timepoint : dict
        The timepoint to normalize. Dictionary mapping unit names to values.

    Returns:
    -------
    dict
        The normalized timepoint in canonical form.

    References:
    ----------
    - See [Hierarchical Partition](/docs/theory/hierarchical_partition.md#canonical-form) for details.
    - Definition 7 in the Timekeeper Mathematical Framework.

    Examples:
    --------
    >>> temporal = AgentTemporal()
    >>> non_canonical = {'epoch': 1, 'cycle': 70, 'step': 30, 'microstep': 0}
    >>> canonical = temporal.normalize(non_canonical)
    >>> print(canonical)
    {'epoch': 2, 'cycle': 10, 'step': 30, 'microstep': 0}
    """
```
