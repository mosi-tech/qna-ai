# Queue Worker Launcher

Simple shell scripts to start analysis and execution workers using `.env` configuration.

## Usage

```bash
# Start analysis worker
./start-analysis-worker.sh

# Start execution worker  
./start-execution-worker.sh

# Pass additional arguments (override .env settings)
./start-analysis-worker.sh --max-retries 5 --retry-delay 120
./start-execution-worker.sh --log-level DEBUG
```

## Configuration

Edit `.env` file in this directory to configure workers:

```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=qna_ai_admin

# Analysis Worker Configuration  
ANALYSIS_WORKER_ID=worker_analysis_server
ANALYSIS_POLL_INTERVAL=5
ANALYSIS_MAX_CONCURRENT=2
ANALYSIS_WORKER_MAX_RETRIES=0

# Execution Worker Configuration
EXECUTION_WORKER_ID=worker_execution_server
EXECUTION_POLL_INTERVAL=5
EXECUTION_MAX_CONCURRENT=3
EXECUTION_WORKER_MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
```

## Environment Variable Mapping

The Python worker uses these environment variables:

- `ANALYSIS_WORKER_POLL_INTERVAL` → `ANALYSIS_POLL_INTERVAL`
- `ANALYSIS_WORKER_MAX_CONCURRENT` → `ANALYSIS_MAX_CONCURRENT`
- `ANALYSIS_WORKER_MAX_RETRIES` → `ANALYSIS_WORKER_MAX_RETRIES`
- `ANALYSIS_WORKER_ID` → `ANALYSIS_WORKER_ID`

Command line arguments always override `.env` settings.