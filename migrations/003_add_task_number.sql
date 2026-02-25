-- ============================================================
-- Add task_number column (recyclable identifier)
-- Numbers are assigned 1-N on active tasks.
-- When archived, task_number is set to NULL, freeing it for reuse.
-- ============================================================

BEGIN;

-- 1. Add the column (nullable, since archived tasks won't have one)
ALTER TABLE task ADD COLUMN task_number SMALLINT;

-- 2. Assign sequential numbers to all non-archived tasks
WITH numbered AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS rn
  FROM task
  WHERE archived_at IS NULL
)
UPDATE task SET task_number = numbered.rn
FROM numbered WHERE task.id = numbered.id;

-- 3. Ensure no two active tasks share a number
CREATE UNIQUE INDEX idx_task_number_active
  ON task (task_number)
  WHERE task_number IS NOT NULL;

COMMIT;
