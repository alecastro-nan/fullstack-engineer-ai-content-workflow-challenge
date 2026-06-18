#!/usr/bin/env bash
set -euo pipefail

# Run a single task from feature_list.json
# Usage: ./agentic/run-task.sh F-001

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 TASK_ID (e.g., F-001)"
  exit 1
fi

RUN_DIR="agentic/runs/$TASK_ID"
mkdir -p "$RUN_DIR"

echo "=== Running $TASK_ID ==="
echo "Logging to $RUN_DIR/audit.log"
echo "Task: $TASK_ID" > "$RUN_DIR/audit.log"
echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$RUN_DIR/audit.log"
echo "" >> "$RUN_DIR/audit.log"

# Run the task (placeholder — actual execution depends on the task)
echo "Executing $TASK_ID..."
# Implement task-specific logic here

echo "Task $TASK_ID completed." | tee -a "$RUN_DIR/audit.log"
echo "Completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$RUN_DIR/audit.log"
