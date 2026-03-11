import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.data import get_stock_data, get_company_info
from modules.indicators import compute_all
from modules.signals import generate_signal
from modules.valuation import get_valuation
from modules.news import get_news, aggregate_sentiment
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

st.set_page_config(
    page_title="Stock Analyzer Dashboard",
    page_icon="📈",
    layout="wide",
)

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0e1117; }
[data-testid="stSidebar"]          { background: #161b22; border-right: 1px solid #30363d; }
[data-testid="stAppViewContainer"] > .main > div:first-child { padding-top: 1rem; }

[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px;
}

.badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
}
.badge-buy    { background: #0d2b1e; color: #26a69a; border: 1px solid #26a69a; }
.badge-sell   { background: #2b0d0d; color: #ef5350; border: 1px solid #ef5350; }
.badge-hold   { background: #2b2000; color: #f0c040; border: 1px solid #f0c040; }
.badge-green  { background: #0d2b1e; color: #26a69a; border: 1px solid #26a69a; }
.badge-blue   { background: #0d1b2b; color: #4fc3f7; border: 1px solid #4fc3f7; }
.badge-gray   { background: #1e1e1e; color: #9e9e9e; border: 1px solid #9e9e9e; }
.badge-orange { background: #2b1800; color: #ffa726; border: 1px solid #ffa726; }
.badge-red    { background: #2b0d0d; color: #ef5350; border: 1px solid #ef5350; }

.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 8px 0;
    border-bottom: 1px solid #30363d;
    padding-bottom: 6px;
}

.news-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.news-card:hover { border-color: #58a6ff; }

.sent-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Stock Analyzer")
    st.markdown("<div style='color:#8b949e;font-size:0.8rem;margin-bottom:1.2rem'>Análisis técnico · fundamental · sentimiento</div>", unsafe_allow_html=True)

    ticker   = st.text_input("Ticker", value="AAPL", placeholder="AAPL, MSFT, TSLA…").upper().strip()
    period   = st.selectbox("Período",   ["1mo","3mo","6mo","1y","2y","5y"], index=2)
    interval = st.selectbox("Intervalo", ["1d","1wk","1mo"], index=0)

    st.markdown("---")
    st.markdown("<p class='section-title'>Indicadores</p>", unsafe_allow_html=True)
    show_sma = st.multiselect("Medias móviles", [20, 50, 200], default=[20, 50])
    show_bb  = st.checkbox("Bollinger Bands", value=True)

    st.markdown("---")
    st.markdown("<p class='section-title'>Noticias</p>", unsafe_allow_html=True)
    news_days = st.slider("Últimos N días", 1, 30, 7)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.button("Analizar", use_container_width=True, type="primary")

# ── Carga de datos ────────────────────────────────────────────────────────────
if not ticker:
    st.stop()

with st.spinner(f"Cargando {ticker}…"):
    df_raw = get_stock_data(ticker, period=period, interval=interval)
    info   = get_company_info(ticker)

if df_raw.empty:
    st.error(f"No se encontraron datos para **{ticker}**.")
    st.stop()

df     = compute_all(df_raw)
result = generate_signal(df)
val    = get_valuation(info)

current    = info.get("currentPrice") or df["Close"].iloc[-1]
prev_close = info.get("previousClose") or df["Close"].iloc[-2]
change     = current - prev_close
change_pct = (change / prev_close) * 100
currency   = info.get("currency", "")
name       = info.get("longName") or ticker

# ── Header ────────────────────────────────────────────────────────────────────
signal    = result["signal"]
score     = result["score"]
sig_class = {"BUY": "badge-buy", "SELL": "badge-sell", "HOLD": "badge-hold"}[signal]
sig_icon  = {"BUY": "▲", "SELL": "▼", "HOLD": "●"}[signal]

verdict        = val["verdict"]
verdict_colors = {
    "INFRAVALORADA":    ("badge-green",  "🟢"),
    "PRECIO JUSTO":     ("badge-blue",   "🔵"),
    "NEUTRA":           ("badge-gray",   "⚪"),
    "SOBREVALUADA":     ("badge-orange", "🟠"),
    "MUY SOBREVALUADA": ("badge-red",    "🔴"),
}
verd_class, verd_icon = verdict_colors.get(verdict, ("badge-gray", "⚪"))

h_left, h_right = st.columns([4, 2])
with h_left:
    tag_line = " · ".join(filter(None, [info.get("sector",""), info.get("industry","")]))
    st.markdown(f"## {name} &nbsp;<span style='font-size:1rem;color:#8b949e'>{ticker}</span>", unsafe_allow_html=True)
    if tag_line:
        st.markdown(f"<div style='color:#8b949e;margin-top:-10px;margin-bottom:6px'>{tag_line}</div>", unsafe_allow_html=True)
with h_right:
    st.markdown(
        f"<div style='text-align:right;padding-top:8px'>"
        f"<span class='badge {sig_class}' style='font-size:1rem;padding:8px 22px'>"
        f"{sig_icon} {signal} &nbsp;<span style='font-weight:400;font-size:0.8rem'>({score:+d} pts)</span></span>"
        f"&nbsp;&nbsp;"
        f"<span class='badge {verd_class}'>{verd_icon} {verdict}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Precio",   f"{current:.2f} {currency}", f"{change:+.2f} ({change_pct:+.2f}%)")
m2.metric("Apertura", f"{info.get('open') or 'N/A'}")
m3.metric("Máx. día", f"{info.get('dayHigh') or 'N/A'}")
m4.metric("Mín. día", f"{info.get('dayLow') or 'N/A'}")
m5.metric("52w High", f"{info.get('fiftyTwoWeekHigh') or 'N/A'}")
m6.metric("52w Low",  f"{info.get('fiftyTwoWeekLow') or 'N/A'}")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Dos columnas principales ──────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("<p class='section-title'>Análisis técnico</p>", unsafe_allow_html=True)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20],
        vertical_spacing=0.03,
        subplot_titles=(f"{ticker} · {period}", "MACD", "RSI"),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]],
    )

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Precio",
        increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
    ), row=1, col=1, secondary_y=False)

    vol_colors = ["#26a69a" if c >= o else "#ef5350" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], name="Volumen",
        marker_color=vol_colors, opacity=0.35,
    ), row=1, col=1, secondary_y=True)

    ma_colors = {20: "#f0c040", 50: "#4fc3f7", 200: "#ce93d8"}
    for w in show_sma:
        if f"SMA_{w}" in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[f"SMA_{w}"], name=f"SMA {w}",
                line=dict(color=ma_colors.get(w, "white"), width=1.2),
            ), row=1, col=1)

    if show_bb and "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_upper"], name="BB+",
            line=dict(color="rgba(173,216,230,0.5)", width=1, dash="dot"), showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_lower"], name="BB−",
            line=dict(color="rgba(173,216,230,0.5)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(173,216,230,0.04)", showlegend=False,
        ), row=1, col=1)

    macd_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["MACD_hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="Histograma",
                         marker_color=macd_colors, opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                             line=dict(color="#4fc3f7", width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Señal",
                             line=dict(color="#f48fb1", width=1.5)), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#f0c040", width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,83,80,0.5)",  row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(38,166,154,0.5)", row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(255,255,255,0.02)", line_width=0, row=3, col=1)

    fig.update_layout(
        height=660, template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(t=40, b=10, l=10, r=10),
    )
    fig.update_yaxes(showgrid=False, showticklabels=False, row=1, col=1, secondary_y=True)
    fig.update_yaxes(gridcolor="#1e2530", row=1, col=1, secondary_y=False)
    fig.update_yaxes(gridcolor="#1e2530", row=2, col=1)
    fig.update_yaxes(gridcolor="#1e2530", row=3, col=1)
    fig.update_xaxes(gridcolor="#1e2530", showspikes=True, spikecolor="#444", spikethickness=1)

    st.plotly_chart(fig, use_container_width=True)

with col_right:

    # Señal técnica
    st.markdown("<p class='section-title'>Señal técnica</p>", unsafe_allow_html=True)
    with st.container(border=True):
        sig_color = "#26a69a" if signal == "BUY" else "#ef5350" if signal == "SELL" else "#f0c040"
        pct = min(max((score + 8) / 16 * 100, 0), 100)
        st.markdown(
            f"<div style='text-align:center;padding:16px 0 8px'>"
            f"<div style='font-size:2.8rem;font-weight:800;color:{sig_color}'>{sig_icon} {signal}</div>"
            f"<div style='color:#8b949e;margin-top:4px'>Score: <b style='color:#cdd9e5'>{score:+d}</b> / ±8 pts</div>"
            f"</div>"
            f"<div style='background:#1e2530;border-radius:6px;height:8px;margin:4px 0 14px'>"
            f"<div style='background:{sig_color};width:{pct:.0f}%;height:8px;border-radius:6px'></div></div>",
            unsafe_allow_html=True,
        )
        if result["details"]:
            detail_df = pd.DataFrame(result["details"], columns=["Indicador", "Valor", "Descripción", "Pts"])
            st.dataframe(detail_df, use_container_width=True, hide_index=True, height=180)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Valoración fundamental
    st.markdown("<p class='section-title'>Valoración fundamental</p>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"<div style='text-align:center;padding:12px 0 8px'>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{val['color']}'>{verd_icon} {verdict}</div>"
            f"<div style='color:#8b949e;margin-top:4px'>Score: <b style='color:#cdd9e5'>{val['score']:+d} pts</b></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        ratio_rows = [
            {"Métrica": k, "Valor": v, "Referencia": ref}
            for k, (v, ref) in val["metrics"].items()
            if v is not None
        ]
        if ratio_rows:
            st.dataframe(pd.DataFrame(ratio_rows), use_container_width=True, hide_index=True, height=280)
        else:
            st.info("Sin datos fundamentales disponibles.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Info empresa
    with st.expander("Sobre la empresa"):
        st.markdown(f"**{info.get('sector','N/A')}** · {info.get('industry','N/A')}")
        st.markdown(f"🌍 {info.get('country','N/A')} &nbsp;|&nbsp; 🏛 {info.get('exchange','N/A')}", unsafe_allow_html=True)
        cap = info.get("marketCap")
        if cap:
            st.markdown(f"💰 Cap. {cap/1e9:.2f}B {currency}")
        web = info.get("website")
        if web:
            st.markdown(f"🔗 [{web}]({web})")
        if info.get("longBusinessSummary"):
            st.caption(info["longBusinessSummary"][:400] + "…")

# ── Noticias (full width) ─────────────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>Noticias recientes & sentimiento</p>", unsafe_allow_html=True)

articles = get_news(info.get("longName") or ticker, days=news_days, max_articles=10)

if not articles:
    st.info("No se encontraron noticias. Verifica que NEWSAPI_KEY está en el archivo .env y reinicia la app.")
else:
    agg = aggregate_sentiment(articles)

    na1, na2, na3, na4, na5 = st.columns(5)
    na1.metric("Sentimiento general", agg["label"])
    na2.metric("Score medio",         f"{agg['avg']:+.3f}")
    na3.metric("Noticias",            len(articles))
    na4.metric("Positivas 🟢",        agg["pos"])
    na5.metric("Negativas 🔴",        agg["neg"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    left_news, right_news = st.columns(2, gap="medium")
    for i, art in enumerate(articles):
        s_color  = {"Positivo": "#26a69a", "Negativo": "#ef5350", "Neutro": "#9e9e9e"}[art["sentiment"]]
        pill_bg  = {"Positivo": "#0d2b1e", "Negativo": "#2b0d0d", "Neutro": "#1e1e1e"}[art["sentiment"]]
        desc     = (art["description"] or "")[:100]
        desc_txt = desc + "…" if desc else ""
        target   = left_news if i % 2 == 0 else right_news
        with target:
            st.markdown(
                f"<div class='news-card'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:8px'>"
                f"<a href='{art['url']}' target='_blank' style='color:#58a6ff;text-decoration:none;"
                f"font-weight:600;font-size:0.9rem;line-height:1.3'>{art['title']}</a>"
                f"<span class='sent-pill' style='background:{pill_bg};color:{s_color};"
                f"border:1px solid {s_color};white-space:nowrap'>{art['compound']:+.2f}</span>"
                f"</div>"
                f"<div style='color:#8b949e;font-size:0.78rem;margin-top:6px'>{desc_txt}</div>"
                f"<div style='color:#484f58;font-size:0.75rem;margin-top:6px'>{art['source']} · {art['published_at']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
