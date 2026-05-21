"""
Stripe tool - list charges, create payment links, check balance.
"""
import os
from tools.base import BaseTool
class StripeTool(BaseTool):
    name = "stripe"
    description = """Manage Stripe payments.
    Actions: 'balance' (), 'list_charges' (limit=10), 'create_payment_link' (amount, currency, description)"""
    category = "Finance"
    required_env_vars = ["STRIPE_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("STRIPE_API_KEY"))
    def _run(self, action: str, limit: int = 10, amount: int = None, currency: str = "usd", description: str = None, **kwargs) -> str:
        import stripe
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        if action == "balance":
            balance = stripe.Balance.retrieve()
            return "Balance:\n" + "\n".join(f"  {b.currency.upper()}: {b.amount / 100:.2f}" for b in balance.available)
        elif action == "list_charges":
            charges = stripe.Charge.list(limit=limit)
            return "Charges:\n" + "\n".join(f"- {c.amount / 100:.2f} {c.currency.upper()} - {c.status}" for c in charges.data)
        elif action == "create_payment_link":
            if not amount:
                return "Error: 'create_payment_link' requires 'amount' (in cents)"
            product = stripe.Product.create(name=description or "Payment")
            price = stripe.Price.create(unit_amount=amount, currency=currency, product=product.id)
            link = stripe.PaymentLink.create(line_items=[{"price": price.id, "quantity": 1}])
            return f"Payment link: {link.url}"
        return f"Error: Unknown action '{action}'"
