"""
Trello tool - create cards, move between lists.
"""
import os
from tools.base import BaseTool
class TrelloTool(BaseTool):
    name = "trello"
    description = """Manage Trello boards and cards.
    Actions: 'create_card' (list_id, name, desc), 'move_card' (card_id, list_id), 'list_boards' (), 'list_lists' (board_id)"""
    category = "Productivity"
    required_env_vars = ["TRELLO_API_KEY", "TRELLO_API_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("TRELLO_API_KEY") and os.getenv("TRELLO_API_TOKEN"))
    def _run(self, action: str, list_id: str = None, card_id: str = None, board_id: str = None, name: str = None, desc: str = None, **kwargs) -> str:
        from trello import TrelloClient
        client = TrelloClient(api_key=os.getenv("TRELLO_API_KEY"), token=os.getenv("TRELLO_API_TOKEN"))
        if action == "create_card":
            if not all([list_id, name]):
                return "Error: 'create_card' requires 'list_id' and 'name'"
            trello_list = client.get_list(list_id)
            card = trello_list.add_card(name=name, desc=desc or "")
            return f"Card created: {card.name} (ID: {card.id})"
        elif action == "list_boards":
            boards = client.list_boards()
            return "Boards:\n" + "\n".join(f"- {b.name} (ID: {b.id})" for b in boards)
        return f"Error: Unknown action '{action}'"
