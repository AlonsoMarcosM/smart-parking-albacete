"""Dashboard Streamlit del piloto Smart Parking Albacete.

Consume exclusivamente la API REST publicada por el backend (no toca DynamoDB
directamente) para demostrar que un cliente externo cualquiera podria hacer lo
mismo. Layout 2x2 compacto pensado para pantalla 1080p sin scroll.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "infra" / "infra_state.json"


def _resolve_api_base() -> str:
    if os.environ.get("API_BASE_URL"):
        return os.environ["API_BASE_URL"]
    if STATE_FILE.exists():
        with STATE_FILE.open(encoding="utf-8") as fh:
            state = json.load(fh)
        if state.get("apiBaseUrl"):
            return state["apiBaseUrl"]
    return ""


API_BASE = _resolve_api_base()

st.set_page_config(
    page_title="Smart Parking Albacete",
    page_icon=":car:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS compactador: reduce paddings/margenes para caber en 1080p sin scroll.
st.markdown(
    """
    <style>
      .block-container {padding-top: 0.6rem; padding-bottom: 0.4rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%;}
      [data-testid="stMetric"] {padding: 4px 8px;}
      [data-testid="stMetricLabel"] {font-size: 0.8rem;}
      [data-testid="stMetricValue"] {font-size: 1.6rem;}
      h1 {font-size: 1.4rem !important; margin-bottom: 0.2rem;}
      h2, h3 {font-size: 1.0rem !important; margin-top: 0.2rem; margin-bottom: 0.2rem;}
      .stPlotlyChart, .stPyDeckChart {margin-top: 0 !important;}
      .stDataFrame {margin-top: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuracion")
    api_input = st.text_input("URL base de la API", value=API_BASE)
    refresh_seconds = st.slider("Refresco automatico (s)", 0, 30, 10)
    if st.button("Forzar refresco"):
        st.rerun()

api_input = api_input or API_BASE
refresh_seconds = locals().get("refresh_seconds", 10)

if not api_input:
    st.warning("Define API_BASE_URL o despliega API Gateway primero.")
    st.stop()


@st.cache_data(ttl=4)
def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


try:
    spots_data = fetch_json(f"{api_input}/spots")
    zones_data = fetch_json(f"{api_input}/zones")
except Exception as err:
    st.error(f"No se pudo conectar con la API: {err}")
    st.stop()

spots = spots_data.get("items", [])
zones = zones_data.get("items", [])

total = len(spots)
free = sum(1 for s in spots if s.get("status") == "free")
occupied = sum(1 for s in spots if s.get("status") == "occupied")
unknown = total - free - occupied
rate = (occupied / total * 100) if total else 0.0

# Cabecera ultracompacta: titulo + KPIs en la misma fila.
st.markdown("### Smart Parking Albacete · Panel de operador")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Plazas", total)
k2.metric("Libres", free)
k3.metric("Ocupadas", occupied)
k4.metric("Sin datos", unknown)
k5.metric("Ocupacion", f"{rate:.1f} %")

# ---- Grid 2x2 ----
row1_left, row1_right = st.columns(2, gap="small")
row2_left, row2_right = st.columns(2, gap="small")

MAP_HEIGHT = 360
CHART_HEIGHT = 320
TABLE_HEIGHT = 320

# (1,1) Mapa en tiempo real
with row1_left:
    st.markdown("**Mapa en tiempo real**")
    if spots:
        df = pd.DataFrame(spots)
        df["lat"] = df["lat"].astype(float)
        df["lon"] = df["lon"].astype(float)
        _color_map = {"free": [46, 204, 113], "occupied": [231, 76, 60]}
        df["color"] = df["status"].apply(lambda s: _color_map.get(s, [127, 140, 141]))
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position="[lon, lat]",
            get_color="color",
            get_radius=12,
            pickable=True,
        )
        view = pdk.ViewState(latitude=38.9796, longitude=-1.8524, zoom=15, pitch=0)
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                tooltip={"text": "{spotId}\n{street}\nEstado: {status}"},
            ),
            height=MAP_HEIGHT,
        )

# (1,2) KPIs por sub-zona
with row1_right:
    st.markdown("**KPIs por sub-zona**")
    if zones:
        zdf = pd.DataFrame(zones).sort_values("zoneId")
        fig = px.bar(
            zdf,
            x="zoneId",
            y=["free", "occupied", "unknown"],
            labels={"value": "Plazas", "zoneId": "Sub-zona", "variable": "Estado"},
            color_discrete_map={
                "free": "#2ecc71",
                "occupied": "#e74c3c",
                "unknown": "#95a5a6",
            },
        )
        fig.update_layout(
            height=MAP_HEIGHT,
            margin=dict(l=0, r=0, t=10, b=0),
            barmode="stack",
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

# (2,1) Evolucion temporal
with row2_left:
    st.markdown("**Evolucion temporal**")
    zone_options = [z["zoneId"] for z in zones]
    if zone_options:
        selected_zone = st.selectbox(
            "Sub-zona",
            zone_options,
            label_visibility="collapsed",
            key="zone_select",
        )
        try:
            kpis_data = fetch_json(f"{api_input}/zones/{selected_zone}/kpis?limit=200")
            items = kpis_data.get("items", [])
            if items:
                ts = pd.DataFrame(items).sort_values("windowEnd")
                ts["occupancyRate"] = ts["occupancyRate"].astype(float) * 100
                fig2 = px.line(
                    ts,
                    x="windowEnd",
                    y="occupancyRate",
                    labels={"occupancyRate": "% Ocupacion", "windowEnd": "Tiempo"},
                )
                fig2.update_layout(
                    height=CHART_HEIGHT - 40,
                    margin=dict(l=0, r=0, t=5, b=0),
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sin agregados aun. Espera unos segundos.")
        except Exception as err:
            st.warning(f"KPIs temporales: {err}")

# (2,2) Detalle de plazas
with row2_right:
    st.markdown("**Detalle de plazas**")
    if spots:
        spots_df = pd.DataFrame(spots)
        show_cols = ["spotId", "zoneId", "street", "status", "batteryLevel"]
        st.dataframe(
            spots_df[[c for c in show_cols if c in spots_df.columns]],
            use_container_width=True,
            hide_index=True,
            height=TABLE_HEIGHT,
        )

if refresh_seconds:
    time.sleep(refresh_seconds)
    st.rerun()
