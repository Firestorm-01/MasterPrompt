"""
Code interpreter tool - execute Python in E2B sandbox.
"""
import os
from tools.base import BaseTool
class CodeInterpreterTool(BaseTool):
    name = "code_interpreter"
    description = """Execute Python code in a secure sandbox and return results.
    Parameters: code (Python code to execute)"""
    category = "AI & Dev"
    required_env_vars = ["E2B_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("E2B_API_KEY"))
    def _run(self, code: str, **kwargs) -> str:
        from e2b_code_interpreter import CodeInterpreter
        with CodeInterpreter(api_key=os.getenv("E2B_API_KEY")) as sandbox:
            execution = sandbox.notebook.exec_cell(code)
        output = []
        if execution.logs.stdout:
            output.append("STDOUT:\n" + "\n".join(execution.logs.stdout))
        if execution.logs.stderr:
            output.append("STDERR:\n" + "\n".join(execution.logs.stderr))
        if execution.error:
            output.append(f"ERROR: {execution.error.name}: {execution.error.value}")
        return "\n\n".join(output) if output else "Code executed (no output)"
