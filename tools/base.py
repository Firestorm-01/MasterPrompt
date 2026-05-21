"""
Base tool class that all tools must extend.
Provides standard interface for availability checking and safe execution.
"""
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Type
from langchain.tools import BaseTool as LangChainBaseTool
from langchain.tools import StructuredTool
from pydantic import BaseModel, create_model
import inspect


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.

    Each tool must implement:
    - name: Unique tool identifier
    - description: Clear description for the LLM
    - category: Tool category string
    - required_env_vars: List of required environment variables
    - _run(**kwargs) -> str: The actual tool implementation
    - is_available() -> bool: Check if required credentials are present
    """

    name: ClassVar[str]
    description: ClassVar[str]
    category: ClassVar[str]
    required_env_vars: ClassVar[list[str]]
    is_free: ClassVar[bool] = False

    @abstractmethod
    def _run(self, **kwargs) -> str:
        """Execute the tool. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the tool has all required credentials configured."""
        pass

    def safe_run(self, args: dict) -> str:
        """
        Safely execute the tool with error handling and retries.
        Returns tool output or a descriptive error message.
        """
        if not self.is_available():
            return f"Tool '{self.name}' is not available. Missing required credentials: {', '.join(self.required_env_vars)}"

        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                result = self._run(**args)
                return result
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue

        return f"Tool '{self.name}' failed after {max_retries} attempts. Last error: {last_error}"

    def _build_input_model(self) -> Type[BaseModel]:
        """
        Dynamically build a Pydantic input model from _run's signature.
        This gives the LLM a proper structured schema for tool calling.
        """
        sig = inspect.signature(self._run)
        fields = {}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "kwargs"):
                continue

            annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
            
            # Normalise Optional types
            if annotation is None:
                annotation = Any

            if param.default != inspect.Parameter.empty:
                fields[param_name] = (annotation, param.default)
            else:
                fields[param_name] = (annotation, ...)

        if not fields:
            fields["input"] = (str, "")

        return create_model(f"{self.name}_input", **fields)

    def to_langchain_tool(self) -> LangChainBaseTool:
        """
        Convert to a LangChain StructuredTool with a proper input schema.
        StructuredTool accepts keyword arguments and validates them against
        the Pydantic model, which is required for reliable tool calling.
        """
        tool_instance = self
        input_model = self._build_input_model()

        def run_func(**kwargs) -> str:
            return tool_instance.safe_run(kwargs)

        return StructuredTool(
            name=self.name,
            description=self.description,
            func=run_func,
            args_schema=input_model,
        )

    def get_input_schema(self) -> dict:
        """Return JSON schema for tool inputs."""
        return self._build_input_model().model_json_schema()
