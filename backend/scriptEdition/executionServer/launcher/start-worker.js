#!/usr/bin/env node
/**
 * Unified Worker Launcher
 * 
 * Node.js script to start either analysis or execution workers with environment configuration.
 * Replaces start_analysis_worker.sh and start_queue_worker.sh with unified functionality.
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
 * Worker types and their configurations
 */
const WORKER_TYPES = {
    analysis: {
        name: 'Analysis Worker',
        description: 'Processes analysis requests asynchronously',
        defaultWorkerId: 'worker_analysis_server',
        defaultPollInterval: 5,
        defaultMaxConcurrent: 2
    },
    execution: {
        name: 'Execution Worker', 
        description: 'Processes script execution requests from queue',
        defaultWorkerId: (hostname, pid) => `worker_execution_${hostname}_${pid}`,
        defaultPollInterval: 5,
        defaultMaxConcurrent: 3
    }
};

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
 * Generate default worker ID
 */
function generateWorkerId(workerType) {
    const os = require('os');
    const hostname = os.hostname();
    const pid = process.pid;
    
    const config = WORKER_TYPES[workerType];
    if (typeof config.defaultWorkerId === 'function') {
        return config.defaultWorkerId(hostname, pid);
    }
    return config.defaultWorkerId;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
    const args = process.argv.slice(2);
    const options = {};
    
    // First argument should be worker type (if no flags)
    if (args.length > 0 && !args[0].startsWith('--')) {
        options.workerType = args[0];
        args.shift(); // Remove it from args
    }
    
    for (let i = 0; i < args.length; i += 2) {
        const flag = args[i];
        const value = args[i + 1];
        
        switch (flag) {
            case '--type':
            case '-t':
                options.workerType = value;
                break;
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
            case '--dry-run':
                options.dryRun = true;
                i--; // No value for this flag
                break;
            case '--help':
            case '-h':
                showHelp();
                process.exit(0);
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
Unified Worker Launcher

Usage: node start-worker.js [worker-type] [options]

Worker Types:
  analysis      Start analysis worker (processes analysis requests)
  execution     Start execution worker (processes script executions)

Options:
  -t, --type <type>        Worker type: analysis | execution
  --worker-id <id>         Worker ID (default: auto-generated)
  --poll-interval <secs>   Polling interval in seconds (default: 5)
  --max-concurrent <num>   Maximum concurrent jobs (default: varies by type)
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
  node start-worker.js analysis
  node start-worker.js execution --worker-id worker-1
  node start-worker.js --type analysis --poll-interval 10
  node start-worker.js execution --max-concurrent 5 --log-level DEBUG
  node start-worker.js analysis --dry-run

Worker Descriptions:
  analysis      ${WORKER_TYPES.analysis.description}
  execution     ${WORKER_TYPES.execution.description}
`);
}

/**
 * Validate worker type
 */
function validateWorkerType(workerType) {
    if (!workerType) {
        console.error('❌ Worker type is required. Use --type <type> or specify as first argument.');
        console.error('   Available types: analysis, execution');
        console.error('   Use --help for more information.');
        process.exit(1);
    }
    
    if (!WORKER_TYPES[workerType]) {
        console.error(`❌ Invalid worker type: ${workerType}`);
        console.error('   Available types: ' + Object.keys(WORKER_TYPES).join(', '));
        process.exit(1);
    }
}

/**
 * Set up Python path for shared modules
 */
function setupPythonPath() {
    const currentDir = process.cwd();
    const sharedPath = path.join(currentDir, '../../');
    const currentPythonPath = process.env.PYTHONPATH || '';
    
    if (currentPythonPath) {
        process.env.PYTHONPATH = `${currentPythonPath}:${sharedPath}`;
    } else {
        process.env.PYTHONPATH = sharedPath;
    }
    
    console.log(`📋 Python path: ${process.env.PYTHONPATH}`);
}

/**
 * Start the specified worker
 */
async function startWorker() {
    // Load environment variables
    loadEnvironment();
    
    // Parse command line arguments
    const cliOptions = parseArgs();
    
    // Validate worker type
    validateWorkerType(cliOptions.workerType);
    
    const workerConfig = WORKER_TYPES[cliOptions.workerType];
    
    // Set default environment variables with CLI overrides
    const config = {
        workerType: cliOptions.workerType,
        mongoUrl: getEnv('MONGO_URL', 'mongodb://localhost:27017'),
        dbName: getEnv('MONGO_DB_NAME', 'qna_ai_admin'),
        workerId: cliOptions.workerId || getEnv('WORKER_ID', generateWorkerId(cliOptions.workerType)),
        pollInterval: cliOptions.pollInterval || parseInt(getEnv('POLL_INTERVAL', workerConfig.defaultPollInterval.toString())),
        maxConcurrent: cliOptions.maxConcurrent || parseInt(getEnv('MAX_CONCURRENT', workerConfig.defaultMaxConcurrent.toString())),
        logLevel: cliOptions.logLevel || getEnv('LOG_LEVEL', 'INFO')
    };
    
    console.log(`🚀 Starting ${workerConfig.name}...`);
    console.log(`   Type: ${config.workerType}`);
    console.log(`   Worker ID: ${config.workerId}`);
    console.log(`   MongoDB URL: ${config.mongoUrl}`);
    console.log(`   Database: ${config.dbName}`);
    console.log(`   Poll Interval: ${config.pollInterval} seconds`);
    console.log(`   Max Concurrent: ${config.maxConcurrent}`);
    console.log(`   Log Level: ${config.logLevel}`);
    console.log(`   Description: ${workerConfig.description}`);
    console.log('');
    
    // Set up environment variables for the Python process
    const env = {
        ...process.env,
        MONGO_URL: config.mongoUrl,
        MONGO_DB_NAME: config.dbName,
        WORKER_ID: config.workerId,
        POLL_INTERVAL: config.pollInterval.toString(),
        MAX_CONCURRENT: config.maxConcurrent.toString(),
        LOG_LEVEL: config.logLevel
    };
    
    // Set up Python path
    setupPythonPath();
    
    // Determine Python executable
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    // Build Python command - now both workers use the same script
    const pythonArgs = [
        'queue_worker.py',
        '--type', config.workerType,
        '--worker-id', config.workerId,
        '--poll-interval', config.pollInterval.toString(),
        '--max-concurrent', config.maxConcurrent.toString(),
        '--log-level', config.logLevel
    ];
    
    // Both workers now use the same script in the parent directory
    const workingDir = path.join(process.cwd(), '..');
    
    console.log(`💻 Executing: ${pythonCmd} ${pythonArgs.join(' ')}`);
    console.log(`📋 Working directory: ${workingDir}`);
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
        cwd: workingDir
    });
    
    // Handle child process events
    child.on('error', (error) => {
        console.error(`❌ Failed to start ${workerConfig.name}: ${error.message}`);
        
        if (error.code === 'ENOENT') {
            console.error('💡 Make sure Python is installed and available in PATH');
            console.error('   Try: python3 --version or python --version');
        }
        
        process.exit(1);
    });
    
    child.on('close', (code, signal) => {
        if (signal) {
            console.log(`🛑 ${workerConfig.name} terminated by signal: ${signal}`);
        } else {
            console.log(`🛑 ${workerConfig.name} exited with code: ${code}`);
        }
        
        process.exit(code || 0);
    });
    
    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.log(`\\n🛑 Received SIGINT, shutting down ${workerConfig.name} gracefully...`);
        child.kill('SIGINT');
    });
    
    process.on('SIGTERM', () => {
        console.log(`\\n🛑 Received SIGTERM, shutting down ${workerConfig.name} gracefully...`);
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

module.exports = { startWorker, WORKER_TYPES };