# Backlog Management Capability - Spec Delta

## ADDED Requirements

### Requirement: Workflow Stage Tracking
The system SHALL track the workflow stage for each backlog item.

#### Scenario: Create item with workflow stage
- **WHEN** a user creates a new backlog item
- **THEN** the item SHALL have a `workflow_stage` field set to one of: `"upstream"`, `"downstream"`, or `"sustentacao"`
- **AND** the default value SHALL be `"upstream"`

#### Scenario: Update item workflow stage
- **WHEN** a user updates an item's workflow stage
- **THEN** the system SHALL validate the stage value is one of the allowed values
- **AND** the system SHALL persist the new stage value

#### Scenario: Filter items by workflow stage
- **WHEN** a user requests backlog items
- **THEN** the system SHALL support filtering by `workflow_stage`
- **AND** return only items matching the specified stage

### Requirement: Upstream Completion Tracking
The system SHALL track when an item completes the upstream stage.

#### Scenario: Mark upstream as complete
- **WHEN** a user marks an item's upstream work as complete
- **THEN** the system SHALL set the `upstream_completed_at` timestamp
- **AND** the timestamp SHALL be in UTC format

#### Scenario: View upstream completion status
- **WHEN** a user views a backlog item
- **THEN** the system SHALL display whether upstream is complete
- **AND** show the completion date if available

### Requirement: Workflow Stage Validation
The system SHALL enforce workflow stage transition rules.

#### Scenario: Prevent downstream without upstream completion
- **WHEN** a user attempts to move an item to downstream stage
- **AND** the item's `upstream_completed_at` is null
- **THEN** the system SHALL display a warning message
- **AND** the system SHOULD prevent the transition (soft enforcement initially)

#### Scenario: Allow downstream after upstream completion
- **WHEN** a user attempts to move an item to downstream stage
- **AND** the item's `upstream_completed_at` is set
- **THEN** the system SHALL allow the transition

## MODIFIED Requirements

### Requirement: Backlog Item Data Model
The backlog item data model SHALL include workflow stage information.

**Previous**: Backlog items had status, priority, and impact attributes only.

**Modified**: Backlog items SHALL include:
- All previous fields (status, priority, impacts, etc.)
- `workflow_stage`: string enum (`"upstream"` | `"downstream"` | `"sustentacao"`)
- `upstream_completed_at`: optional timestamp

#### Scenario: Create backlog item with all fields
- **WHEN** a user creates a backlog item
- **THEN** the system SHALL accept and store all required fields
- **AND** include `workflow_stage` and `upstream_completed_at`

#### Scenario: Retrieve backlog item
- **WHEN** a user retrieves a backlog item
- **THEN** the system SHALL return all fields including workflow stage
- **AND** the response SHALL be backward compatible (handle missing fields gracefully)

## Database Schema Changes

### SQLite
```sql
ALTER TABLE backlog_items 
ADD COLUMN workflow_stage TEXT DEFAULT 'upstream';

ALTER TABLE backlog_items 
ADD COLUMN upstream_completed_at TIMESTAMP NULL;
```

### DynamoDB
- Add `workflow_stage` attribute (string)
- Add `upstream_completed_at` attribute (string, ISO 8601 format)
- Handle missing attributes gracefully with defaults
