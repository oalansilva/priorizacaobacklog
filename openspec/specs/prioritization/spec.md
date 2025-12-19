# prioritization Specification

## Purpose
TBD - created by archiving change add-upstream-downstream-workflow. Update Purpose after archive.
## Requirements
### Requirement: Stage-Aware Prioritization
The prioritization system SHALL prioritize items separately for each workflow stage.

**Previous**: All items were prioritized together in a single list.

**Modified**: Items SHALL be prioritized within their workflow stage, respecting per-stage capacity limits.

#### Scenario: Prioritize upstream items
- **WHEN** the system prioritizes backlog items
- **THEN** it SHALL group items by workflow stage
- **AND** prioritize upstream items separately
- **AND** respect upstream capacity limit
- **AND** items SHALL be ranked within the upstream stage

#### Scenario: Prioritize downstream items
- **WHEN** the system prioritizes downstream items
- **THEN** it SHALL only consider items with `upstream_completed_at` set
- **AND** respect downstream capacity limit
- **AND** items SHALL be ranked within the downstream stage

#### Scenario: Prioritize sustentação items
- **WHEN** the system prioritizes sustentação items
- **THEN** it SHALL respect sustentação capacity limit
- **AND** items SHALL be ranked within the sustentação stage

#### Scenario: Multi-stage prioritization result
- **WHEN** prioritization completes
- **THEN** the system SHALL return results grouped by stage
- **AND** each stage SHALL have its own priority ranking (1, 2, 3, ...)
- **AND** include capacity usage per stage

### Requirement: LLM Prompt Enhancement
The LLM prioritization prompts SHALL include workflow stage context.

#### Scenario: Upstream prioritization prompt
- **WHEN** the system calls the LLM to prioritize upstream items
- **THEN** the prompt SHALL include:
  - Stage name: "Upstream"
  - Stage description: "Discovery, research, design work"
  - Available capacity for upstream stage
  - Only upstream items

#### Scenario: Downstream prioritization prompt
- **WHEN** the system calls the LLM to prioritize downstream items
- **THEN** the prompt SHALL include:
  - Stage name: "Downstream"
  - Stage description: "Implementation work (requires upstream completion)"
  - Available capacity for downstream stage
  - Only downstream items that have completed upstream

#### Scenario: Sustentação prioritization prompt
- **WHEN** the system calls the LLM to prioritize sustentação items
- **THEN** the prompt SHALL include:
  - Stage name: "Sustentação"
  - Stage description: "Maintenance, bug fixes, support"
  - Available capacity for sustentação stage
  - Only sustentação items

### Requirement: Workflow Stage Validation in Prioritization
The prioritization system SHALL validate workflow stage constraints.

#### Scenario: Warn about downstream items without upstream completion
- **WHEN** prioritizing downstream items
- **AND** some items lack `upstream_completed_at`
- **THEN** the system SHALL log a warning
- **AND** optionally exclude those items from prioritization
- **AND** notify the user of excluded items

#### Scenario: Capacity overflow per stage
- **WHEN** prioritized items exceed stage capacity
- **THEN** the system SHALL mark excess items as "Despriorizado"
- **AND** provide justification: "Exceeds {stage} capacity"
- **AND** show which items fit within capacity

### Requirement: Stage-Specific "Must Have" Handling
The system SHALL handle "Must Have" items within their workflow stage.

#### Scenario: Must Have upstream item
- **WHEN** an upstream item is marked as "Must Have"
- **THEN** it SHALL get priority within the upstream stage
- **AND** receive 100% score
- **AND** be prioritized before other upstream items

#### Scenario: Must Have downstream item
- **WHEN** a downstream item is marked as "Must Have"
- **AND** has completed upstream
- **THEN** it SHALL get priority within the downstream stage
- **AND** receive 100% score
- **AND** be prioritized before other downstream items

#### Scenario: Must Have without upstream completion
- **WHEN** a downstream item is marked as "Must Have"
- **AND** has NOT completed upstream
- **THEN** the system SHALL warn the user
- **AND** suggest completing upstream first or moving to upstream stage

