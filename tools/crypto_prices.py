"""
Crypto prices tool - CoinGecko API (FREE).
"""
import httpx
from tools.base import BaseTool
class CryptoPricesTool(BaseTool):
    name = "crypto_prices"
    description = """Get cryptocurrency prices from CoinGecko. FREE - no API key required.
    Actions: 'price' (coin), 'top' (limit=10), 'search' (query)
    Coin IDs: bitcoin, ethereum, solana, etc."""
    category = "Finance"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        return True
    def _run(self, action: str = "price", coin: str = None, query: str = None, limit: int = 10, **kwargs) -> str:
        if action == "price":
            if not coin:
                return "Error: 'price' requires 'coin'"
            with httpx.Client() as client:
                resp = client.get(f"https://api.coingecko.com/api/v3/coins/{coin.lower()}", params={"localization": "false", "tickers": "false"})
                if resp.status_code == 404:
                    return f"Coin '{coin}' not found."
                data = resp.json()
            market = data.get("market_data", {})
            price = market.get("current_price", {}).get("usd", 0)
            change = market.get("price_change_percentage_24h", 0)
            return f"{data.get('name')} ({data.get('symbol', '').upper()})\nPrice: ${price:,.2f}\n24h: {'+' if change >= 0 else ''}{change:.2f}%"
        elif action == "top":
            with httpx.Client() as client:
                resp = client.get("https://api.coingecko.com/api/v3/coins/markets", params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": min(limit, 50), "page": 1})
                data = resp.json()
            return "Top Cryptos:\n" + "\n".join(f"{c['market_cap_rank']}. {c['name']}: ${c['current_price']:,.2f}" for c in data)
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            with httpx.Client() as client:
                resp = client.get("https://api.coingecko.com/api/v3/search", params={"query": query})
                data = resp.json()
            coins = data.get("coins", [])[:10]
            return "Results:\n" + "\n".join(f"- {c['name']} ({c['symbol']}) ID: {c['id']}" for c in coins)
        return f"Error: Unknown action '{action}'"
