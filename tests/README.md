# Test Configuration

This directory contains tests for the workflow stage functionality.

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_capacity.py -v
pytest tests/test_workflow_integration.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=app.core.capacity --cov=app.models.db -v
```

## Test Structure

### Unit Tests (`test_capacity.py`)
- **TestCapacityCalculations**: Tests for capacity calculation functions
- **TestCapacityValidation**: Tests for capacity allocation validation
- **TestSystemSettingsValidation**: Tests for SystemSettings model validation
- **TestBacklogItemWorkflowStage**: Tests for BacklogItem workflow stage

### Integration Tests (`test_workflow_integration.py`)
- **TestWorkflowStageDatabase**: Tests for database operations with workflow stages
- **TestWorkflowStageFiltering**: Tests for filtering items by stage
- **TestCapacityAllocationIntegration**: Tests for capacity allocation persistence

## Test Coverage

The tests cover:
- ✅ Capacity calculation with different percentages
- ✅ Capacity usage tracking per stage
- ✅ Capacity summary generation
- ✅ Validation of capacity allocation (sum = 100%)
- ✅ SystemSettings model validation
- ✅ BacklogItem workflow stage defaults
- ✅ Database CRUD operations with workflow stages
- ✅ Settings persistence
- ✅ Filtering items by workflow stage

## Dependencies

Tests require:
- pytest
- pytest-cov (optional, for coverage reports)

Install with:
```bash
pip install pytest pytest-cov
```
