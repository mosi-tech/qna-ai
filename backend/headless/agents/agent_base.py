#!/usr/bin/env python3
"""
Agent Base Class

Provides common functionality for all headless agents:
- Standard input/output contracts
- Prompt file loading
- LLM service initialization
- Logging and error handling
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from pathlib import Path

# Add backend to path for imports
_BACKEND = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

from shared.llm import LLMService, create_llm_service, LLMConfig
from shared.llm.providers import create_provider


class AgentResult:
    """Standard result object for all agents"""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AgentBase(ABC):
    """
    Base class for all headless agents.

    Each agent must:
    1. Define its input schema
    2. Define its output schema
    3. Implement the process() method
    4. Optionally implement validation methods
    """

    def __init__(
        self,
        name: str,
        task: Optional[str] = None,  # Task name for LLMConfig.for_task()
        prompt_file: Optional[str] = None,
        llm_model: Optional[str] = None,  # Override model
        llm_provider: Optional[str] = None,  # Override provider
        **kwargs  # Allow subclasses to pass additional args
    ):
        self.name = name
        self.task = task
        self.default_timeout = kwargs.get('default_timeout', 60)

        # Setup logging
        self.logger = logging.getLogger(f"agent.{name}")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        self.logger.addHandler(handler)

        # Load prompt file
        self.prompt_file = prompt_file
        self.system_prompt = None
        if prompt_file:
            self._load_prompt(prompt_file)

        # Initialize LLM service (use task-based config, or explicit override)
        self.llm_service: Optional[LLMService] = None
        if task or llm_model or llm_provider:
            self._initialize_llm(llm_model, llm_provider, task)

        # Metrics
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_time_seconds": 0
        }

    def _load_prompt(self, prompt_file: str):
        """Load system prompt from file"""
        # Handle both absolute and relative paths
        if not os.path.isabs(prompt_file):
            # Try relative to shared/config/agents/
            config_dir = os.path.join(_BACKEND, "shared", "config", "agents")
            full_path = os.path.join(config_dir, prompt_file)
            if not os.path.exists(full_path):
                # Try relative to current directory
                full_path = os.path.join(os.path.dirname(__file__), prompt_file)
        else:
            full_path = prompt_file

        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
            self.logger.info(f"✅ Loaded prompt from {full_path} ({len(self.system_prompt)} chars)")
        else:
            self.logger.warning(f"⚠️ Prompt file not found: {full_path}")

    def _initialize_llm(self, model: Optional[str], provider: Optional[str], task: Optional[str] = None):
        """Initialize LLM service"""
        try:
            # Priority: explicit model/provider > task-based config > default
            if model or provider:
                # Use explicit model/provider
                provider_type = provider or "ollama"
                provider_upper = provider_type.upper()

                # Get base_url from environment
                base_url = os.getenv(f"OLLAMA_BASE_URL") or os.getenv(f"{provider_upper}_BASE_URL")

                config = LLMConfig(
                    provider_type=provider_type,
                    default_model=model or os.getenv("OLLAMA_MODEL", "glm-4.7:cloud"),
                    api_key=os.getenv("OLLAMA_API_KEY"),
                    base_url=base_url,
                    service_name=self.name
                )
            elif task:
                # Use task-based configuration (like original pipeline)
                config = LLMConfig.for_task(task)
                config.service_name = self.name
            else:
                # No task or explicit config provided
                raise Exception("Either 'task' or explicit 'llm_model'/'llm_provider' must be provided")

            self.llm_service = create_llm_service(config=config)
            self.logger.info(f"✅ LLM service initialized: {self.llm_service.config.provider_type}/{self.llm_service.config.default_model} (base_url: {self.llm_service.config.base_url})")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize LLM service: {e}")
            self.llm_service = None

    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected input"""
        pass

    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected output"""
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Main processing method.

        Args:
            input_data: Dictionary containing required input fields

        Returns:
            AgentResult with success status, data, and optional error
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Validate input data against schema.

        Returns:
            Error message if validation fails, None otherwise
        """
        try:
            schema = self.get_input_schema()
            required_fields = schema.get("required", [])

            for field in required_fields:
                if field not in input_data:
                    return f"Missing required field: {field}"

            return None
        except Exception as e:
            return f"Validation error: {e}"

    def validate_output(self, output_data: Any) -> Optional[str]:
        """
        Validate output data against schema.

        Returns:
            Error message if validation fails, None otherwise
        """
        try:
            schema = self.get_output_schema()
            if isinstance(output_data, dict):
                required_fields = schema.get("required", [])
                for field in required_fields:
                    if field not in output_data:
                        return f"Missing required output field: {field}"
            return None
        except Exception as e:
            return f"Output validation error: {e}"

    def execute(self, input_data: Any) -> AgentResult:
        """
        Execute agent with input validation and error handling.

        Args:
            input_data: Input (can be dict, JSON string, or file path)

        Returns:
            AgentResult
        """
        start_time = datetime.now()

        try:
            # Parse input if needed
            if isinstance(input_data, str):
                if input_data.startswith("{"):
                    input_data = json.loads(input_data)
                elif os.path.exists(input_data):
                    with open(input_data, 'r', encoding='utf-8') as f:
                        input_data = json.load(f)
                else:
                    input_data = {"question": input_data}

            # Validate input
            validation_error = self.validate_input(input_data)
            if validation_error:
                self.logger.error(f"❌ Input validation failed: {validation_error}")
                return AgentResult(success=False, error=validation_error)

            # Process
            self.logger.info(f"🚀 Executing {self.name} agent...")
            result = self.process(input_data)

            # Validate output
            if result.success:
                validation_error = self.validate_output(result.data)
                if validation_error:
                    self.logger.warning(f"⚠️ Output validation failed: {validation_error}")

            # Update metrics
            elapsed = (datetime.now() - start_time).total_seconds()
            self.metrics["total_calls"] += 1
            if result.success:
                self.metrics["successful_calls"] += 1
            else:
                self.metrics["failed_calls"] += 1
            self.metrics["total_time_seconds"] += elapsed

            self.logger.info(f"{'✅' if result.success else '❌'} Agent {self.name} completed in {elapsed:.2f}s")

            return result

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.metrics["total_calls"] += 1
            self.metrics["failed_calls"] += 1
            self.metrics["total_time_seconds"] += elapsed

            self.logger.error(f"❌ Agent {self.name} failed: {e}", exc_info=True)
            return AgentResult(success=False, error=str(e))

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_time = (
            self.metrics["total_time_seconds"] / self.metrics["total_calls"]
            if self.metrics["total_calls"] > 0
            else 0
        )
        return {
            **self.metrics,
            "avg_time_seconds": avg_time,
            "success_rate": (
                self.metrics["successful_calls"] / self.metrics["total_calls"]
                if self.metrics["total_calls"] > 0
                else 0
            )
        }

    def print_metrics(self):
        """Print performance metrics"""
        m = self.get_metrics()
        print(f"\n📊 {self.name} Agent Metrics:")
        print(f"  Total calls: {m['total_calls']}")
        print(f"  Success rate: {m['success_rate']:.1%}")
        print(f"  Avg time: {m['avg_time_seconds']:.2f}s")
        print(f"  Total time: {m['total_time_seconds']:.2f}s")
        print()

    def _make_llm_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Make LLM request with error handling"""
        if not self.llm_service:
            raise Exception("LLM service not initialized")

        prompt = system_prompt or self.system_prompt
        if not prompt:
            self.logger.warning("⚠️ No system prompt provided")

        try:
            # Use async make_request
            import asyncio
            response = asyncio.run(self.llm_service.make_request(
                messages=messages,
                system_prompt=prompt,
                tools=tools
            ))

            if not response.get("success"):
                raise Exception(response.get("error", "LLM request failed"))

            return response

        except Exception as e:
            self.logger.error(f"❌ LLM request failed: {e}")
            raise

    def _safe_parse_json(self, content: str) -> Any:
        """Safely parse JSON with fallbacks"""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try cleaning common issues
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            try:
                return json.loads(content)
            except:
                self.logger.error(f"❌ Failed to parse JSON: {e}")
                raise Exception(f"Invalid JSON response: {content[:200]}...")


def get_agent_class(agent_name: str) -> Optional[type]:
    """Import and return agent class by name"""
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    agent_file = os.path.join(agents_dir, f"{agent_name}_agent.py")

    if not os.path.exists(agent_file):
        return None

    try:
        # Dynamic import with absolute path
        import importlib.util
        spec = importlib.util.spec_from_file_location(agent_name, agent_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[agent_name] = module
        spec.loader.exec_module(module)

        # Find the agent class (Agent subclass)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, AgentBase) and
                attr is not AgentBase):
                return attr

        return None
    except Exception as e:
        logging.getLogger("agent_base").error(f"Failed to load agent {agent_name}: {e}")
        return None