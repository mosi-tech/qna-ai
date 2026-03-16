#!/usr/bin/env python3
"""
Script Validator Agent

Validates Python scripts for syntax, structure, and code quality.

Input:
    {
        "script": "#!/usr/bin/env python3\n..."
    }

Output:
    {
        "valid": true,
        "syntax_valid": true,
        "structure_valid": true,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "summary": "Script is valid"
    }
"""

import ast
import json
from typing import Dict, Any, List, Optional

from agent_base import AgentBase, AgentResult


class ScriptValidatorAgent(AgentBase):
    """Agent that validates Python scripts"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/script_validator.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="script_validator",
            task="SCRIPT_VALIDATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {"type": "string", "description": "Python script to validate"}
            },
            "required": ["script"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"},
                "syntax_valid": {"type": "boolean"},
                "structure_valid": {"type": "boolean"},
                "mcp_calls_valid": {"type": "boolean"},
                "errors": {"type": "array"},
                "warnings": {"type": "array"},
                "suggestions": {"type": "array"},
                "summary": {"type": "string"}
            },
            "required": ["valid", "summary"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Validate the Python script"""
        script = input_data.get("script", "")

        if not script:
            return AgentResult(
                success=False,
                error="Script content is empty"
            )

        errors = []
        warnings = []
        suggestions = []

        # 1. Syntax validation
        syntax_valid, syntax_errors = self._validate_syntax(script)
        errors.extend(syntax_errors)

        # 2. Structure validation
        structure_valid, structure_warnings = self._validate_structure(script)
        warnings.extend(structure_warnings)

        # 3. Import validation
        import_valid, import_warnings = self._validate_imports(script)
        warnings.extend(import_warnings)

        # 4. Function validation
        function_valid, function_errors, function_warnings = self._validate_functions(script)
        errors.extend(function_errors)
        warnings.extend(function_warnings)

        # 5. MCP function validation
        mcp_valid, mcp_warnings = self._validate_mcp_calls(script)
        warnings.extend(mcp_warnings)

        # 6. Code quality checks
        quality_warnings = self._validate_code_quality(script)
        warnings.extend(quality_warnings)

        # Determine overall validity
        valid = syntax_valid and structure_valid and function_valid and len(errors) == 0

        # Generate summary
        if valid:
            summary = "Script is valid and ready for execution"
            if warnings:
                summary += f" (with {len(warnings)} warning{'s' if len(warnings) != 1 else ''})"
        else:
            summary = f"Script has {len(errors)} critical error{'s' if len(errors) != 1 else ''} that must be fixed"

        result_data = {
            "valid": valid,
            "syntax_valid": syntax_valid,
            "structure_valid": structure_valid,
            "mcp_calls_valid": mcp_valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "summary": summary
        }

        self.logger.info(f"✅ Validation complete: {'VALID' if valid else 'INVALID'} ({len(errors)} errors, {len(warnings)} warnings)")

        return AgentResult(success=True, data=result_data)

    def _validate_syntax(self, script: str) -> tuple[bool, List[str]]:
        """Validate Python syntax using AST parsing"""
        errors = []

        try:
            ast.parse(script)
            return True, errors
        except SyntaxError as e:
            errors.append(f"Syntax error: {e.msg} at line {e.lineno}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected syntax error: {str(e)}")
            return False, errors

    def _validate_structure(self, script: str) -> tuple[bool, List[str]]:
        """Validate script structure"""
        warnings = []

        # Check for shebang
        lines = script.split('\n')
        if not lines[0].startswith('#!/usr/bin/env python3'):
            warnings.append("Missing shebang line - script should start with '#!/usr/bin/env python3'")

        # Check for docstring
        has_docstring = False
        for i, line in enumerate(lines[1:20], 1):
            if '"""' in line or "'''" in line:
                has_docstring = True
                break

        if not has_docstring:
            warnings.append("Missing docstring - script should have a descriptive docstring after the shebang")

        # Check for main guard
        if '__main__' not in script:
            warnings.append("Missing if __name__ == '__main__' block for CLI support")

        return True, warnings

    def _validate_imports(self, script: str) -> tuple[bool, List[str]]:
        """Validate imports"""
        warnings = []

        try:
            tree = ast.parse(script)

            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    imports.add(module.split('.')[0])

            # Check for required imports
            required = {'json', 'pandas', 'datetime', 'typing'}
            for req in required:
                if req not in imports:
                    # pandas is usually imported as pd
                    if req != 'pandas' or 'pd' not in script:
                        warnings.append(f"Missing recommended import: {req}")

            # Check for undefined imports
            known_imports = {
                'json', 'pandas', 'pd', 'datetime', 'timedelta',
                'typing', 'Dict', 'Any', 'List', 'Optional',
                'argparse', 'os', 'sys', 'math', 're'
            }

            for imp in imports:
                if imp not in known_imports and not imp.startswith('shared'):
                    # Could be an external library, check if it's valid
                    pass

            return True, warnings

        except SyntaxError:
            return False, []

    def _validate_functions(self, script: str) -> tuple[bool, List[str], List[str]]:
        """Validate function definitions"""
        errors = []
        warnings = []

        try:
            tree = ast.parse(script)

            has_analyze_question = False
            has_main = False

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for analyze_question function
                    if node.name == 'analyze_question':
                        has_analyze_question = True
                        # Check for type hints
                        has_type_hints = any(
                            arg.annotation is not None
                            for arg in node.args.args
                        )
                        if not has_type_hints:
                            warnings.append("analyze_question() missing type hints for parameters")

                        # Check for docstring
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            warnings.append("analyze_question() missing docstring")

                    # Check for main function
                    if node.name == 'main':
                        has_main = True
                        # Check for **kwargs
                        has_kwargs = any(
                            arg.arg == 'kwargs' and arg.kind == ast.arg.VAR_KEYWORD
                            for arg in node.args.args + node.args.kwonlyargs + node.args.kw_defaults
                        )
                        # Look for **kwargs in the arguments
                        has_kwargs = has_kwargs or any(
                            arg.kind == ast.arg.VAR_KEYWORD
                            for arg in node.args.args + node.args.kwonlyargs
                        )
                        if not has_kwargs:
                            warnings.append("main() should accept **kwargs for HTTP execution")

            if not has_analyze_question:
                errors.append("Missing required function: analyze_question()")

            if not has_main:
                warnings.append("Missing recommended function: main() for HTTP execution")

            return (len(errors) == 0, errors, warnings)

        except SyntaxError:
            return False, [], []

    def _validate_mcp_calls(self, script: str) -> tuple[bool, List[str]]:
        """Validate MCP function calls"""
        warnings = []

        # Known MCP function names (from mcp-financial-server and mcp-analytics-server)
        known_mcp_functions = {
            # Financial data functions
            'get_historical_data', 'get_real_time_data', 'get_latest_quotes',
            'get_latest_trades', 'get_most_active_stocks', 'get_top_gainers',
            'get_top_losers', 'get_market_news', 'get_fundamentals',
            'get_dividends', 'get_splits', 'get_account', 'get_positions',
            'get_position', 'get_orders', 'get_portfolio_history',
            'get_market_clock', 'get_technical_indicator', 'search_symbols',
            'get_exchanges_list', 'get_exchange_symbols', 'get_custom_screener',
            # Analytics functions
            'L2_reg', 'align_series', 'analyze_leverage_fund',
            'analyze_monthly_performance', 'analyze_portfolio_concentration',
            'analyze_portfolio_turnover', 'analyze_returns_symmetry',
            'analyze_seasonality', 'analyze_signal_quality',
            'analyze_volatility_clustering', 'analyze_weekday_performance',
            'backtest_strategy', 'black_scholes_option_price',
            'calculate_active_share', 'calculate_ad', 'calculate_adosc',
            'calculate_adx', 'calculate_adxr', 'calculate_annualized_return',
            'calculate_annualized_volatility', 'calculate_aroon',
            'calculate_aroon_oscillator', 'calculate_atr', 'calculate_benchmark_metrics',
            'calculate_beta', 'calculate_beta_analysis', 'calculate_bollinger_bands',
            # ... and more
        }

        # Look for call_mcp_function calls and check function names
        lines = script.split('\n')
        for i, line in enumerate(lines):
            if 'call_mcp_function(' in line:
                # Extract the function name being called
                import re
                match = re.search(r'call_mcp_function\(\s*[\'"]([^\'"]+)[\'"]', line)
                if match:
                    func_name = match.group(1)
                    # Check if it looks like a valid MCP function
                    if '__' not in func_name:
                        warnings.append(
                            f"Line {i+1}: MCP function name '{func_name}' "
                            f"should use format 'category__function_name' (e.g., 'financial_data__get_historical_data')"
                        )

        return True, warnings

    def _validate_code_quality(self, script: str) -> List[str]:
        """Validate code quality"""
        warnings = []

        lines = script.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for bare except clauses
            if 'except:' in stripped and 'except ' not in stripped:
                warnings.append(f"Line {i}: Bare except clause - should specify exception type")

            # Check for print statements (should use json.dumps for output)
            if stripped.startswith('print(') and 'json.dumps' not in line:
                # Allow print for debugging/error messages, but not for data output
                if not any(x in line for x in ['error', 'Error', 'warning', 'Warning', 'debug', 'Debug']):
                    warnings.append(f"Line {i}: Print statement for data output - should use json.dumps")

            # Check for hardcoded ticker symbols that should be parameters
            hardcoded_symbols = ["'QQQ'", '"QQQ"', "'SPY'", '"SPY"', "'AAPL'", '"AAPL"']
            for symbol in hardcoded_symbols:
                if symbol in stripped and '=' in stripped and 'def ' not in stripped:
                    # This might be a default value in a function definition, which is OK
                    if 'def ' not in ''.join(lines[max(0, i-5):i]):
                        warnings.append(f"Line {i}: Hardcoded value {symbol} should be a parameter")

        return warnings


# Factory function for easy creation
def create_script_validator_agent(**kwargs) -> ScriptValidatorAgent:
    """Create Script Validator agent with optional overrides"""
    return ScriptValidatorAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        script_path = sys.argv[1]

        try:
            with open(script_path, 'r') as f:
                script_content = f.read()

            agent = ScriptValidatorAgent()
            result = agent.execute({"script": script_content})
            print(json.dumps(result.to_dict(), indent=2))
        except FileNotFoundError:
            print(f"Error: File not found: {script_path}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python script_validator_agent.py /path/to/script.py")