# LaTeX Style Guide for Timekeeper Documentation

## Overview

This document provides guidelines for using LaTeX notation consistently across all Timekeeper documentation. Following these standards ensures that mathematical concepts are presented uniformly across theory documentation, implementation docstrings, and examples.

## LaTeX in Python Docstrings

### Basic Setup

Sphinx with the `sphinx.ext.mathjax` extension can interpret LaTeX in docstrings. In NumPy-style docstrings, LaTeX can be used as follows:

```python
def function_name(param1, param2):
    """
    Function description with LaTeX math such as $f(x) = x^2$.

    Mathematical content can also be set in display mode:

    \\begin{align}
    f(x) &= x^2 \\\\
    g(x) &= \\frac{1}{x}
    \\end{align}

    Parameters
    ----------
    param1 : type
        Description that can include $\\alpha$ math notation.
    param2 : type
        Description.

    Returns
    -------
    type
        Description with math like $\\beta = \\alpha^2$.

    See Also
    --------
    other_function : Other related function
    docs/theory/reference.md : Reference to theory documentation
    """
```

### LaTeX Delimiters

- **Inline Math**: Use single dollar signs (`$...$`) for inline mathematical expressions
- **Display Math**: Use `\\begin{align}...\\end{align}` for multi-line equations with alignment
- **Single Equation Display**: Use `\\begin{equation}...\\end{equation}` for centered display equations
- **No Numbering**: Use the starred variants (`align*`, `equation*`) when equation numbering is not needed

## Standard Mathematical Notation

### Temporal Concepts

| Concept                | LaTeX Notation    | Example                                                   |
| ---------------------- | ----------------- | --------------------------------------------------------- |
| Timepoint              | $t$ or $t_i$      | $t = (u_1, u_2, \ldots, u_n)$                             |
| Temporal Universe      | $T$               | $T = \{(u_1, u_2, \ldots, u_n) \mid u_i \in \mathbb{N}\}$ |
| Hierarchical Partition | $H$               | $H = (U, S)$                                              |
| Unit Vector            | $\vec{u}$         | $\vec{u} = (u_1, u_2, \ldots, u_n)$                       |
| Subdivision Vector     | $\vec{s}$         | $\vec{s} = (s_1, s_2, \ldots, s_{n-1})$                   |
| Normalization Function | $N(t)$            | $N(t) = (u_1 \bmod s_1, u_2 \bmod s_2, \ldots)$           |
| Addition               | $t_1 \oplus t_2$  | $t_1 \oplus t_2 = N(t_1 + t_2)$                           |
| Subtraction            | $t_1 \ominus t_2$ | $t_1 \ominus t_2 = N(t_1 - t_2)$                          |
| Base Unit Conversion   | $B(t)$            | $B(t) = \sum_{i=1}^{n} u_i \cdot \prod_{j=i+1}^{n} s_j$   |
| Human-Agent Mapping    | $\phi(t)$         | $\phi: T_\text{agent} \rightarrow T_\text{human}$         |

### Scheduling Concepts

| Concept      | LaTeX Notation     | Example                                        |
| ------------ | ------------------ | ---------------------------------------------- |
| Task         | $\tau$ or $\tau_i$ | $\tau = (id, name, t, d, deps)$                |
| Duration     | $d$ or $d_i$       | $d = (d_1, d_2, \ldots, d_n)$                  |
| Dependencies | $deps$             | $deps = \{\tau_i, \tau_j, \ldots\}$            |
| Schedule     | $S$                | $S = \{\tau_1, \tau_2, \ldots, \tau_m\}$       |
| Start Time   | $t^\text{start}$   | $t^\text{start}_i$                             |
| End Time     | $t^\text{end}$     | $t^\text{end}_i = t^\text{start}_i \oplus d_i$ |

### Adaptive Concepts

| Concept             | LaTeX Notation | Example                            |
| ------------------- | -------------- | ---------------------------------- |
| Adaptation Function | $A(T, f)$      | $A(T, f) = T'$                     |
| Adaptation Factor   | $f$            | $f \in \mathbb{R}^+$               |
| Agent Index         | $a$ or $a_i$   | $a \in \{0, 1, \ldots, n-1\}$      |
| Agent-Specific Time | $t^a$          | $t^a = (u_1, u_2, \ldots, u_n, a)$ |
| Workload            | $W$ or $W_a$   | $W_a = \sum_{\tau \in S_a} d_\tau$ |

## LaTeX Packages and Commands

The following LaTeX packages and commands are used throughout the documentation:

### Basic Math Commands

```latex
\mathbb{N}      % Natural numbers
\mathbb{Z}      % Integers
\mathbb{R}      % Real numbers
\mathbb{R}^+    % Positive real numbers

\rightarrow    % Function mapping
\mapsto        % Variable mapping

\oplus         % Temporal addition
\ominus        % Temporal subtraction
\otimes        % Temporal multiplication (if needed)

\mid           % Such that in set definitions
\forall        % For all
\exists        % There exists
```

### Matrix and Vector Notation

```latex
\vec{u}        % Vector u
\vec{s}        % Vector s

\begin{pmatrix} % Matrix
a & b \\
c & d
\end{pmatrix}
```

### Text in Math Mode

```latex
\text{agent}   % Text within math mode
```

## Integration with Theory Documentation

When referencing mathematical concepts defined in the theory documentation, use consistent notation and explicitly reference the source document:

```python
"""
This implements the normalization function $N: T \rightarrow T$ defined in the
Temporal Universe theory (see docs/theory/temporal_universe.md), where:

\begin{align}
N(t) = (u_1 \bmod s_1, u_2 \bmod s_2, \ldots, u_{n-1} \bmod s_{n-1}, u_n)
\end{align}

where $s_i$ is the number of subdivisions for unit $i$.
"""
```

## LaTeX in Sphinx Documentation

When writing RST files for Sphinx documentation, LaTeX can be included using the same syntax as in docstrings:

```rst
The temporal universe :math:`T` is defined as...

.. math::

   T = \{(u_1, u_2, \ldots, u_n) \mid u_i \in \mathbb{N}\}
```

## LaTeX in Quarto

When writing Quarto documentation, use standard LaTeX delimiters:

```markdown
The temporal universe $T$ is defined as...

$$
T = \{(u_1, u_2, \ldots, u_n) \mid u_i \in \mathbb{N}\}
$$
```

## Test Rendering

Before finalizing the documentation:

1. Build the Sphinx documentation to verify LaTeX formatting:

   ```
   cd config/sphinx
   make html
   ```

2. Render the Quarto documentation:

   ```
   quarto render
   ```

3. Check for rendering issues or inconsistencies between the two systems.

## Common Issues and Solutions

### Escaping Backslashes

In Python strings, backslashes must be escaped:

```python
# Incorrect
"""
\begin{align}
f(x) = x^2
\end{align}
"""

# Correct
"""
\\begin{align}
f(x) = x^2
\\end{align}
"""
```

### Line Breaks in Align Environment

In Python docstrings, double backslash for line breaks needs four backslashes:

```python
"""
\\begin{align}
f(x) &= x^2 \\\\
g(x) &= \\frac{1}{x}
\\end{align}
"""
```

### Math Mode Spacing

Use `\,` for thin spaces, `\;` for medium spaces, and `\quad` or `\qquad` for larger spaces:

```latex
f(x) \, g(x)    % Thin space
f(x) \; g(x)    % Medium space
f(x) \quad g(x) % Larger space
```

## LaTeX Checking Tools

Consider using these tools to help check LaTeX consistency:

1. **latexdiff**: For comparing LaTeX documents and highlighting differences
2. **ChkTeX**: For checking LaTeX for common mistakes
3. **LaTeX-Workshop VSCode extension**: For previewing LaTeX in VSCode

## Recommended Implementation Process

1. Start with the core mathematical definitions in theory documentation
2. Copy the exact LaTeX expressions to docstrings with proper escaping
3. Add cross-references to ensure traceability
4. Build documentation to verify rendering
5. Check consistency across all components
