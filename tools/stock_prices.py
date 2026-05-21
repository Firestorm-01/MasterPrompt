"""
Stock prices tool - real-time and historical data via yfinance (FREE).
"""
from tools.base import BaseTool
class StockPricesTool(BaseTool):
    name = "stock_prices"
    description = """Get stock market data using Yahoo Finance. FREE - no API key required.
    Actions: 'quote' (symbol), 'history' (symbol, period='1mo'), 'info' (symbol)
    Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y"""
    category = "Finance"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import yfinance
            return True
        except ImportError:
            return False
    def _run(self, symbol: str, action: str = "quote", period: str = "1mo", **kwargs) -> str:
        import yfinance as yf
        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)
        if action == "quote":
            info = ticker.info
            price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
            name = info.get("shortName", symbol)
            change_pct = info.get("regularMarketChangePercent", 0)
            sign = "+" if change_pct >= 0 else ""
            return f"{symbol} ({name})\nPrice: ${price}\nChange: {sign}{change_pct:.2f}%\nMarket Cap: ${info.get('marketCap', 0):,.0f}"
        elif action == "history":
            hist = ticker.history(period=period)
            if hist.empty:
                return f"No historical data for {symbol}"
            output = [f"History for {symbol} ({period}):"]
            for date, row in hist.tail(10).iterrows():
                output.append(f"{date.strftime('%Y-%m-%d')}: ${row['Close']:.2f}")
            return "\n".join(output)
        elif action == "info":
            info = ticker.info
            return f"{symbol} - {info.get('shortName', 'N/A')}\nSector: {info.get('sector', 'N/A')}\nIndustry: {info.get('industry', 'N/A')}"
        return f"Error: Unknown action '{action}'"
