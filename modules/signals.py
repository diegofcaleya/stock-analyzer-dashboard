import pandas as pd


def generate_signal(df: pd.DataFrame) -> dict:
    """
    Genera señal BUY / SELL / HOLD basada en RSI, MACD y Bandas de Bollinger.
    Retorna un dict con la señal, puntuación y detalle de cada regla.
    """
    if df.empty or len(df) < 2:
        return {"signal": "HOLD", "score": 0, "details": []}

    last = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    details = []

    # --- RSI ---
    rsi = last.get("RSI")
    if pd.notna(rsi):
        if rsi < 30:
            score += 2
            details.append(("RSI", f"{rsi:.1f}", "Sobrevendido — bullish", "+2"))
        elif rsi < 45:
            score += 1
            details.append(("RSI", f"{rsi:.1f}", "Zona baja", "+1"))
        elif rsi > 70:
            score -= 2
            details.append(("RSI", f"{rsi:.1f}", "Sobrecomprado — bearish", "-2"))
        elif rsi > 55:
            score -= 1
            details.append(("RSI", f"{rsi:.1f}", "Zona alta", "-1"))
        else:
            details.append(("RSI", f"{rsi:.1f}", "Neutro", "0"))

    # --- MACD cruce ---
    macd, macd_sig = last.get("MACD"), last.get("MACD_signal")
    prev_macd, prev_sig = prev.get("MACD"), prev.get("MACD_signal")
    if all(pd.notna(v) for v in [macd, macd_sig, prev_macd, prev_sig]):
        if prev_macd < prev_sig and macd > macd_sig:
            score += 2
            details.append(("MACD", f"{macd:.3f}", "Cruce alcista", "+2"))
        elif prev_macd > prev_sig and macd < macd_sig:
            score -= 2
            details.append(("MACD", f"{macd:.3f}", "Cruce bajista", "-2"))
        elif macd > macd_sig:
            score += 1
            details.append(("MACD", f"{macd:.3f}", "Por encima de señal", "+1"))
        else:
            score -= 1
            details.append(("MACD", f"{macd:.3f}", "Por debajo de señal", "-1"))

    # --- Bollinger Bands ---
    close = last.get("Close")
    bb_upper = last.get("BB_upper")
    bb_lower = last.get("BB_lower")
    bb_mid = last.get("BB_middle")
    if all(pd.notna(v) for v in [close, bb_upper, bb_lower, bb_mid]):
        if close < bb_lower:
            score += 2
            details.append(("Bollinger", f"{close:.2f}", "Precio bajo banda inferior", "+2"))
        elif close > bb_upper:
            score -= 2
            details.append(("Bollinger", f"{close:.2f}", "Precio sobre banda superior", "-2"))
        elif close < bb_mid:
            score += 1
            details.append(("Bollinger", f"{close:.2f}", "Bajo media central", "+1"))
        else:
            score -= 1
            details.append(("Bollinger", f"{close:.2f}", "Sobre media central", "-1"))

    # --- SMA 20/50 cruce ---
    sma20, sma50 = last.get("SMA_20"), last.get("SMA_50")
    prev_sma20, prev_sma50 = prev.get("SMA_20"), prev.get("SMA_50")
    if all(pd.notna(v) for v in [sma20, sma50, prev_sma20, prev_sma50]):
        if prev_sma20 < prev_sma50 and sma20 > sma50:
            score += 2
            details.append(("SMA 20/50", f"{sma20:.2f}/{sma50:.2f}", "Golden Cross", "+2"))
        elif prev_sma20 > prev_sma50 and sma20 < sma50:
            score -= 2
            details.append(("SMA 20/50", f"{sma20:.2f}/{sma50:.2f}", "Death Cross", "-2"))
        elif sma20 > sma50:
            score += 1
            details.append(("SMA 20/50", f"{sma20:.2f}/{sma50:.2f}", "Tendencia alcista", "+1"))
        else:
            score -= 1
            details.append(("SMA 20/50", f"{sma20:.2f}/{sma50:.2f}", "Tendencia bajista", "-1"))

    # --- Señal final ---
    if score >= 4:
        signal = "BUY"
    elif score <= -4:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {"signal": signal, "score": score, "details": details}
