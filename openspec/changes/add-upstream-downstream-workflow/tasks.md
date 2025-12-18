# Implementation Tasks: Upstream/Downstream Workflow

## 1. Database Schema & Models

### 1.1 Update Data Models
- [ ] Add `workflow_stage` field to `BacklogItem` in `app/models/db.py`
- [ ] Add `upstream_completed_at` field to `BacklogItem`
- [ ] Add capacity percentage fields to `SystemSettings`
- [ ] Add Pydantic validators for capacity sum = 100%
- [ ] Update model documentation/docstrings

### 1.2 Database Migrations
- [ ] Create SQLite migration script for new columns
- [ ] Test SQLite migration on dev database
- [ ] Update DynamoDB repository to handle new fields gracefully
- [ ] Create data backfill script for existing items
- [ ] Test migrations with sample data

## 2. Backend - Repository Layer

### 2.1 SQLite Repository
- [ ] Update `SQLiteRepository.create_item()` to include workflow_stage
- [ ] Update `SQLiteRepository.update_item()` to handle stage changes
- [ ] Add index on `workflow_stage` column for performance
- [ ] Update queries to filter by workflow_stage

### 2.2 DynamoDB Repository
- [ ] Update `DynamoDBRepository.create_item()` to include workflow_stage
- [ ] Update `DynamoDBRepository.update_item()` to handle stage changes
- [ ] Handle missing workflow_stage field gracefully (default to "upstream")
- [ ] Update queries to filter by workflow_stage

### 2.3 Settings Repository
- [ ] Update settings save/load to include capacity percentages
- [ ] Add validation for capacity percentage sum
- [ ] Provide default values if not set

## 3. Backend - Core Logic

### 3.1 Capacity Calculation
- [ ] Create `calculate_stage_capacities()` function in `app/core/capacity.py`
- [ ] Update `app/core/prioritization.py` to use multi-stage capacity
- [ ] Add unit tests for capacity calculation
- [ ] Handle edge cases (zero capacity, rounding errors)

### 3.2 Prioritization Logic
- [ ] Update LLM prompt to include workflow stage context
- [ ] Implement stage-based item grouping
- [ ] Modify prioritization to run per-stage
- [ ] Update capacity enforcement per stage
- [ ] Add validation for downstream items (require upstream completion)
- [ ] Update unit tests for multi-stage prioritization

### 3.3 Roadmap Generation
- [ ] Update `app/services/roadmap_service.py` to group by stage
- [ ] Add stage capacity usage to roadmap output
- [ ] Include workflow progression indicators
- [ ] Update roadmap PDF export to show stages
- [ ] Update roadmap CSV export to include workflow_stage column

## 4. Backend - API Layer

### 4.1 API Schemas
- [ ] Update `BacklogItemCreate` schema to include workflow_stage
- [ ] Update `BacklogItemUpdate` schema for stage transitions
- [ ] Update `SystemSettingsUpdate` schema for capacity percentages
- [ ] Add validation for workflow stage transitions

### 4.2 API Endpoints
- [ ] Update `POST /items` to accept workflow_stage
- [ ] Update `PUT /items/{id}` to handle stage changes
- [ ] Add validation: prevent downstream without upstream completion
- [ ] Update `GET /items` to support filtering by workflow_stage
- [ ] Update `GET /settings` to return capacity percentages
- [ ] Update `PUT /settings` to validate capacity sum

### 4.3 Prioritization Endpoint
- [ ] Update `/priorizacoes` to handle multi-stage prioritization
- [ ] Return stage-specific results
- [ ] Include capacity usage per stage in response

## 5. Frontend - Components

### 5.1 BacklogBoard Component
- [ ] Add workflow stage badge to `BacklogItemCard.jsx`
- [ ] Implement color coding (Blue/Green/Orange)
- [ ] Add stage filter dropdown
- [ ] Show capacity allocation per stage
- [ ] Add visual capacity bars per stage
- [ ] Update item creation form to include workflow_stage selector

### 5.2 Settings Panel
- [ ] Add capacity allocation section to `SettingsPanel.jsx`
- [ ] Implement three percentage sliders (Upstream, Downstream, Sustentação)
- [ ] Add real-time validation (sum = 100%)
- [ ] Show visual feedback for invalid input
- [ ] Display current capacity distribution
- [ ] Add help text explaining each stage

### 5.3 Roadmap View
- [ ] Update `RoadmapView.jsx` to group items by stage
- [ ] Add collapsible sections per stage
- [ ] Show capacity usage per stage
- [ ] Add workflow progression indicator
- [ ] Update roadmap export to include stage information

### 5.4 Item Edit/Create Forms
- [ ] Add workflow_stage dropdown to item forms
- [ ] Add "Mark Upstream Complete" button
- [ ] Disable "Move to Downstream" if upstream not complete
- [ ] Show upstream completion date if set
- [ ] Add validation messages

## 6. Testing

### 6.1 Unit Tests
- [ ] Test capacity calculation logic
- [ ] Test capacity percentage validation
- [ ] Test workflow stage transitions
- [ ] Test multi-stage prioritization
- [ ] Test roadmap generation with stages
- [ ] Test API validation rules

### 6.2 Integration Tests
- [ ] Test full prioritization flow with multiple stages
- [ ] Test roadmap generation end-to-end
- [ ] Test settings update with capacity allocation
- [ ] Test item creation/update with workflow stages
- [ ] Test database migrations

### 6.3 Manual Testing
- [ ] Test UI workflow stage indicators
- [ ] Test capacity allocation sliders
- [ ] Test stage filtering
- [ ] Test roadmap stage grouping
- [ ] Test workflow transitions (Upstream → Downstream)
- [ ] Test validation messages

## 7. Documentation

### 7.1 Code Documentation
- [ ] Update API documentation with new fields
- [ ] Document workflow stage enum values
- [ ] Document capacity calculation logic
- [ ] Add inline comments for complex logic

### 7.2 User Documentation
- [ ] Create user guide for workflow stages
- [ ] Document capacity allocation feature
- [ ] Add examples of typical workflows
- [ ] Update README with new features

## 8. Deployment

### 8.1 Development Environment
- [ ] Run database migrations on dev
- [ ] Deploy backend changes to dev Lambda
- [ ] Deploy frontend changes to dev
- [ ] Test end-to-end on dev environment

### 8.2 Production Deployment
- [ ] Backup production database
- [ ] Run database migrations on production
- [ ] Deploy backend to production Lambda
- [ ] Deploy frontend to production
- [ ] Monitor for errors
- [ ] Run data backfill script if needed

## 9. Post-Deployment

### 9.1 Data Migration
- [ ] Analyze existing backlog items
- [ ] Assign workflow stages to existing items
- [ ] Verify data integrity
- [ ] Update roadmaps with new stage information

### 9.2 Monitoring
- [ ] Monitor CloudWatch logs for errors
- [ ] Check capacity calculation accuracy
- [ ] Verify prioritization results
- [ ] Collect user feedback

## 10. Cleanup
- [ ] Archive this change proposal
- [ ] Update capability specs
- [ ] Remove any temporary migration scripts
- [ ] Update CHANGELOG.md
