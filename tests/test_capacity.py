"""
Unit tests for capacity calculation module.

Tests the workflow stage capacity allocation functionality.
"""

import pytest
from app.core.capacity import (
    calculate_stage_capacities,
    get_stage_capacity,
    calculate_capacity_usage,
    get_capacity_summary,
    validate_capacity_allocation
)
from app.models.db import SystemSettings, BacklogItem


class TestCapacityCalculations:
    """Test capacity calculation functions."""
    
    def test_calculate_stage_capacities_default(self):
        """Test capacity calculation with default percentages (40/40/20)."""
        settings = SystemSettings(
            capacity_upstream_percent=40.0,
            capacity_downstream_percent=40.0,
            capacity_sustentacao_percent=20.0
        )
        
        result = calculate_stage_capacities(100, settings)
        
        assert result["upstream"] == 40.0
        assert result["downstream"] == 40.0
        assert result["sustentacao"] == 20.0
    
    def test_calculate_stage_capacities_custom(self):
        """Test capacity calculation with custom percentages."""
        settings = SystemSettings(
            capacity_upstream_percent=50.0,
            capacity_downstream_percent=30.0,
            capacity_sustentacao_percent=20.0
        )
        
        result = calculate_stage_capacities(200, settings)
        
        assert result["upstream"] == 100.0
        assert result["downstream"] == 60.0
        assert result["sustentacao"] == 40.0
    
    def test_get_stage_capacity_upstream(self):
        """Test getting capacity for upstream stage."""
        settings = SystemSettings(
            capacity_upstream_percent=40.0,
            capacity_downstream_percent=40.0,
            capacity_sustentacao_percent=20.0
        )
        
        capacity = get_stage_capacity("upstream", 100, settings)
        
        assert capacity == 40.0
    
    def test_get_stage_capacity_invalid_stage(self):
        """Test that invalid stage raises ValueError."""
        settings = SystemSettings()
        
        with pytest.raises(ValueError, match="Invalid workflow stage"):
            get_stage_capacity("invalid_stage", 100, settings)
    
    def test_calculate_capacity_usage(self):
        """Test calculating capacity usage for a stage."""
        items = [
            BacklogItem(
                id="1",
                titulo="Item 1",
                descricao="Test",
                esforco_estimado=10,
                area="Tech",
                workflow_stage="upstream"
            ),
            BacklogItem(
                id="2",
                titulo="Item 2",
                descricao="Test",
                esforco_estimado=20,
                area="Tech",
                workflow_stage="upstream"
            ),
            BacklogItem(
                id="3",
                titulo="Item 3",
                descricao="Test",
                esforco_estimado=15,
                area="Tech",
                workflow_stage="downstream"
            ),
        ]
        
        upstream_usage = calculate_capacity_usage(items, "upstream")
        downstream_usage = calculate_capacity_usage(items, "downstream")
        
        assert upstream_usage == 30
        assert downstream_usage == 15
    
    def test_get_capacity_summary(self):
        """Test comprehensive capacity summary."""
        settings = SystemSettings(
            capacity_upstream_percent=50.0,
            capacity_downstream_percent=30.0,
            capacity_sustentacao_percent=20.0
        )
        
        items = [
            BacklogItem(
                id="1",
                titulo="Item 1",
                descricao="Test",
                esforco_estimado=25,
                area="Tech",
                workflow_stage="upstream"
            ),
            BacklogItem(
                id="2",
                titulo="Item 2",
                descricao="Test",
                esforco_estimado=15,
                area="Tech",
                workflow_stage="downstream"
            ),
        ]
        
        summary = get_capacity_summary(items, 100, settings)
        
        # Upstream: 50% of 100 = 50, used 25
        assert summary["upstream"]["allocated"] == 50.0
        assert summary["upstream"]["used"] == 25
        assert summary["upstream"]["remaining"] == 25.0
        assert summary["upstream"]["usage_percent"] == 50.0
        
        # Downstream: 30% of 100 = 30, used 15
        assert summary["downstream"]["allocated"] == 30.0
        assert summary["downstream"]["used"] == 15
        assert summary["downstream"]["remaining"] == 15.0
        assert summary["downstream"]["usage_percent"] == 50.0
        
        # Sustentacao: 20% of 100 = 20, used 0
        assert summary["sustentacao"]["allocated"] == 20.0
        assert summary["sustentacao"]["used"] == 0
        assert summary["sustentacao"]["remaining"] == 20.0
        assert summary["sustentacao"]["usage_percent"] == 0.0


class TestCapacityValidation:
    """Test capacity allocation validation."""
    
    def test_validate_capacity_allocation_valid(self):
        """Test validation with valid percentages (sum = 100)."""
        is_valid, error = validate_capacity_allocation(40.0, 40.0, 20.0)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_capacity_allocation_invalid_sum(self):
        """Test validation with invalid sum."""
        is_valid, error = validate_capacity_allocation(40.0, 40.0, 30.0)
        
        assert is_valid is False
        assert "must sum to 100%" in error
        assert "110.0%" in error
    
    def test_validate_capacity_allocation_negative(self):
        """Test validation with negative percentage."""
        is_valid, error = validate_capacity_allocation(50.0, 60.0, -10.0)
        
        assert is_valid is False
        assert "cannot be negative" in error
    
    def test_validate_capacity_allocation_floating_point_tolerance(self):
        """Test that small floating point errors are tolerated."""
        # 33.33 + 33.33 + 33.34 = 100.00 (with floating point precision)
        is_valid, error = validate_capacity_allocation(33.33, 33.33, 33.34)
        
        assert is_valid is True
        assert error == ""


class TestSystemSettingsValidation:
    """Test SystemSettings model validation."""
    
    def test_system_settings_valid_capacity(self):
        """Test creating SystemSettings with valid capacity allocation."""
        settings = SystemSettings(
            capacity_upstream_percent=40.0,
            capacity_downstream_percent=40.0,
            capacity_sustentacao_percent=20.0
        )
        
        assert settings.capacity_upstream_percent == 40.0
        assert settings.capacity_downstream_percent == 40.0
        assert settings.capacity_sustentacao_percent == 20.0
    
    def test_system_settings_invalid_capacity_sum(self):
        """Test that SystemSettings validation rejects invalid sum."""
        with pytest.raises(ValueError, match="must sum to 100%"):
            SystemSettings(
                capacity_upstream_percent=50.0,
                capacity_downstream_percent=40.0,
                capacity_sustentacao_percent=20.0  # Sum = 110%
            )
    
    def test_system_settings_default_values(self):
        """Test that SystemSettings has correct default values."""
        settings = SystemSettings()
        
        assert settings.capacity_upstream_percent == 40.0
        assert settings.capacity_downstream_percent == 40.0
        assert settings.capacity_sustentacao_percent == 20.0
        
        # Verify defaults sum to 100%
        total = (settings.capacity_upstream_percent + 
                settings.capacity_downstream_percent + 
                settings.capacity_sustentacao_percent)
        assert total == 100.0


class TestBacklogItemWorkflowStage:
    """Test BacklogItem workflow stage functionality."""
    
    def test_backlog_item_default_workflow_stage(self):
        """Test that BacklogItem defaults to 'upstream'."""
        item = BacklogItem(
            id="1",
            titulo="Test Item",
            descricao="Description",
            esforco_estimado=10,
            area="Tech"
        )
        
        assert item.workflow_stage == "upstream"
        assert item.upstream_completed_at is None
    
    def test_backlog_item_custom_workflow_stage(self):
        """Test creating BacklogItem with custom workflow stage."""
        item = BacklogItem(
            id="1",
            titulo="Test Item",
            descricao="Description",
            esforco_estimado=10,
            area="Tech",
            workflow_stage="downstream"
        )
        
        assert item.workflow_stage == "downstream"
    
    def test_backlog_item_all_workflow_stages(self):
        """Test all three workflow stages."""
        stages = ["upstream", "downstream", "sustentacao"]
        
        for stage in stages:
            item = BacklogItem(
                id=f"item-{stage}",
                titulo=f"Test {stage}",
                descricao="Description",
                esforco_estimado=10,
                area="Tech",
                workflow_stage=stage
            )
            assert item.workflow_stage == stage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
