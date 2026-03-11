import pandas as pd
import numpy as np


def add_moving_averages(df: pd.DataFrame, windows: list[int] = [20, 50, 200]) -> pd.DataFrame:
    for w in windows:
        df[f"SMA_{w}"] = df["Close"].rolling(window=w).mean()
    return df


def add_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    sma = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()
    df["BB_upper"] = sma + num_std * std
    df["BB_middle"] = sma
    df["BB_lower"] = sma - num_std * std
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]
    return df


def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = add_moving_averages(df)
    df = add_bollinger_bands(df)
    df = add_rsi(df)
    df = add_macd(df)
    return df
