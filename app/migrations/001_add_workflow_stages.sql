-- Migration: Add Upstream/Downstream Workflow Support
-- Date: 2025-12-18
-- Description: Adds workflow_stage and upstream_completed_at to backlog_items,
--              adds capacity allocation percentages to system_settings

-- ============================================================================
-- BACKLOG ITEMS TABLE
-- ============================================================================

-- Add workflow stage column (default to 'upstream' for existing items)
ALTER TABLE backlog_items 
ADD COLUMN workflow_stage TEXT DEFAULT 'upstream';

-- Add upstream completion timestamp
ALTER TABLE backlog_items 
ADD COLUMN upstream_completed_at TIMESTAMP NULL;

-- Create index for performance (filtering by workflow_stage)
CREATE INDEX IF NOT EXISTS idx_workflow_stage 
ON backlog_items(workflow_stage);

-- ============================================================================
-- SYSTEM SETTINGS TABLE
-- ============================================================================

-- Add capacity allocation percentages (default: 40% upstream, 40% downstream, 20% sustentacao)
ALTER TABLE system_settings
ADD COLUMN capacity_upstream_percent REAL DEFAULT 40.0;

ALTER TABLE system_settings
ADD COLUMN capacity_downstream_percent REAL DEFAULT 40.0;

ALTER TABLE system_settings
ADD COLUMN capacity_sustentacao_percent REAL DEFAULT 20.0;

-- ============================================================================
-- ROADMAPS TABLE (if exists)
-- ============================================================================

-- Add capacity allocation snapshot to roadmaps
ALTER TABLE roadmaps
ADD COLUMN capacity_upstream_percent REAL DEFAULT 40.0;

ALTER TABLE roadmaps
ADD COLUMN capacity_downstream_percent REAL DEFAULT 40.0;

ALTER TABLE roadmaps
ADD COLUMN capacity_sustentacao_percent REAL DEFAULT 20.0;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify backlog_items schema
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='backlog_items';

-- Check existing items have default workflow_stage
-- SELECT id, titulo, workflow_stage, upstream_completed_at FROM backlog_items LIMIT 10;

-- Verify system_settings schema
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='system_settings';

-- Check capacity allocation defaults
-- SELECT capacity_upstream_percent, capacity_downstream_percent, capacity_sustentacao_percent FROM system_settings;

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- Note: SQLite doesn't support DROP COLUMN directly
-- To rollback, you would need to:
-- 1. Create new tables without the new columns
-- 2. Copy data from old tables
-- 3. Drop old tables
-- 4. Rename new tables

-- For safety, always backup database before running migration:
-- cp backlog.db backlog.db.backup_YYYYMMDD
