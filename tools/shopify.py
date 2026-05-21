"""
Shopify tool - read orders, update inventory.
"""
import os
from tools.base import BaseTool
class ShopifyTool(BaseTool):
    name = "shopify"
    description = """Manage Shopify store.
    Actions: 'list_orders' (limit=10), 'list_products' (limit=10)"""
    category = "Finance"
    required_env_vars = ["SHOPIFY_SHOP_URL", "SHOPIFY_ACCESS_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("SHOPIFY_SHOP_URL") and os.getenv("SHOPIFY_ACCESS_TOKEN"))
    def _run(self, action: str, limit: int = 10, **kwargs) -> str:
        import httpx
        shop_url = os.getenv("SHOPIFY_SHOP_URL").rstrip("/")
        headers = {"X-Shopify-Access-Token": os.getenv("SHOPIFY_ACCESS_TOKEN")}
        if action == "list_orders":
            with httpx.Client() as client:
                data = client.get(f"{shop_url}/admin/api/2024-01/orders.json", headers=headers, params={"limit": limit}).json()
            orders = data.get("orders", [])
            return "Orders:\n" + "\n".join(f"- #{o['order_number']}: {o['total_price']} {o['currency']}" for o in orders)
        elif action == "list_products":
            with httpx.Client() as client:
                data = client.get(f"{shop_url}/admin/api/2024-01/products.json", headers=headers, params={"limit": limit}).json()
            products = data.get("products", [])
            return "Products:\n" + "\n".join(f"- {p['title']} (ID: {p['id']})" for p in products)
        return f"Error: Unknown action '{action}'"
