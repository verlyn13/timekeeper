"""
Visualization tools for the AgentTemporal framework.

This module provides visualization capabilities for timepoints,
temporal hierarchies, and task schedules.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

def visualize_temporal_hierarchy(temporal_system, figsize=(10, 6)):
    """
    Visualize the hierarchical partitioning of time.
    
    Args:
        temporal_system: An AgentTemporal instance
        figsize: Figure size tuple (default: (10, 6))
        
    Returns:
        matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get unit names
    units = [u["name"] for u in temporal_system.units]
    
    # Setup y-axis
    y_positions = np.arange(len(units))
    ax.set_yticks(y_positions)
    ax.set_yticklabels(units)
    
    # Set axis labels
    ax.set_title('Temporal Hierarchy')
    ax.set_xlabel('Time')
    ax.set_ylabel('Hierarchical Units')
    
    # Draw partition boundaries for each unit
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
    
    # Clean up the plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    return fig, ax

def visualize_timepoint(temporal_system, timepoint, figsize=(10, 3)):
    """
    Visualize a timepoint on the temporal hierarchy.
    
    Args:
        temporal_system: An AgentTemporal instance
        timepoint: A timepoint dictionary
        figsize: Figure size tuple (default: (10, 3))
        
    Returns:
        matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get unit names
    units = [u["name"] for u in temporal_system.units]
    
    # Convert to base units for visualization
    base_value = temporal_system.to_base_units(timepoint)
    
    # Setup y-axis
    y_positions = np.arange(len(units))
    ax.set_yticks(y_positions)
    ax.set_yticklabels(units)
    
    # Set axis labels
    ax.set_title(f'Timepoint Visualization: {", ".join(f"{k}={v}" for k, v in timepoint.items())}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Hierarchical Units')
    
    # Track the position in each unit
    running_base = 0
    positions = []
    
    # Calculate positions for each unit
    for i, unit in enumerate(temporal_system.units):
        # For each unit, calculate where in the timeline it sits
        if i == len(temporal_system.units) - 1:  # Base unit
            positions.append((base_value, 1))  # Base unit gets full value
        else:
            # Get conversion factor to base
            factor = temporal_system.conversion_factors[(unit["name"], temporal_system.units[-1]["name"])]
            # Get the unit value
            unit_value = timepoint[unit["name"]]
            # Calculate base units for this unit
            unit_base = unit_value * factor
            # Add to positions
            positions.append((running_base, unit_base))
            # Update running total
            running_base += unit_base
    
    # Draw hierarchical representation
    ax.axvline(x=base_value, color='red', linestyle='-', linewidth=2)
    
    for i, (start, width) in enumerate(positions):
        if width > 0:  # Only draw if this unit has a value
            rect = Rectangle((start, i-0.4), width, 0.8, 
                             facecolor='skyblue', alpha=0.7,
                             edgecolor='blue')
            ax.add_patch(rect)
            
            # Add label if there's room
            if width > max(base_value * 0.05, 1):
                ax.text(start + width/2, i, 
                        f"{timepoint[temporal_system.units[i]['name']]}", 
                        va='center', ha='center')
    
    # Set axis limits
    ax.set_xlim(0, base_value * 1.1)
    
    # Clean up the plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig, ax

def visualize_conversions(temporal_system, figsize=(8, 6)):
    """
    Visualize the conversion factors between temporal units.
    
    Args:
        temporal_system: An AgentTemporal instance
        figsize: Figure size tuple (default: (8, 6))
        
    Returns:
        matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get unit names
    units = [u["name"] for u in temporal_system.units]
    n_units = len(units)
    
    # Create conversion matrix
    conversion_matrix = np.zeros((n_units, n_units))
    
    for i, from_unit in enumerate(units):
        for j, to_unit in enumerate(units):
            conversion_matrix[i, j] = temporal_system.conversion_factors[(from_unit, to_unit)]
    
    # Create logarithmic color map for better visualization
    conversion_matrix = np.log10(conversion_matrix + 1e-10)  # Avoid log(0)
    
    # Create custom colormap (blue to red)
    cmap = LinearSegmentedColormap.from_list('conversion', 
                                          [(0, 'white'), 
                                           (0.5, 'skyblue'), 
                                           (1, 'darkblue')])
    
    # Plot heatmap
    im = ax.imshow(conversion_matrix, cmap=cmap)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('log10(conversion factor)')
    
    # Set tick labels
    ax.set_xticks(np.arange(n_units))
    ax.set_yticks(np.arange(n_units))
    ax.set_xticklabels(units)
    ax.set_yticklabels(units)
    
    # Rotate x labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Set title and labels
    ax.set_title('Unit Conversion Factors')
    ax.set_xlabel('Target Unit')
    ax.set_ylabel('Source Unit')
    
    # Add grid
    ax.set_xticks(np.arange(n_units+1)-.5, minor=True)
    ax.set_yticks(np.arange(n_units+1)-.5, minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Add text annotations
    for i in range(n_units):
        for j in range(n_units):
            if conversion_matrix[i, j] > -5:  # Only show reasonable values
                ax.text(j, i, f"{10**conversion_matrix[i, j]:.1e}",
                        ha="center", va="center", 
                        color="black" if conversion_matrix[i, j] < 0 else "white",
                        fontsize=8)
    
    plt.tight_layout()
    return fig, ax

def visualize_schedule(scheduler, figsize=(12, 6)):
    """
    Visualize a task schedule with Gantt chart.
    
    Args:
        scheduler: A TaskScheduler instance with scheduled tasks
        figsize: Figure size tuple (default: (12, 6))
        
    Returns:
        matplotlib figure and axes
    """
    # Get the visualization data
    viz_data = scheduler.visualize_schedule()
    
    # Sort by agent and start time
    viz_data.sort(key=lambda x: (x["agent"], x["start"]))
    
    # Group by agent
    agents = {}
    for task in viz_data:
        agent_id = task["agent"]
        if agent_id not in agents:
            agents[agent_id] = []
        agents[agent_id].append(task)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Colors for different tasks
    colors = plt.cm.tab10.colors
    
    # Track y-position
    y_pos = 0
    labels = []
    
    # Plot tasks for each agent
    for agent_id, tasks in agents.items():
        # Add agent label
        ax.text(-0.01 * max(task["end"] for task in viz_data), 
                y_pos + len(tasks)/2, 
                f"Agent {agent_id}", 
                va='center', ha='right', fontweight='bold')
        
        # Plot each task as a rectangle
        for i, task in enumerate(tasks):
            # Create rectangle
            rect = Rectangle((task["start"], y_pos + i), 
                             task["duration"], 0.8, 
                             facecolor=colors[int(task["id"].replace("T", "")) % len(colors)],
                             alpha=0.7)
            ax.add_patch(rect)
            
            # Add task label
            ax.text(task["start"] + task["duration"]/2, 
                    y_pos + i + 0.4, 
                    task["id"], 
                    va='center', ha='center', 
                    color='white' if task["duration"] > 100 else 'black',
                    fontweight='bold')
            
            # Track label for dependencies
            labels.append((task["id"], task["start"], task["end"], y_pos + i + 0.4))
        
        # Update y-position for next agent
        y_pos += len(tasks) + 1
    
    # Draw dependency arrows
    for task in viz_data:
        task_label = next(label for label in labels if label[0] == task["id"])
        
        for dep_id in task["dependencies"]:
            dep_label = next(label for label in labels if label[0] == dep_id)
            
            # Draw arrow from dependency end to task start
            ax.annotate("", 
                        xy=(task["start"], task_label[3]), 
                        xytext=(dep_label[2], dep_label[3]),
                        arrowprops=dict(arrowstyle="->", color="gray", alpha=0.5))
    
    # Set axis limits
    ax.set_ylim(0, y_pos)
    ax.set_xlim(-0.02 * max(task["end"] for task in viz_data), 
                1.02 * max(task["end"] for task in viz_data))
    
    # Remove y-axis ticks
    ax.set_yticks([])
    
    # Set title and labels
    ax.set_title('Task Schedule')
    ax.set_xlabel('Time (in base units)')
    
    # Add grid
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    return fig, ax