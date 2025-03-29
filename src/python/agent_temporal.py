"""
Implementation of the AgentTemporal framework core components.

This module directly implements the mathematical constructs described in
the theoretical framework, including temporal universe, hierarchical partitions,
timepoints, and operations on them.
"""


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
        # If no custom configuration is passed, define a standard hierarchy
        # from coarsest to finest or vice versa. (Equivalent to {Pi_0, ..., Pi_n})
        self.default_config = [
            # Pi_0: coarsest partition
            {"name": "epoch", "subdivisions": 24},  # e.g., 1 epoch -> 24 cycles
            # Pi_1:
            {"name": "cycle", "subdivisions": 60},  # 1 cycle -> 60 steps
            # Pi_2:
            {"name": "step", "subdivisions": 1000},  # 1 step -> 1000 microsteps
            # Pi_3: finest partition
            {"name": "microstep", "subdivisions": None, "is_base": True},
        ]
        # If user gave a config, use it; otherwise use default
        self.units = unit_config if unit_config else self.default_config

        # The base unit is the "finest" partition Pi_n
        # We'll find which index has is_base == True:
        self.base_unit_index = next(
            i for i, u in enumerate(self.units) if u.get("is_base", False)
        )

        # Build a quick mapping from a unit name to its index
        self.unit_indices = {u["name"]: i for i, u in enumerate(self.units)}

        # Precompute conversion factors among all units for quick add/sub
        self.conversion_factors = {}
        self._compute_conversions()

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
        # Step 1: define how to convert each unit to the base unit
        # e.g., if base unit is microstep, we figure out how many microsteps in one step, cycle, epoch, etc.
        to_base = [1.0] * len(self.units)

        # Going from the 'finest' index up to coarser indices:
        # We'll multiply subdivisions as we go up the chain from base to coarser.

        # If base_unit_index is the last in the list, we proceed backward, etc.
        # We'll unify the approach by always going from coarsest to finest in code:
        # but actually we can do it from the base up:

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
        # Initialize with 0 for all units
        tp = {u["name"]: 0 for u in self.units}
        # Fill any user-provided values
        for k, v in kwargs.items():
            if k not in tp:
                raise ValueError(f"Unknown unit '{k}' in create_timepoint(...)")
            tp[k] = v
        # We'll let normalizing or user calls handle out-of-range values, if any
        return self.normalize(tp)

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
        # Convert to the base unit measure
        total_base = self.to_base_units(timepoint)
        # Convert back from base to hierarchical
        return self.from_base_units(total_base)

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
        total = 0
        for unit_name, amount in timepoint.items():
            factor = self.conversion_factors[
                (unit_name, self.units[self.base_unit_index]["name"])
            ]
            total += amount * factor
        return total

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
        # We proceed from the coarsest to the base.
        # We'll produce integer "digits" in each partition's base.
        # That is the direct analog of the canonical form described in the paper.
        result = {}
        remainder = base_value
        for i, u in enumerate(self.units):
            # If i is not the last index, we see how many of that unit fit in remainder
            # using the factor from that unit to the base.
            conv = self.conversion_factors[
                (u["name"], self.units[self.base_unit_index]["name"])
            ]
            # conv = how many base units is 1 of u
            if conv != 0:
                # integer portion of remainder / conv
                count = int(remainder // conv)
                result[u["name"]] = count
                # subtract that from remainder
                remainder -= count * conv
            else:
                result[u["name"]] = 0
        return result

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
        base_main = self.to_base_units(tp)
        # Build an additive timepoint from kwargs, e.g. step=5
        addition_tp = self.create_timepoint(**kwargs)
        base_add = self.to_base_units(addition_tp)
        summed = base_main + base_add
        return self.from_base_units(summed)

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
        base_main = self.to_base_units(tp)
        sub_tp = self.create_timepoint(**kwargs)
        base_sub = self.to_base_units(sub_tp)
        if base_sub > base_main:
            raise ValueError("Subtraction would produce a negative time result.")
        result = base_main - base_sub
        return self.from_base_units(result)

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
        b1 = self.to_base_units(t1)
        b2 = self.to_base_units(t2)
        if b1 < b2:
            return -1
        elif b1 > b2:
            return 1
        else:
            return 0

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
        b1 = self.to_base_units(t1)
        b2 = self.to_base_units(t2)
        diff = abs(b2 - b1)
        return self.from_base_units(diff)

    # The paper also references mapping to 'human time' (Definitions 16-19).
    # We'll do a simple version here:

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
        # Example: you can define your own mapping. For demonstration:
        known_map = {"seconds": "step", "minutes": "cycle", "hours": "epoch"}
        agent_tp = {u["name"]: 0 for u in self.units}
        for h_key, val in human_dict.items():
            if h_key not in known_map:
                raise ValueError(f"Human unit {h_key} not recognized.")
            agent_unit = known_map[h_key]
            agent_tp[agent_unit] = val
        return self.normalize(agent_tp)

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
        known_map = {
            "step": "seconds",
            "cycle": "minutes",
            "epoch": "hours",
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
