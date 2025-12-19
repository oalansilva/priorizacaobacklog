# roadmap-generation Specification

## Purpose
TBD - created by archiving change add-upstream-downstream-workflow. Update Purpose after archive.
## Requirements
### Requirement: Stage-Grouped Roadmap Display
Roadmaps SHALL display items grouped by workflow stage.

**Previous**: Roadmaps showed all items in a single prioritized list.

**Modified**: Roadmaps SHALL organize items into sections by workflow stage with capacity information.

#### Scenario: Generate roadmap with stage grouping
- **WHEN** the system generates a roadmap
- **THEN** it SHALL create separate sections for each workflow stage:
  - Upstream section
  - Downstream section
  - Sustentação section
- **AND** each section SHALL contain only items from that stage
- **AND** items within each section SHALL be ordered by priority

#### Scenario: Display capacity per stage in roadmap
- **WHEN** a user views a roadmap
- **THEN** each stage section SHALL display:
  - Total allocated capacity for the stage
  - Total used capacity (sum of prioritized items)
  - Remaining capacity
  - Usage percentage
- **AND** use visual indicators (progress bars, colors)

#### Scenario: Empty stage section
- **WHEN** a workflow stage has no prioritized items
- **THEN** the roadmap SHALL still show the stage section
- **AND** display "No items prioritized for this stage"
- **AND** show allocated capacity as unused

### Requirement: Workflow Progression Indicator
Roadmaps SHALL indicate workflow progression and dependencies.

#### Scenario: Show upstream → downstream flow
- **WHEN** a user views a roadmap
- **THEN** the system SHALL visually indicate the workflow flow
- **AND** show that downstream items depend on upstream completion
- **AND** use arrows, icons, or labels to indicate progression

#### Scenario: Highlight blocked downstream items
- **WHEN** a downstream item is in the roadmap
- **AND** its upstream work is not yet complete
- **THEN** the system SHALL highlight the item as blocked
- **AND** display a warning icon or badge
- **AND** show tooltip: "Waiting for upstream completion"

### Requirement: Stage-Aware Roadmap Filtering
Users SHALL be able to filter roadmap views by workflow stage.

#### Scenario: Filter roadmap by stage
- **WHEN** a user selects a workflow stage filter
- **THEN** the roadmap SHALL show only items from that stage
- **AND** display capacity information for the selected stage only

#### Scenario: View all stages
- **WHEN** a user selects "All Stages" filter
- **THEN** the roadmap SHALL show all three stage sections
- **AND** display capacity information for all stages

### Requirement: Roadmap Export with Stages
Roadmap exports SHALL include workflow stage information.

#### Scenario: Export roadmap to PDF with stages
- **WHEN** a user exports a roadmap to PDF
- **THEN** the PDF SHALL include:
  - Separate sections for each workflow stage
  - Capacity allocation and usage per stage
  - Visual stage grouping (headers, colors)
  - Workflow progression indicators

#### Scenario: Export roadmap to CSV with stages
- **WHEN** a user exports a roadmap to CSV
- **THEN** the CSV SHALL include a `workflow_stage` column
- **AND** include capacity allocation columns:
  - `stage_allocated_capacity`
  - `stage_used_capacity`
  - `stage_remaining_capacity`

### Requirement: Historical Roadmap Stage Tracking
Historical roadmaps SHALL preserve workflow stage information.

#### Scenario: View historical roadmap with stages
- **WHEN** a user views a previously generated roadmap
- **THEN** the system SHALL display items with their original workflow stages
- **AND** show capacity allocation as it was at generation time
- **AND** preserve stage grouping from the original roadmap

#### Scenario: Compare roadmaps across time
- **WHEN** a user compares multiple roadmaps
- **THEN** the system SHALL show how items moved between stages
- **AND** highlight stage transitions
- **AND** show capacity allocation changes over time

