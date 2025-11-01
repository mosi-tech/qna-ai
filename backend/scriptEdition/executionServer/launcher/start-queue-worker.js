#!/usr/bin/env node
/**
 * Queue Worker Launcher
 * 
 * Node.js script to start the MongoDB queue worker with environment configuration.
 * Replaces start_queue_worker.sh with better cross-platform support and .env handling.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Load dotenv for .env file support (if available)
try {
    require('dotenv').config();
} catch (error) {
    // dotenv not available, will load .env manually
}

/**
 * Load and parse .env file manually for better error handling
 */
function loadEnvironment() {
    const envPath = path.join(process.cwd(), '.env');
    
    if (fs.existsSync(envPath)) {
        console.log('📝 Loading environment variables from .env file...');
        try {
            const envContent = fs.readFileSync(envPath, 'utf8');
            const lines = envContent.split('\n');
            
            lines.forEach(line => {
                const trimmed = line.trim();
                if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
                    const [key, ...valueParts] = trimmed.split('=');
                    const value = valueParts.join('='); // Handle values with = in them
                    if (key && value !== undefined) {
                        process.env[key.trim()] = value.trim().replace(/^["']|["']$/g, ''); // Remove quotes
                    }
                }
            });
        } catch (error) {
            console.warn(`⚠️  Failed to parse .env file: ${error.message}`);
        }
    } else {
        console.log('ℹ️  No .env file found, using system environment variables');
    }
}

/**
 * Get environment variable with default fallback
 */
function getEnv(key, defaultValue) {
    return process.env[key] || defaultValue;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);
    const options = {};
    
    for (let i = 0; i < args.length; i += 2) {
        const flag = args[i];
        const value = args[i + 1];
        
        switch (flag) {
            case '--worker-id':
                options.workerId = value;
                break;
            case '--poll-interval':
                options.pollInterval = parseInt(value);
                break;
            case '--max-concurrent':
                options.maxConcurrent = parseInt(value);
                break;
            case '--log-level':
                options.logLevel = value;
                break;
            case '--help':
            case '-h':
                showHelp();
                process.exit(0);
            case '--dry-run':
                options.dryRun = true;
                break;
            default:
                if (flag && flag.startsWith('--')) {
                    console.warn(`⚠️  Unknown option: ${flag}`);
                }
        }
    }
    
    return options;
}

/**
 * Show help message
 */
function showHelp() {
    console.log(`
Queue Worker Launcher

Usage: node start-queue-worker.js [options]

Options:
  --worker-id <id>         Worker ID (default: worker_<hostname>_<pid>)
  --poll-interval <secs>   Polling interval in seconds (default: 5)
  --max-concurrent <num>   Maximum concurrent executions (default: 3)
  --log-level <level>      Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
  --dry-run                Show configuration without starting worker
  --help, -h               Show this help message

Environment Variables:
  MONGO_URL               MongoDB connection URL (default: mongodb://localhost:27017)
  MONGO_DB_NAME          MongoDB database name (default: qna_ai_admin)
  WORKER_ID              Worker ID override
  POLL_INTERVAL          Poll interval override
  MAX_CONCURRENT         Max concurrent override
  LOG_LEVEL              Log level override

Examples:
  node start-queue-worker.js
  node start-queue-worker.js --worker-id worker-1 --poll-interval 10
  node start-queue-worker.js --max-concurrent 5 --log-level DEBUG
`);
}

/**
 * Generate default worker ID
 */
function generateWorkerId() {
    const os = require('os');
    const hostname = os.hostname();
    const pid = process.pid;
    return `worker_${hostname}_${pid}`;
}

/**
 * Start the Python queue worker
 */
async function startWorker() {
    // Load environment variables
    loadEnvironment();
    
    // Parse command line arguments
    const cliOptions = parseArgs();
    
    // Set default environment variables with CLI overrides
    const config = {
        mongoUrl: getEnv('MONGO_URL', 'mongodb://localhost:27017'),
        dbName: getEnv('MONGO_DB_NAME', 'qna_ai_admin'),
        workerId: cliOptions.workerId || getEnv('WORKER_ID', generateWorkerId()),
        pollInterval: cliOptions.pollInterval || parseInt(getEnv('POLL_INTERVAL', '5')),
        maxConcurrent: cliOptions.maxConcurrent || parseInt(getEnv('MAX_CONCURRENT', '3')),
        logLevel: cliOptions.logLevel || getEnv('LOG_LEVEL', 'INFO')
    };
    
    console.log('🚀 Starting Queue Worker with configuration:');
    console.log(`   Worker ID: ${config.workerId}`);
    console.log(`   MongoDB URL: ${config.mongoUrl}`);
    console.log(`   Database: ${config.dbName}`);
    console.log(`   Poll Interval: ${config.pollInterval} seconds`);
    console.log(`   Max Concurrent: ${config.maxConcurrent}`);
    console.log(`   Log Level: ${config.logLevel}`);
    console.log('');
    
    // Set environment variables for the Python process
    const env = {
        ...process.env,
        MONGO_URL: config.mongoUrl,
        MONGO_DB_NAME: config.dbName,
        WORKER_ID: config.workerId,
        POLL_INTERVAL: config.pollInterval.toString(),
        MAX_CONCURRENT: config.maxConcurrent.toString(),
        LOG_LEVEL: config.logLevel
    };
    
    // Determine Python executable
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    // Build Python command arguments
    const pythonArgs = [
        'queue_worker.py',
        '--worker-id', config.workerId,
        '--poll-interval', config.pollInterval.toString(),
        '--max-concurrent', config.maxConcurrent.toString(),
        '--log-level', config.logLevel
    ];
    
    console.log(`💻 Executing: ${pythonCmd} ${pythonArgs.join(' ')}`);
    console.log('');
    
    // If dry run, exit after showing configuration
    if (cliOptions.dryRun) {
        console.log('🔍 Dry run mode - configuration shown above, not starting worker');
        process.exit(0);
    }
    
    // Spawn the Python process
    const child = spawn(pythonCmd, pythonArgs, {
        stdio: 'inherit', // Pass through stdin, stdout, stderr
        env: env,
        cwd: process.cwd()
    });
    
    // Handle child process events
    child.on('error', (error) => {
        console.error(`❌ Failed to start worker: ${error.message}`);
        
        if (error.code === 'ENOENT') {
            console.error('💡 Make sure Python is installed and available in PATH');
            console.error('   Try: python3 --version or python --version');
        }
        
        process.exit(1);
    });
    
    child.on('close', (code, signal) => {
        if (signal) {
            console.log(`🛑 Worker terminated by signal: ${signal}`);
        } else {
            console.log(`🛑 Worker exited with code: ${code}`);
        }
        
        process.exit(code || 0);
    });
    
    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.log('\n🛑 Received SIGINT, shutting down gracefully...');
        child.kill('SIGINT');
    });
    
    process.on('SIGTERM', () => {
        console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
        child.kill('SIGTERM');
    });
    
    // Keep the process alive
    process.stdin.resume();
}

// Run the worker if this script is executed directly
if (require.main === module) {
    startWorker().catch(error => {
        console.error(`❌ Worker startup failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { startWorker };