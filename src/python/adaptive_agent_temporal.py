"""
Implementation of the dynamic adaptability components of the AgentTemporal framework.

This module extends the core AgentTemporal class with adaptability features
that allow the system to adjust its temporal units based on observed usage patterns.
"""

from collections import defaultdict
from .agent_temporal import AgentTemporal

class AdaptiveAgentTemporal(AgentTemporal):
    """
    Extension of AgentTemporal that implements dynamic adaptability as described
    in Section 5 of the paper, in particular:
    
    - Adaptive Subdivision Function Γ(O, A) (Definition 21)
    - Partition Reconfiguration (Axiom 4)
    - Optimal Temporal Granularity (Property 1)
    """
    
    def __init__(self, unit_config=None, agent_count=1):
        """
        Initialize the adaptive temporal system.
        
        Args:
            unit_config: Optional custom configuration of time units
            agent_count: Number of agents in the system (default: 1)
        """
        super().__init__(unit_config)
        
        # Track the number of agents
        self.agent_count = agent_count
        
        # Operation tracking for adaptation
        self.operations = defaultdict(int)
        self.op_counter = 0
        self.adaptation_threshold = 100  # Adjust after 100 operations
        
        # Initialize optimal ranges based on agent count (Property 1)
        self._initialize_optimal_ranges()
    
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
    
    def track_operation(self, op_type, unit_name=None):
        """
        Track operations to inform adaptive behavior.
        
        Args:
            op_type: Type of operation ('add', 'subtract', 'compare', etc.)
            unit_name: Specific unit the operation primarily involves, if applicable
        """
        self.operations[op_type] += 1
        if unit_name:
            self.operations[f"{op_type}:{unit_name}"] += 1
            
        self.op_counter += 1
        
        # Check if we should adjust parameters
        if self.op_counter >= self.adaptation_threshold:
            self._check_for_adjustment()
            
            # Reset counter but keep history
            self.op_counter = 0
    
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
        
        # Apply adjustments
        for idx, new_subdiv in adjustments:
            unit_name = self.units[idx]["name"]
            print(f"Adjusting subdivision factor for {unit_name} from {self.units[idx]['subdivisions']} to {new_subdiv}")
            self.adjust_subdivision(unit_name, new_subdiv)
    
    def adjust_subdivision(self, unit_name, new_subdiv):
        """
        Adjust the subdivision factor for a specific unit.
        
        This implements part of the Partition Reconfiguration axiom.
        
        Args:
            unit_name: Name of the unit to adjust
            new_subdiv: New subdivision factor
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
        
        Args:
            name: Name of the new unit
            subdivisions: How many of the next finer unit it contains
            after_unit: Add after this unit (coarser side)
            before_unit: Add before this unit (finer side)
        """
        if name in self.unit_indices:
            raise ValueError(f"Unit {name} already exists")
            
        # Determine insertion position
        if after_unit is not None:
            if after_unit not in self.unit_indices:
                raise ValueError(f"Unknown unit: {after_unit}")
            position = self.unit_indices[after_unit] + 1
        elif before_unit is not None:
            if before_unit not in self.unit_indices:
                raise ValueError(f"Unknown unit: {before_unit}")
            position = self.unit_indices[before_unit]
        else:
            # Default to inserting before the base unit
            position = self.base_unit_index
        
        # Create the new unit
        new_unit = {"name": name, "subdivisions": subdivisions}
        
        # Insert the new unit
        self.units.insert(position, new_unit)
        
        # Update base unit index if needed
        if position <= self.base_unit_index:
            self.base_unit_index += 1
            
        # Rebuild unit indices mapping
        self.unit_indices = {u["name"]: i for i, u in enumerate(self.units)}
        
        # Recompute conversion factors
        self._compute_conversions()
        
        # Update optimal ranges
        self._initialize_optimal_ranges()
    
    def remove_time_unit(self, unit_name):
        """
        Remove a time unit from the hierarchy.
        
        This implements the Coarsening operation from the Partition Reconfiguration axiom.
        
        Args:
            unit_name: Name of the unit to remove
        """
        if unit_name not in self.unit_indices:
            raise ValueError(f"Unknown unit: {unit_name}")
            
        idx = self.unit_indices[unit_name]
        
        # Cannot remove the base unit
        if idx == self.base_unit_index:
            raise ValueError("Cannot remove the base unit")
            
        # Remove the unit
        self.units.pop(idx)
        
        # Update base unit index if needed
        if idx < self.base_unit_index:
            self.base_unit_index -= 1
            
        # Rebuild unit indices mapping
        self.unit_indices = {u["name"]: i for i, u in enumerate(self.units)}
        
        # Recompute conversion factors
        self._compute_conversions()
        
        # Update optimal ranges
        self._initialize_optimal_ranges()
    
    def optimize_for_agent_count(self, new_agent_count):
        """
        Optimize temporal structure for a specific number of agents.
        
        This implements the agent-specific optimality described in Property 1.
        
        Args:
            new_agent_count: New number of agents in the system
        """
        if new_agent_count < 1:
            raise ValueError("Agent count must be at least 1")
            
        # Update agent count
        self.agent_count = new_agent_count
        
        # Update optimal ranges
        self._initialize_optimal_ranges()
        
        # Adjust each unit's subdivision to match optimal ranges
        for i, unit in enumerate(self.units[:-1]):  # Skip base unit
            min_val, max_val = self.optimal_ranges[i]
            current_subdiv = unit["subdivisions"]
            
            # If outside range, adjust to nearest boundary
            if current_subdiv < min_val:
                self.adjust_subdivision(unit["name"], min_val)
            elif current_subdiv > max_val:
                self.adjust_subdivision(unit["name"], max_val)
    
    # Override core operations to track usage
    
    def add_time(self, tp, **kwargs):
        """Override to track operation"""
        result = super().add_time(tp, **kwargs)
        self.track_operation("add")
        return result
    
    def subtract_time(self, tp, **kwargs):
        """Override to track operation"""
        result = super().subtract_time(tp, **kwargs)
        self.track_operation("subtract")
        return result
    
    def compare_timepoints(self, t1, t2):
        """Override to track operation"""
        result = super().compare_timepoints(t1, t2)
        self.track_operation("compare")
        return result
    
    def to_human_time(self, agent_tp):
        """Override to track operation"""
        result = super().to_human_time(agent_tp)
        self.track_operation("to_human")
        return result
    
    def from_human_time(self, human_dict):
        """Override to track operation"""
        result = super().from_human_time(human_dict)
        self.track_operation("from_human")
        return result


"""
Example usage:

adaptive = AdaptiveAgentTemporal(agent_count=2)

# Create some timepoints
t1 = adaptive.create_timepoint(epoch=1, cycle=12, step=30)
t2 = adaptive.create_timepoint(cycle=10, step=45)

# Perform operations
for _ in range(50):
    adaptive.add_time(t1, cycle=5, step=25)
    adaptive.compare_timepoints(t1, t2)

# Add more agents and optimize
adaptive.optimize_for_agent_count(3)

# Add a new unit
adaptive.add_time_unit("megacycle", 10, after_unit="epoch")

# Print current structure
print("Current time unit hierarchy:")
for i, unit in enumerate(adaptive.units):
    if i < len(adaptive.units) - 1:  # Not the last unit
        subdiv = unit["subdivisions"]
        next_unit = adaptive.units[i+1]["name"]
        print(f"1 {unit['name']} = {subdiv} {next_unit}s")
    else:
        print(f"{unit['name']} (base unit)")
"""