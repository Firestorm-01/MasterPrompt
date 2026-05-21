"""
Tool registry - auto-discovers and manages all available tools.
"""
import importlib
import os
import pkgutil
from pathlib import Path
from typing import Optional
from langchain.tools import BaseTool as LangChainBaseTool
from tools.base import BaseTool
class ToolRegistry:
    """
    Automatically discovers and registers all tools.
    Filters tools based on credential availability.
    """
    
    def __init__(self):
        self.all_tools: list[BaseTool] = []
        self.available_tools: list[BaseTool] = []
        self._discover_tools()
    
    def _discover_tools(self):
        """Auto-discover all tool modules in the tools directory."""
        tools_dir = Path(__file__).parent
        
        # Import all modules in tools directory
        for module_info in pkgutil.iter_modules([str(tools_dir)]):
            if module_info.name in ("base", "registry", "__init__"):
                continue
            
            try:
                module = importlib.import_module(f"tools.{module_info.name}")
                
                # Find tool classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) and
                        issubclass(attr, BaseTool) and
                        attr is not BaseTool and
                        hasattr(attr, "name")
                    ):
                        try:
                            tool_instance = attr()
                            self.all_tools.append(tool_instance)
                            
                            if tool_instance.is_available():
                                self.available_tools.append(tool_instance)
                        except Exception as e:
                            # Skip tools that fail to instantiate
                            print(f"Warning: Could not instantiate {attr_name}: {e}")
            except Exception as e:
                print(f"Warning: Could not import tools.{module_info.name}: {e}")
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Get a specific tool by name."""
        for tool in self.available_tools:
            if tool.name == name:
                return tool
        return None
    
    def get_langchain_tools(self) -> list[LangChainBaseTool]:
        """Get all available tools as LangChain tools."""
        return [tool.to_langchain_tool() for tool in self.available_tools]
    
    def get_tools_by_category(self) -> dict[str, list[BaseTool]]:
        """Group all tools by category."""
        categories: dict[str, list[BaseTool]] = {}
        
        for tool in self.all_tools:
            category = getattr(tool, "category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)
        
        return categories
    
    def get_tool_info(self) -> list[dict]:
        """Get information about all tools for the frontend."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": getattr(tool, "category", "Other"),
                "is_available": tool.is_available(),
                "required_env_vars": getattr(tool, "required_env_vars", []),
                "is_free": getattr(tool, "is_free", False)
            }
            for tool in self.all_tools
        ]
