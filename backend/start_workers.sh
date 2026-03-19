#!/bin/bash
# Start PM2 workers for dashboard pipeline
# Workers must be run from the backend directory

cd "$(dirname "$0")"

PYTHONPATH=. pm2 start -m shared.queue.analysis_worker --name analysis-queue-worker --interpreter python3 --merge-logs
PYTHONPATH=. pm2 start -m shared.queue.execution_worker --name execution-queue-worker --interpreter python3 --merge-logs

echo "Workers started. Use 'pm2 list' to check status."
echo "Use 'pm2 logs' to view logs."
echo "Use 'pm2 stop all' to stop workers."