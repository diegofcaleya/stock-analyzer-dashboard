import os
from datetime import datetime, timedelta, timezone
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def _sentiment_label(compound: float) -> tuple[str, str]:
    """Convierte el score compuesto de VADER en etiqueta y color."""
    if compound >= 0.05:
        return "Positivo", "green"
    if compound <= -0.05:
        return "Negativo", "red"
    return "Neutro", "gray"


def get_news(query: str, days: int = 7, max_articles: int = 10) -> list[dict]:
    """
    Busca noticias relacionadas con `query` usando NewsAPI
    y añade análisis de sentimiento VADER a cada artículo.
    Requiere NEWSAPI_KEY en variables de entorno o .env.
    """
    api_key = os.getenv("NEWSAPI_KEY", "")
    if not api_key:
        return []

    client = NewsApiClient(api_key=api_key)
    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        response = client.get_everything(
            q=query,
            from_param=from_date,
            language="en",
            sort_by="publishedAt",
            page_size=max_articles,
        )
    except Exception:
        return []

    articles = response.get("articles", [])
    results = []

    for art in articles:
        title = art.get("title") or ""
        description = art.get("description") or ""
        text = f"{title}. {description}"

        scores = _analyzer.polarity_scores(text)
        compound = scores["compound"]
        label, color = _sentiment_label(compound)

        results.append({
            "title": title,
            "description": description,
            "url": art.get("url", ""),
            "source": art.get("source", {}).get("name", ""),
            "published_at": art.get("publishedAt", "")[:10],
            "compound": compound,
            "sentiment": label,
            "sentiment_color": color,
        })

    return results


def aggregate_sentiment(articles: list[dict]) -> dict:
    """Resumen del sentimiento agregado de una lista de artículos."""
    if not articles:
        return {"label": "Sin datos", "color": "gray", "avg": 0.0, "pos": 0, "neu": 0, "neg": 0}

    compounds = [a["compound"] for a in articles]
    avg = sum(compounds) / len(compounds)
    label, color = _sentiment_label(avg)

    pos = sum(1 for c in compounds if c >= 0.05)
    neu = sum(1 for c in compounds if -0.05 < c < 0.05)
    neg = sum(1 for c in compounds if c <= -0.05)

    return {"label": label, "color": color, "avg": avg, "pos": pos, "neu": neu, "neg": neg}
