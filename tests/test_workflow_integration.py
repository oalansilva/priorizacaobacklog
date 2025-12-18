"""
Integration tests for workflow stage functionality.

Tests the end-to-end workflow stage features including database operations.
"""

import pytest
from datetime import datetime
from app.core.database import SQLiteRepository
from app.models.db import BacklogItem, SystemSettings
import tempfile
import os


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    repo = SQLiteRepository(db_path=path)
    
    yield repo
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


class TestWorkflowStageDatabase:
    """Test workflow stage database operations."""
    
    def test_add_item_with_workflow_stage(self, temp_db):
        """Test adding item with workflow stage to database."""
        item = BacklogItem(
            id="test-1",
            titulo="Test Item",
            descricao="Test Description",
            esforco_estimado=10,
            area="Tech",
            workflow_stage="downstream"
        )
        
        result = temp_db.add_item(item)
        
        assert result.id == "test-1"
        assert result.workflow_stage == "downstream"
    
    def test_list_items_with_workflow_stage(self, temp_db):
        """Test listing items preserves workflow stage."""
        items = [
            BacklogItem(
                id=f"item-{i}",
                titulo=f"Item {i}",
                descricao="Test",
                esforco_estimado=10,
                area="Tech",
                workflow_stage=stage
            )
            for i, stage in enumerate(["upstream", "downstream", "sustentacao"])
        ]
        
        for item in items:
            temp_db.add_item(item)
        
        retrieved = temp_db.list_items()
        
        assert len(retrieved) == 3
        assert retrieved[0].workflow_stage == "upstream"
        assert retrieved[1].workflow_stage == "downstream"
        assert retrieved[2].workflow_stage == "sustentacao"
    
    def test_update_item_workflow_stage(self, temp_db):
        """Test updating item's workflow stage."""
        item = BacklogItem(
            id="test-1",
            titulo="Test Item",
            descricao="Test",
            esforco_estimado=10,
            area="Tech",
            workflow_stage="upstream"
        )
        
        temp_db.add_item(item)
        
        # Update to downstream
        item.workflow_stage = "downstream"
        item.upstream_completed_at = datetime.now().isoformat()
        
        temp_db.update_item(item)
        
        retrieved = temp_db.list_items()[0]
        assert retrieved.workflow_stage == "downstream"
        assert retrieved.upstream_completed_at is not None
    
    def test_settings_capacity_allocation(self, temp_db):
        """Test saving and retrieving capacity allocation settings."""
        settings = SystemSettings(
            capacidade_total=1000,
            percentual_sustentacao=20,
            capacity_upstream_percent=50.0,
            capacity_downstream_percent=30.0,
            capacity_sustentacao_percent=20.0
        )
        
        temp_db.update_settings(settings)
        
        retrieved = temp_db.get_settings()
        
        assert retrieved.capacity_upstream_percent == 50.0
        assert retrieved.capacity_downstream_percent == 30.0
        assert retrieved.capacity_sustentacao_percent == 20.0
    
    def test_default_workflow_stage_for_existing_items(self, temp_db):
        """Test that items without workflow_stage default to 'upstream'."""
        # Simulate old item without workflow_stage
        item = BacklogItem(
            id="old-item",
            titulo="Old Item",
            descricao="Test",
            esforco_estimado=10,
            area="Tech"
        )
        
        temp_db.add_item(item)
        
        retrieved = temp_db.list_items()[0]
        
        # Should default to upstream
        assert retrieved.workflow_stage == "upstream"


class TestWorkflowStageFiltering:
    """Test filtering items by workflow stage."""
    
    def test_filter_items_by_stage(self, temp_db):
        """Test filtering items by workflow stage."""
        items = [
            BacklogItem(
                id=f"item-{i}",
                titulo=f"Item {i}",
                descricao="Test",
                esforco_estimado=10,
                area="Tech",
                workflow_stage=stage
            )
            for i, stage in enumerate([
                "upstream", "upstream", "downstream", 
                "downstream", "sustentacao"
            ])
        ]
        
        for item in items:
            temp_db.add_item(item)
        
        all_items = temp_db.list_items()
        
        # Filter by stage
        upstream_items = [i for i in all_items if i.workflow_stage == "upstream"]
        downstream_items = [i for i in all_items if i.workflow_stage == "downstream"]
        sustentacao_items = [i for i in all_items if i.workflow_stage == "sustentacao"]
        
        assert len(upstream_items) == 2
        assert len(downstream_items) == 2
        assert len(sustentacao_items) == 1


class TestCapacityAllocationIntegration:
    """Test capacity allocation with real database."""
    
    def test_capacity_allocation_persistence(self, temp_db):
        """Test that capacity allocation persists across updates."""
        # Set initial allocation
        settings1 = SystemSettings(
            capacity_upstream_percent=40.0,
            capacity_downstream_percent=40.0,
            capacity_sustentacao_percent=20.0
        )
        temp_db.update_settings(settings1)
        
        # Update allocation
        settings2 = SystemSettings(
            capacity_upstream_percent=50.0,
            capacity_downstream_percent=30.0,
            capacity_sustentacao_percent=20.0
        )
        temp_db.update_settings(settings2)
        
        # Retrieve and verify
        retrieved = temp_db.get_settings()
        
        assert retrieved.capacity_upstream_percent == 50.0
        assert retrieved.capacity_downstream_percent == 30.0
        assert retrieved.capacity_sustentacao_percent == 20.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
