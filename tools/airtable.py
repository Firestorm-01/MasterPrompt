"""
Airtable tool - read/write records.
"""
import os
from tools.base import BaseTool
class AirtableTool(BaseTool):
    name = "airtable"
    description = """Read and write Airtable records.
    Actions: 'list' (base_id, table_name), 'create' (base_id, table_name, fields), 'update' (base_id, table_name, record_id, fields)"""
    category = "Productivity"
    required_env_vars = ["AIRTABLE_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("AIRTABLE_API_KEY"))
    def _run(self, action: str, base_id: str = None, table_name: str = None, record_id: str = None, fields: dict = None, **kwargs) -> str:
        from pyairtable import Table
        api_key = os.getenv("AIRTABLE_API_KEY")
        if action == "list":
            if not all([base_id, table_name]):
                return "Error: 'list' requires 'base_id' and 'table_name'"
            table = Table(api_key, base_id, table_name)
            records = table.all(max_records=20)
            return "Records:\n" + "\n".join(f"- {r['id']}: {list(r['fields'].values())[:2]}" for r in records)
        elif action == "create":
            if not all([base_id, table_name, fields]):
                return "Error: 'create' requires 'base_id', 'table_name', and 'fields'"
            table = Table(api_key, base_id, table_name)
            record = table.create(fields)
            return f"Record created with ID: {record['id']}"
        return f"Error: Unknown action '{action}'"
