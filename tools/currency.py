"""
Currency exchange rates tool - Frankfurter API (FREE).
"""
import httpx
from tools.base import BaseTool
class CurrencyTool(BaseTool):
    name = "currency_fx"
    description = """Get live currency exchange rates. FREE - no API key required.
    Actions: 'convert' (amount, from_currency, to_currency), 'rates' (base='USD')"""
    category = "Finance"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        return True
    def _run(self, action: str = "rates", amount: float = None, from_currency: str = None, to_currency: str = None, base: str = "USD", **kwargs) -> str:
        if action == "convert":
            if not all([amount, from_currency, to_currency]):
                return "Error: 'convert' requires 'amount', 'from_currency', 'to_currency'"
            with httpx.Client() as client:
                data = client.get("https://api.frankfurter.app/latest", params={"from": from_currency.upper(), "to": to_currency.upper(), "amount": amount}).json()
            converted = data["rates"][to_currency.upper()]
            return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
        elif action == "rates":
            with httpx.Client() as client:
                data = client.get("https://api.frankfurter.app/latest", params={"from": base.upper()}).json()
            return f"Rates for {base.upper()} ({data['date']}):\n" + "\n".join(f"  {c}: {r:.4f}" for c, r in sorted(data["rates"].items()))
        return f"Error: Unknown action '{action}'"
