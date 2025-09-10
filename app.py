import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Vehículos US — EDA", layout="wide")
st.title("Análisis Exploratorio — Vehicles US")  # Encabezado ✔


@st.cache_data
def load_data(path):
    return pd.read_csv(path)

data_path = Path("datasets/vehicles_us.csv")
uploaded = st.file_uploader("Sube un CSV alternativo (opcional)", type=["csv"])

if uploaded is not None:
    df = load_data(uploaded)
elif data_path.exists():
    df = load_data(data_path)
else:
    st.error("No se encontró datasets/vehicles_us.csv")
    st.stop()
st.subheader("Graficar bajo demanda")
col1, col2 = st.columns(2)

with col1:
    if st.button("Mostrar histograma (precio)"):
        st.write("Histograma de precios")
        fig_btn_hist = px.histogram(df, x="price", nbins=40, title="Histograma (botón)")
        st.plotly_chart(fig_btn_hist, use_container_width=True)

with col2:
    if st.button("Mostrar dispersión (odometer vs price)"):
        st.write("Dispersión odometer vs price")
        fig_btn_sc = px.scatter(df, x="odometer", y="price", opacity=0.5,
                                title="Dispersión (botón)")
        st.plotly_chart(fig_btn_sc, use_container_width=True)


st.sidebar.header("Filtros")
remove_outliers = st.sidebar.checkbox("Quitar precios extremos (p5–p95)", value=True)  # Checkbox ✔
log_price = st.sidebar.checkbox("Escala log en precio", value=False)

df_plot = df.copy()
if "price" in df_plot.columns and remove_outliers:
    p5, p95 = df_plot["price"].quantile([0.05, 0.95])
    df_plot = df_plot[(df_plot["price"] >= p5) & (df_plot["price"] <= p95)]

# Histograma ✔
if "price" in df_plot.columns:
    st.subheader("Distribución de precios")
    bins = st.slider("Número de bins", 10, 100, 40, key="bins_hist")
    fig_hist = px.histogram(df_plot, x="price", nbins=bins, title="Histograma de Precio")
    if log_price:
        fig_hist.update_xaxes(type="log")
    st.plotly_chart(fig_hist, use_container_width=True)

# Dispersión ✔
num_cols = df_plot.select_dtypes(include="number").columns.tolist()
cat_cols = df_plot.select_dtypes(exclude="number").columns.tolist()

st.subheader("Relación entre variables")
x_default = "odometer" if "odometer" in num_cols else (num_cols[0] if num_cols else None)
y_default = "price"    if "price"    in num_cols else (num_cols[1] if len(num_cols)>1 else None)

if num_cols:
    x = st.selectbox("Eje X (numérico)", num_cols, index=num_cols.index(x_default) if x_default in num_cols else 0)
    y = st.selectbox("Eje Y (numérico)", num_cols, index=num_cols.index(y_default) if y_default in num_cols else 0)
    color = st.selectbox("Color (categórico, opcional)", [None] + cat_cols)
    fig_scatter = px.scatter(df_plot, x=x, y=y, color=color, opacity=0.5, title=f"Dispersión: {x} vs {y}")
    if log_price and (x == "price" or y == "price"):
        (fig_scatter.update_xaxes if x == "price" else fig_scatter.update_yaxes)(type="log")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No hay columnas numéricas para graficar.")
