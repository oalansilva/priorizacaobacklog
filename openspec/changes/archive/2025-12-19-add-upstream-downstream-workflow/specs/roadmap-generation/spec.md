# Roadmap Generation Capability - Spec Delta

## ADDED Requirements

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

## UI Requirements

### Requirement: Roadmap Stage Visualization
The roadmap UI SHALL provide clear visual distinction between workflow stages.

#### Scenario: Color-coded stage sections
- **WHEN** a user views a roadmap
- **THEN** each stage section SHALL have a distinct color:
  - Upstream: Blue
  - Downstream: Green
  - Sustentação: Orange
- **AND** items SHALL have matching color badges or borders

#### Scenario: Collapsible stage sections
- **WHEN** a user views a roadmap with many items
- **THEN** each stage section SHALL be collapsible
- **AND** show item count when collapsed
- **AND** preserve collapse state in user preferences

#### Scenario: Stage capacity visualization
- **WHEN** a user views a stage section
- **THEN** the system SHALL display a capacity progress bar
- **AND** show percentage used
- **AND** use color coding:
  - Green: < 80% used
  - Yellow: 80-100% used
  - Red: > 100% used (overallocated)

### Requirement: Interactive Roadmap Timeline
The roadmap timeline SHALL show workflow stage progression.

#### Scenario: Timeline with stage markers
- **WHEN** a user views a roadmap timeline
- **THEN** items SHALL be positioned on the timeline
- **AND** include visual markers for workflow stage
- **AND** show stage transitions if applicable

#### Scenario: Drag-and-drop stage transition
- **WHEN** a user drags an item between stage sections
- **THEN** the system SHALL validate the transition
- **AND** update the item's workflow_stage
- **AND** recalculate capacity usage
- **AND** show confirmation or error message
