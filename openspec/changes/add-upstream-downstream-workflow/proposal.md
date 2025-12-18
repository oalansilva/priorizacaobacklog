# Change Proposal: Add Upstream/Downstream Workflow with Capacity Allocation

## Why

The current ARCADIA system treats all backlog items uniformly without distinguishing between different workflow stages. However, the team operates with two distinct workflows:

1. **Upstream** - Initial development/discovery phase
2. **Downstream** - Implementation phase (can only start after Upstream completion)

Additionally, the team allocates capacity across three categories:
- **% Upstream** - Capacity for upstream work
- **% Downstream** - Capacity for downstream work  
- **% Sustentação** - Capacity for maintenance/support

**Problem**: Without this distinction, the prioritization and roadmap generation don't reflect the team's actual workflow and capacity constraints, leading to:
- Unrealistic roadmaps that don't account for workflow dependencies
- Inability to balance capacity across different work types
- Lack of visibility into which stage each item is in

## What Changes

### 1. Data Model Changes
- Add `workflow_stage` field to `BacklogItem`: `"upstream"`, `"downstream"`, or `"sustentacao"`
- Add capacity allocation to `SystemSettings`:
  - `capacity_upstream_percent`: float (0-100)
  - `capacity_downstream_percent`: float (0-100)
  - `capacity_sustentacao_percent`: float (0-100)
  - Validation: sum must equal 100%

### 2. Workflow Rules
- **Dependency**: Items can only move to Downstream after completing Upstream
- **Capacity Calculation**: Total capacity is split according to percentages
  - Example: 100 hours total → 40% Upstream (40h), 40% Downstream (40h), 20% Sustentação (20h)

### 3. Prioritization Logic
- Prioritize items **within each workflow stage** separately
- Respect capacity limits per stage
- LLM must consider workflow stage when prioritizing
- Items marked as "Must Have" still get priority, but within their stage

### 4. Roadmap Generation
- Roadmaps must show items grouped by workflow stage
- Display capacity allocation and usage per stage
- Show workflow progression (Upstream → Downstream)
- Highlight items blocked waiting for Upstream completion

### 5. UI Changes
- **Backlog Board**: 
  - Add workflow stage indicator/badge to each item
  - Filter by workflow stage
  - Show capacity allocation per stage
- **Settings Page**:
  - Add capacity allocation controls (% sliders with validation)
- **Roadmap View**:
  - Group items by workflow stage
  - Show capacity usage per stage
  - Visual workflow progression

### 6. API Changes
- Update `BacklogItem` schema to include `workflow_stage`
- Update `SystemSettings` schema for capacity percentages
- Modify prioritization endpoint to handle multi-stage capacity
- Update roadmap generation to include stage information

## Impact

### Affected Capabilities
This change affects multiple core capabilities:
- **Backlog Management** - New workflow stage field
- **Capacity Planning** - Multi-stage capacity allocation
- **Prioritization** - Stage-aware prioritization logic
- **Roadmap Generation** - Stage-grouped roadmaps
- **Settings Management** - New capacity configuration

### Affected Code/Systems

#### Backend (`app/`)
- `app/models/db.py` - Add `workflow_stage` to `BacklogItem`, capacity fields to `SystemSettings`
- `app/core/prioritization.py` - Multi-stage capacity logic
- `app/services/roadmap_service.py` - Stage-aware roadmap generation
- `app/repositories/` - Database schema updates (both SQLite and DynamoDB)
- `app/api/` - API endpoint updates

#### Frontend (`app/static/`)
- `components/BacklogBoard.jsx` - Stage indicators and filters
- `components/SettingsPanel.jsx` - Capacity allocation controls
- `components/RoadmapView.jsx` - Stage-grouped display
- `components/BacklogItemCard.jsx` - Stage badge/indicator

#### Database
- **SQLite**: Add `workflow_stage` column to `backlog_items` table
- **DynamoDB**: Update item schema (backward compatible)
- **Migration**: Default existing items to `"upstream"` or allow null initially

### Breaking Changes
- **BREAKING**: `BacklogItem` schema changes (new required field `workflow_stage`)
- **BREAKING**: `SystemSettings` schema changes (new capacity allocation fields)
- **Migration Required**: Existing backlog items need workflow stage assignment

### Risks
1. **Data Migration**: Existing items need stage assignment
2. **Complexity**: Multi-stage prioritization is more complex than single-stage
3. **LLM Prompt**: Need to update prompts to handle workflow stages correctly
4. **Validation**: Ensuring capacity percentages always sum to 100%

## Dependencies
- Requires understanding of current prioritization logic
- Requires database migration strategy
- May need updated LLM prompts for stage-aware prioritization

## Timeline Estimate
- **Design & Planning**: 1-2 days
- **Backend Implementation**: 3-4 days
- **Frontend Implementation**: 2-3 days
- **Testing & Migration**: 2 days
- **Total**: ~8-11 days
