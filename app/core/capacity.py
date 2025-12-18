"""
Capacity calculation utilities for multi-stage workflow.

This module provides functions to calculate and manage capacity allocation
across three workflow stages: Upstream, Downstream, and Sustentação.
"""

from typing import Dict
from app.models.db import SystemSettings


def calculate_stage_capacities(
    total_capacity: float, 
    settings: SystemSettings
) -> Dict[str, float]:
    """
    Calculate capacity for each workflow stage based on percentage allocation.
    
    Args:
        total_capacity: Total available capacity (e.g., hours or points)
        settings: System settings containing capacity percentage allocation
        
    Returns:
        Dictionary with capacity for each stage:
        {
            "upstream": float,
            "downstream": float,
            "sustentacao": float
        }
        
    Example:
        >>> settings = SystemSettings(
        ...     capacity_upstream_percent=40.0,
        ...     capacity_downstream_percent=40.0,
        ...     capacity_sustentacao_percent=20.0
        ... )
        >>> calculate_stage_capacities(100, settings)
        {'upstream': 40.0, 'downstream': 40.0, 'sustentacao': 20.0}
    """
    return {
        "upstream": total_capacity * (settings.capacity_upstream_percent / 100.0),
        "downstream": total_capacity * (settings.capacity_downstream_percent / 100.0),
        "sustentacao": total_capacity * (settings.capacity_sustentacao_percent / 100.0)
    }


def get_stage_capacity(
    stage: str,
    total_capacity: float,
    settings: SystemSettings
) -> float:
    """
    Get capacity for a specific workflow stage.
    
    Args:
        stage: Workflow stage ("upstream", "downstream", or "sustentacao")
        total_capacity: Total available capacity
        settings: System settings containing capacity percentage allocation
        
    Returns:
        Capacity allocated to the specified stage
        
    Raises:
        ValueError: If stage is not recognized
    """
    capacities = calculate_stage_capacities(total_capacity, settings)
    
    if stage not in capacities:
        raise ValueError(
            f"Invalid workflow stage: {stage}. "
            f"Must be one of: upstream, downstream, sustentacao"
        )
    
    return capacities[stage]


def calculate_capacity_usage(
    items: list,
    stage: str
) -> float:
    """
    Calculate total capacity used by items in a specific workflow stage.
    
    Args:
        items: List of backlog items
        stage: Workflow stage to calculate usage for
        
    Returns:
        Total effort (capacity) used by items in the specified stage
    """
    return sum(
        item.esforco_estimado 
        for item in items 
        if item.workflow_stage == stage
    )


def get_capacity_summary(
    items: list,
    total_capacity: float,
    settings: SystemSettings
) -> Dict[str, Dict[str, float]]:
    """
    Get comprehensive capacity summary for all workflow stages.
    
    Args:
        items: List of backlog items
        total_capacity: Total available capacity
        settings: System settings containing capacity percentage allocation
        
    Returns:
        Dictionary with capacity information for each stage:
        {
            "upstream": {
                "allocated": float,
                "used": float,
                "remaining": float,
                "usage_percent": float
            },
            "downstream": {...},
            "sustentacao": {...}
        }
    """
    stage_capacities = calculate_stage_capacities(total_capacity, settings)
    summary = {}
    
    for stage in ["upstream", "downstream", "sustentacao"]:
        allocated = stage_capacities[stage]
        used = calculate_capacity_usage(items, stage)
        remaining = max(0, allocated - used)
        usage_percent = (used / allocated * 100) if allocated > 0 else 0
        
        summary[stage] = {
            "allocated": allocated,
            "used": used,
            "remaining": remaining,
            "usage_percent": round(usage_percent, 2)
        }
    
    return summary


def validate_capacity_allocation(
    upstream_percent: float,
    downstream_percent: float,
    sustentacao_percent: float
) -> tuple[bool, str]:
    """
    Validate that capacity percentages sum to 100%.
    
    Args:
        upstream_percent: Percentage for upstream stage
        downstream_percent: Percentage for downstream stage
        sustentacao_percent: Percentage for sustentacao stage
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    total = upstream_percent + downstream_percent + sustentacao_percent
    
    if abs(total - 100.0) > 0.01:  # Allow small floating point errors
        return False, (
            f"Capacity percentages must sum to 100%, got {total}% "
            f"(upstream: {upstream_percent}%, downstream: {downstream_percent}%, "
            f"sustentacao: {sustentacao_percent}%)"
        )
    
    # Check individual percentages are non-negative
    if upstream_percent < 0 or downstream_percent < 0 or sustentacao_percent < 0:
        return False, "Capacity percentages cannot be negative"
    
    return True, ""
