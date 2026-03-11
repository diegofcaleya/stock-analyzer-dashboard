def get_valuation(info: dict) -> dict:
    """
    Calcula métricas de valoración fundamental y emite un veredicto.
    Retorna un dict con ratios, benchmarks y etiqueta.
    """
    pe = info.get("trailingPE") or info.get("forwardPE")
    pb = info.get("priceToBook")
    peg = info.get("trailingPegRatio") or info.get("pegRatio")
    ps = info.get("priceToSalesTrailing12Months")
    roe = info.get("returnOnEquity")
    profit_margin = info.get("profitMargins")
    debt_equity = info.get("debtToEquity")
    current_ratio = info.get("currentRatio")
    revenue_growth = info.get("revenueGrowth")
    earnings_growth = info.get("earningsGrowth")

    metrics = {
        "P/E (trailing)": (info.get("trailingPE"), "< 25 razonable"),
        "P/E (forward)":  (info.get("forwardPE"),  "< 20 atractivo"),
        "P/B":            (pb,                      "< 3 razonable"),
        "PEG":            (peg,                     "< 1 infravalorado"),
        "P/S":            (ps,                      "< 5 razonable"),
        "ROE":            (f"{roe*100:.1f}%" if roe else None, "> 15 % bueno"),
        "Margen neto":    (f"{profit_margin*100:.1f}%" if profit_margin else None, "> 10 % bueno"),
        "Deuda/Equity":   (f"{debt_equity:.1f}" if debt_equity else None, "< 100 conservador"),
        "Ratio corriente":(current_ratio, "> 1.5 saludable"),
        "Crec. ingresos": (f"{revenue_growth*100:.1f}%" if revenue_growth else None, "> 10 % bueno"),
        "Crec. beneficio":(f"{earnings_growth*100:.1f}%" if earnings_growth else None, "> 10 % bueno"),
    }

    # --- Puntuación de valoración ---
    score = 0
    reasons = []

    if pe is not None:
        if pe < 15:
            score += 2; reasons.append(("P/E", f"{pe:.1f}", "Barato", "+2"))
        elif pe < 25:
            score += 1; reasons.append(("P/E", f"{pe:.1f}", "Razonable", "+1"))
        elif pe < 40:
            score -= 1; reasons.append(("P/E", f"{pe:.1f}", "Caro", "-1"))
        else:
            score -= 2; reasons.append(("P/E", f"{pe:.1f}", "Muy caro", "-2"))

    if pb is not None:
        if pb < 1:
            score += 2; reasons.append(("P/B", f"{pb:.2f}", "Bajo valor en libros", "+2"))
        elif pb < 3:
            score += 1; reasons.append(("P/B", f"{pb:.2f}", "Razonable", "+1"))
        elif pb < 6:
            score -= 1; reasons.append(("P/B", f"{pb:.2f}", "Elevado", "-1"))
        else:
            score -= 2; reasons.append(("P/B", f"{pb:.2f}", "Muy elevado", "-2"))

    if peg is not None:
        if peg < 1:
            score += 2; reasons.append(("PEG", f"{peg:.2f}", "Infravalorado vs crecimiento", "+2"))
        elif peg < 2:
            score += 1; reasons.append(("PEG", f"{peg:.2f}", "Justo precio", "+1"))
        else:
            score -= 1; reasons.append(("PEG", f"{peg:.2f}", "Sobrevaluado vs crecimiento", "-1"))

    if roe is not None:
        if roe > 0.20:
            score += 1; reasons.append(("ROE", f"{roe*100:.1f}%", "Alta rentabilidad", "+1"))
        elif roe < 0:
            score -= 1; reasons.append(("ROE", f"{roe*100:.1f}%", "Rentabilidad negativa", "-1"))

    if profit_margin is not None:
        if profit_margin > 0.15:
            score += 1; reasons.append(("Margen neto", f"{profit_margin*100:.1f}%", "Margen saludable", "+1"))
        elif profit_margin < 0:
            score -= 1; reasons.append(("Margen neto", f"{profit_margin*100:.1f}%", "Pérdidas", "-1"))

    # --- Veredicto ---
    if score >= 4:
        verdict = "INFRAVALORADA"
        color = "green"
    elif score >= 1:
        verdict = "PRECIO JUSTO"
        color = "blue"
    elif score >= -1:
        verdict = "NEUTRA"
        color = "gray"
    elif score >= -3:
        verdict = "SOBREVALUADA"
        color = "orange"
    else:
        verdict = "MUY SOBREVALUADA"
        color = "red"

    return {
        "metrics": metrics,
        "score": score,
        "verdict": verdict,
        "color": color,
        "reasons": reasons,
    }
