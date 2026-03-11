import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Descarga el histórico OHLCV de un ticker."""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    if df.empty:
        return pd.DataFrame()
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)
    return df


def get_company_info(ticker: str) -> dict:
    """Devuelve la información básica de la empresa."""
    stock = yf.Ticker(ticker)
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
