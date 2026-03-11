import yfinance as yf
import pandas as pd

try:
    from curl_cffi import requests as curl_requests
    _SESSION = curl_requests.Session(impersonate="chrome")
except ImportError:
    _SESSION = None


def _ticker(symbol: str):
    """Crea un Ticker con sesión curl_cffi si está disponible."""
    if _SESSION is not None:
        return yf.Ticker(symbol, session=_SESSION)
    return yf.Ticker(symbol)


def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Descarga el histórico OHLCV de un ticker."""
    stock = _ticker(ticker)
    df = stock.history(period=period, interval=interval)
    if df.empty:
        return pd.DataFrame()
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)
    return df


def get_company_info(ticker: str) -> dict:
    """Devuelve la información básica de la empresa."""
    stock = _ticker(ticker)
    info = stock.info
    keys = [
        # Identificación
        "longName", "sector", "industry", "country",
        "currency", "exchange", "website", "longBusinessSummary",
        # Precio
        "marketCap", "currentPrice", "previousClose",
        "open", "dayHigh", "dayLow", "volume",
        "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
        # Valoración fundamental
        "trailingPE", "forwardPE", "priceToBook",
        "trailingPegRatio", "pegRatio",
        "priceToSalesTrailing12Months",
        # Rentabilidad y márgenes
        "returnOnEquity", "returnOnAssets", "profitMargins", "grossMargins",
        # Crecimiento
        "revenueGrowth", "earningsGrowth",
        # Salud financiera
        "debtToEquity", "currentRatio", "quickRatio",
        "totalCash", "totalDebt", "freeCashflow",
        # Dividendo
        "dividendYield", "payoutRatio",
    ]
    return {k: info.get(k) for k in keys}


def get_current_price(ticker: str) -> float | None:
    """Devuelve el precio actual del ticker."""
    info = get_company_info(ticker)
    return info.get("currentPrice")
