# Headless Agents - Model Configuration

## Overview

Headless agents use task-based model configuration via environment variables, following the same pattern as the original pipeline.

## Environment Variables

### Task-Specific Model Configuration

Each agent can be configured independently using the pattern `{TASK}_LLM_MODEL`:

| Task | Environment Variable | Default Model |
|------|---------------------|---------------|
| UI_PLANNER | `UI_PLANNER_LLM_MODEL` | Provider default |
| QUESTION_ENHANCER | `QUESTION_ENHANCER_LLM_MODEL` | Provider default |
| REUSE_EVALUATOR | `REUSE_EVALUATOR_LLM_MODEL` | Provider default |
| CODE_PROMPT_BUILDER | `CODE_PROMPT_BUILDER_LLM_MODEL` | Provider default |
| CODE_SCRIPT_GENERATOR | `CODE_SCRIPT_GENERATOR_LLM_MODEL` | Provider default |
| SCRIPT_VALIDATOR | `SCRIPT_VALIDATOR_LLM_MODEL` | Provider default |
| SCRIPT_EXECUTOR | `SCRIPT_EXECUTOR_LLM_MODEL` | Provider default |

### Verification Models

Verification uses multiple models configured via:

```bash
VERIFICATION_LLM_MODEL_1="glm-4.7:cloud"
VERIFICATION_LLM_MODEL_2="gpt-oss:120b"
VERIFICATION_LLM_MODEL_3="..."  # Optional third model
```

Defaults (if not configured):
- Model 1: `glm-4.7:cloud`
- Model 2: `gpt-oss:120b`

### Provider Configuration

For each model, you can also specify the provider:

```bash
# Provider-specific (applies to all models from that provider)
OLLAMA_BASE_URL="https://ollama.com/api"

# Provider for a specific task
{TASK}_LLM_PROVIDER="ollama"

# API key (for cloud providers)
OLLAMA_API_KEY="your-api-key"
```

## Configuration Examples

### Using Different Models for Different Tasks

```bash
# Fast model for planning
UI_PLANNER_LLM_MODEL="glm-4.7:cloud"

# Better model for code generation
CODE_SCRIPT_GENERATOR_LLM_MODEL="gpt-oss:120b"

# Lightweight model for validation
SCRIPT_VALIDATOR_LLM_MODEL="haiku"
```

### Using Different Providers

```bash
# Use Ollama Cloud for most tasks
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="https://ollama.com/api"
OLLAMA_API_KEY="your-key"

# Use OpenAI for code generation
CODE_SCRIPT_GENERATOR_LLM_PROVIDER="openai"
OPENAI_API_KEY="your-openai-key"
```

### Configuring Verification

```bash
# Two-model verification (default)
VERIFICATION_LLM_MODEL_1="glm-4.7:cloud"
VERIFICATION_LLM_MODEL_2="gpt-oss:120b"

# Three-model verification for higher confidence
VERIFICATION_LLM_MODEL_1="glm-4.7:cloud"
VERIFICATION_LLM_MODEL_2="gpt-oss:120b"
VERIFICATION_LLM_MODEL_3="claude-3-5-sonnet"

# All same model (single-model verification)
VERIFICATION_LLM_MODEL_1="glm-4.7:cloud"
VERIFICATION_LLM_MODEL_2="glm-4.7:cloud"
```

## Testing Your Configuration

Test specific agent model configuration:

```bash
# Test UI Planner
python headless/agents/run_single_agent.py ui_planner \
    --input '{"question": "Show QQQ ETF price"}'

# Test Code Script Generator
python headless/agents/run_single_agent.py code_script_generator \
    --input '{"enriched_prompt": "...", "question": "...", "selected_functions": []}'
```

## .env File Example

Create a `.env` file in `backend/`:

```bash
# Default provider
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://ollama.com/api
OLLAMA_API_KEY=your-key

# Task-specific models
UI_PLANNER_LLM_MODEL=glm-4.7:cloud
CODE_SCRIPT_GENERATOR_LLM_MODEL=gpt-oss:120b
CODE_PROMPT_BUILDER_LLM_MODEL=glm-4.7:cloud

# Verification models
VERIFICATION_LLM_MODEL_1=glm-4.7:cloud
VERIFICATION_LLM_MODEL_2=gpt-oss:120b
```

## Model Selection Guidelines

| Task | Recommended Model | Reason |
|------|------------------|--------|
| ui_planner | glm-4.7:cloud | Fast, good at structured output |
| question_enhancer | glm-4.7:cloud | Good at understanding and expanding queries |
| reuse_evaluator | glm-4.7:cloud | Lightweight, deterministic decisions |
| code_prompt_builder | glm-4.7:cloud | Good at function selection |
| code_script_generator | gpt-oss:120b | Better at code generation |
| script_validator | glm-4.7:cloud | Fast AST-based validation |
| verification | glm-4.7:cloud + gpt-oss:120b | Multi-model for consensus |
| script_executor | N/A | No LLM needed |

## Temperature Defaults

Each task has temperature defaults (from LLMConfig):

| Task | Temperature | Purpose |
|------|-------------|---------|
| ANALYSIS | 0.2 | Slight creativity for insights |
| CODE_PROMPT_BUILDER | 0.1 | Deterministic function selection |
| REUSE_EVALUATOR | 0.1 | Consistent decision making |
| CONTEXT | 0.1 | More deterministic |
| Default | 0.1 | Most tasks are deterministic |

Override via env:
```bash
{TASK}_LLM_TEMPERATURE=0.3
```