# capacity-planning Specification

## Purpose
TBD - created by archiving change add-upstream-downstream-workflow. Update Purpose after archive.
## Requirements
### Requirement: Multi-Stage Capacity Allocation
The system SHALL support capacity allocation across three workflow stages.

#### Scenario: Configure capacity percentages
- **WHEN** a user configures capacity allocation in settings
- **THEN** the system SHALL accept three percentage values:
  - `capacity_upstream_percent` (0-100)
  - `capacity_downstream_percent` (0-100)
  - `capacity_sustentacao_percent` (0-100)
- **AND** the sum of all three percentages SHALL equal 100%

#### Scenario: Validate capacity sum
- **WHEN** a user saves capacity allocation settings
- **AND** the sum of percentages does not equal 100%
- **THEN** the system SHALL reject the update
- **AND** display an error message: "Capacity percentages must sum to 100%"

#### Scenario: Calculate stage capacities
- **WHEN** the system calculates available capacity
- **THEN** it SHALL split total capacity according to configured percentages
- **AND** return capacity values for each stage

**Example**:
- Total capacity: 100 hours
- Upstream: 40% → 40 hours
- Downstream: 40% → 40 hours
- Sustentação: 20% → 20 hours

### Requirement: Default Capacity Allocation
The system SHALL provide default capacity allocation values.

#### Scenario: First-time setup
- **WHEN** a user accesses capacity settings for the first time
- **THEN** the system SHALL use default values:
  - Upstream: 40%
  - Downstream: 40%
  - Sustentação: 20%

#### Scenario: Display current allocation
- **WHEN** a user views capacity settings
- **THEN** the system SHALL display current percentage allocation
- **AND** show calculated hours per stage based on total capacity

### Requirement: Capacity Usage Tracking
The system SHALL track capacity usage per workflow stage.

#### Scenario: Calculate used capacity per stage
- **WHEN** items are prioritized
- **THEN** the system SHALL calculate total effort for prioritized items per stage
- **AND** compare against allocated capacity for that stage

#### Scenario: Display capacity usage
- **WHEN** a user views the backlog or roadmap
- **THEN** the system SHALL display:
  - Allocated capacity per stage
  - Used capacity per stage
  - Remaining capacity per stage
  - Usage percentage per stage

### Requirement: System Settings Data Model
The system settings SHALL include capacity allocation configuration.

**Previous**: System settings included total capacity and prioritization weights only.

**Modified**: System settings SHALL include:
- All previous fields (total capacity, weights, etc.)
- `capacity_upstream_percent`: float (default 40.0)
- `capacity_downstream_percent`: float (default 40.0)
- `capacity_sustentacao_percent`: float (default 20.0)

#### Scenario: Save system settings
- **WHEN** a user saves system settings
- **THEN** the system SHALL validate capacity percentages sum to 100%
- **AND** persist all settings including capacity allocation

#### Scenario: Load system settings
- **WHEN** the system loads settings
- **THEN** it SHALL return all settings including capacity percentages
- **AND** use defaults if capacity percentages are not set

