#!/usr/bin/env python3
"""
Verification Agent

Multi-model verification of generated Python scripts.

Input:
    {
        "question": "Show QQQ ETF price",
        "script": "#!/usr/bin/env python3\n...",
        "context": {...}
    }

Output:
    {
        "approved": true,
        "confidence": 0.92,
        "issues": [],
        "model_votes": {"glm-4.7:cloud": "approve", "gpt-oss:120b": "approve"}
    }
"""

import os
import json
from typing import Dict, Any, List, Optional

from agent_base import AgentBase, AgentResult


class VerificationAgent(AgentBase):
    """Agent that verifies generated scripts"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/verification-prompt.txt",
        llm_model: str = None,  # Not used (multi-model verification)
        llm_provider: str = None  # Not used (multi-model verification)
    ):
        super().__init__(
            name="verification",
            task="VERIFICATION",  # Use task-based config
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

        # Load verification models from environment variables
        self.verification_models = self._load_verification_models()

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"},
                "script": {"type": "string", "description": "Python script to verify"},
                "context": {"type": "object", "description": "Additional context"}
            },
            "required": ["question", "script"]
        }

    def _load_verification_models(self) -> List[str]:
        """Load verification models from environment variables"""
        # Format: VERIFICATION_LLM_MODEL_1, VERIFICATION_LLM_MODEL_2, ...
        # or use defaults
        models = []
        for i in range(1, 10):  # Support up to 9 verification models
            model_key = f"VERIFICATION_LLM_MODEL_{i}"
            model = os.getenv(model_key)
            if model:
                models.append(model.strip())
                self.logger.info(f"✅ Loaded verification model {i}: {model}")

        # If no models configured, use defaults
        if not models:
            models = ["glm-4.7:cloud", "gpt-oss:120b"]
            self.logger.info("🔧 Using default verification models: glm-4.7:cloud, gpt-oss:120b")

        return models

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "approved": {"type": "boolean"},
                "confidence": {"type": "number"},
                "issues": {"type": "array"},
                "suggestions": {"type": "array"},
                "model_votes": {"type": "object"}
            },
            "required": ["approved", "confidence"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Verify the script using multiple models"""
        question = input_data.get("question", "")
        script = input_data.get("script", "")
        context = input_data.get("context", {})

        if not question or not script:
            return AgentResult(
                success=False,
                error="Missing required input: question or script"
            )

        # Build verification prompt
        verification_prompt = self._build_verification_prompt(question, script, context)

        # Collect votes from multiple models
        model_votes = {}
        all_issues = []
        all_suggestions = []
        total_confidence = 0
        vote_count = 0

        for model_name in self.verification_models:
            try:
                self.logger.info(f"🔍 Verifying with model: {model_name}")

                # Make LLM request with specific model
                # Temporarily change the model for this request
                original_model = self.llm_service.config.default_model
                self.llm_service.config.default_model = model_name

                response = self._make_llm_request(
                    messages=[{"role": "user", "content": verification_prompt}]
                )

                # Restore original model
                self.llm_service.config.default_model = original_model

                content = response.get("content", "").strip()
                result = self._safe_parse_json(content)

                # Map verification prompt format to agent format
                # Prompt returns: verdict, critical_issues, reasoning
                # Agent expects: approved, confidence, issues
                verdict = result.get("verdict", "REJECT").upper()
                approved = verdict == "APPROVE"
                confidence = result.get("confidence", 0.5)
                vote = "approve" if approved else "reject"
                model_votes[model_name] = vote

                # Collect issues and suggestions
                critical_issues = result.get("critical_issues", [])
                reasoning = result.get("reasoning", "")

                if approved:
                    all_suggestions.append(reasoning)
                else:
                    all_issues.extend(critical_issues)
                    if reasoning:
                        all_issues.append(reasoning)

                total_confidence += confidence
                vote_count += 1

                self.logger.info(f"✅ {model_name}: {vote} (confidence: {confidence:.2f})")

            except Exception as e:
                self.logger.warning(f"⚠️  Verification failed for {model_name}: {e}")
                # Record failed vote as reject
                model_votes[model_name] = "reject"

        # Calculate final decision
        approve_votes = sum(1 for v in model_votes.values() if v == "approve")
        total_votes = len(model_votes)

        # Approve if majority approve AND at least 2 votes
        final_approved = approve_votes >= max(1, total_votes // 2 + 1) if total_votes > 1 else approve_votes > 0
        avg_confidence = total_confidence / vote_count if vote_count > 0 else 0.5

        result_data = {
            "approved": final_approved,
            "confidence": avg_confidence,
            "issues": all_issues,
            "suggestions": all_suggestions,
            "model_votes": model_votes,
            "vote_summary": f"{approve_votes}/{total_votes} approved"
        }

        self.logger.info(f"✅ Final verification: {'APPROVED' if final_approved else 'REJECTED'} ({result_data['vote_summary']})")

        return AgentResult(success=True, data=result_data)

    def _build_verification_prompt(self, question: str, script: str, context: Dict) -> str:
        """Build verification prompt"""
        # Truncate script if too long
        script_preview = script
        if len(script) > 10000:
            script_preview = script[:10000] + "\n\n... [script truncated] ..."

        context_section = ""
        if context:
            context_section = f"CONTEXT:\n{json.dumps(context, indent=2)}\n\n"

        verification_prompt = f"""USER QUESTION:
{question}

{context_section}GENERATED SCRIPT:
```python
{script_preview}
```

TASK: Verify that this script correctly addresses the user's question and will produce accurate results.

Please check:
1. Does the script correctly understand and address the user's question?
2. Are MCP functions being used correctly?
3. Is data handling appropriate?
4. Are calculations accurate?
5. Are edge cases handled?
6. Will the output be in the correct format?

Return your verification decision in the exact JSON format specified in the system prompt.
"""

        return verification_prompt


# Factory function for easy creation
def create_verification_agent(**kwargs) -> VerificationAgent:
    """Create Verification agent with optional overrides"""
    return VerificationAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = VerificationAgent()

        # Mock script for testing
        mock_script = '''#!/usr/bin/env python3
"""
Q: Show QQQ ETF current price
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

def analyze_question(symbol: str = "QQQ", period_days: int = 252) -> Dict[str, Any]:
    """Main analysis function"""
    result = call_mcp_function(
        "financial_data__get_historical_data",
        {
            "symbols": symbol,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "timeframe": "1Day"
        }
    )

    if not result.get("success"):
        return {"error": "Failed to fetch data", "success": False}

    bars = result["data"].get(symbol, [])
    if not bars:
        return {"error": f"No data for {symbol}", "success": False}

    df = pd.DataFrame(bars)
    return {"current_price": df["close"].iloc[-1], "success": True}

def main(**kwargs):
    symbol = kwargs.get("symbol", "QQQ")
    return analyze_question(symbol=symbol)

if __name__ == "__main__":
    print(json.dumps(analyze_question(), indent=2))
'''

        result = agent.execute({
            "question": question,
            "script": mock_script,
            "context": {}
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python verification_agent.py \"Your question here\"")