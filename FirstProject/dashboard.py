import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent / "atendimentos_manicure_com_horario.json"

@st.cache_data
def load_data() -> pd.DataFrame:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        atendimentos = json.load(f)
    df = pd.DataFrame(atendimentos)
    # Parse date/time fields
    df["data"] = pd.to_datetime(df["data"])  # date
    df["hora"] = pd.to_datetime(df["horario_atendimento"], format="%H:%M").dt.hour
    # Order weekday for nicer charts
    ordered_days = ["Segunda-feira", "Terca-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sabado"]
    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=ordered_days, ordered=True)
    return df

st.set_page_config(page_title="Manicure - Dashboard", layout="wide")

st.title("Manicure - Dashboard de Atendimentos e Faturamento")

# Sidebar filters
with st.sidebar:
    st.header("Filtros")
    df_all = load_data()

    # Date range
    min_date = df_all["data"].min().date()
    max_date = df_all["data"].max().date()
    date_range = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Service filter
    servicos = sorted(df_all["servico"].unique())
    sel_servicos = st.multiselect("Serviços", options=servicos, default=servicos)

    # Payment filter
    pagamentos = sorted(df_all["forma_pagamento"].unique())
    sel_pagamentos = st.multiselect("Forma de pagamento", options=pagamentos, default=pagamentos)

    # Frequent client filter
    sel_frequente = st.selectbox("Cliente frequente?", options=["Todos", True, False], index=0)

# Apply filters
mask = (
    (df_all["data"].dt.date >= start_date) &
    (df_all["data"].dt.date <= end_date) &
    (df_all["servico"].isin(sel_servicos)) &
    (df_all["forma_pagamento"].isin(sel_pagamentos))
)
if sel_frequente != "Todos":
    mask &= (df_all["cliente_frequente"] == sel_frequente)

df = df_all[mask].copy()

# KPI row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Atendimentos", int(df.shape[0]))
with col2:
    st.metric("Faturamento (R$)", float(df["preco_final"].sum()))
with col3:
    st.metric("Ticket médio (R$)", round(float(df["preco_final"].mean() if len(df) else 0), 2))
with col4:
    st.metric("Serviços únicos", int(df["servico"].nunique()))

st.markdown("---")

# Row 1: Faturamento semanal & Serviços mais vendidos
c1, c2 = st.columns(2)
with c1:
    freq = st.selectbox(
        "Frequência",
        options=[("Semanal", "W"), ("Diária", "D"), ("Mensal", "M")],
        index=0,
        key="freq_semana",
        format_func=lambda x: x[0],
    )[1]
    df_semana = df.set_index("data").resample(freq)["preco_final"].sum().reset_index()
    fig1 = px.line(
        df_semana,
        x="data",
        y="preco_final",
        markers=True,
        title=f"Faturamento ({'W' if freq=='W' else 'D' if freq=='D' else 'M'})",
        labels={"data": "Período", "preco_final": "R$"},
    )
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1, width='stretch')

with c2:
    serv_counts = df["servico"].value_counts().reset_index()
    serv_counts.columns = ["servico", "quantidade"]
    sort_serv = st.selectbox("Ordenação (serviço)", ["Decrescente", "Crescente"], index=0, key="sort_servicos")
    if sort_serv == "Decrescente":
        serv_counts = serv_counts.sort_values("quantidade", ascending=True)
    else:
        serv_counts = serv_counts.sort_values("quantidade", ascending=False)
    fig2 = px.bar(
        serv_counts,
        x="servico",
        y="quantidade",
        title="Quantidade de atendimentos por serviço",
        labels={"servico": "Serviço", "quantidade": "Atendimentos"},
    )
    fig2.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Dia da semana & Horários de pico
c3, c4 = st.columns(2)
with c3:
    dia_counts = (
        df["dia_semana"].value_counts().sort_index().reset_index()
    )
    dia_counts.columns = ["dia_semana", "atendimentos"]
    fig3 = px.bar(
        dia_counts,
        x="dia_semana",
        y="atendimentos",
        title="Atendimentos por dia da semana",
        labels={"dia_semana": "Dia da semana", "atendimentos": "Atendimentos"},
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    hora_counts = df["hora"].value_counts().sort_index().reset_index()
    hora_counts.columns = ["hora", "atendimentos"]
    fig4 = px.bar(
        hora_counts,
        x="hora",
        y="atendimentos",
        title="Distribuição de atendimentos por horário",
        labels={"hora": "Hora do dia", "atendimentos": "Atendimentos"},
    )
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Formas de pagamento
c5 = st.container()
with c5:
    pay_counts = df["forma_pagamento"].value_counts().reset_index()
    pay_counts.columns = ["forma_pagamento", "percentual"]
    fig5 = px.pie(
        pay_counts,
        names="forma_pagamento",
        values="percentual",
        title="Distribuição das formas de pagamento",
        hole=0.3,
    )
    st.plotly_chart(fig5, use_container_width=True)

# Extra metrics
m1, m2 = st.columns(2)
with m1:
    st.metric("Descontos concedidos (R$)", float(df["desconto"].sum()))
with m2:
    st.metric("Idade média", int(df["cliente_idade"].mean() if len(df) else 0))

st.markdown("---")

# Row 4: Idade (histograma) & Descontos por serviço
c6, c7 = st.columns(2)
with c6:
    idade_viz = st.selectbox("Visualização de idade", ["Histograma", "Faixas etárias"], index=1, key="idade_viz")
    if idade_viz == "Histograma":
        fig6 = px.histogram(
            df,
            x="cliente_idade",
            nbins=12,
            title="Distribuição de idade das clientes",
            labels={"cliente_idade": "Idade"},
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        bins = [0, 25, 35, 45, 55, 65, 200]
        labels_bins = ["<25", "25-34", "35-44", "45-54", "55-64", "65+"]
        df_age = df.copy()
        df_age["faixa_idade"] = pd.cut(df_age["cliente_idade"], bins=bins, labels=labels_bins, right=False)
        faixa_counts = df_age["faixa_idade"].value_counts().reindex(labels_bins).reset_index()
        faixa_counts.columns = ["faixa_idade", "atendimentos"]
        fig6b = px.bar(
            faixa_counts,
            x="faixa_idade",
            y="atendimentos",
            title="Atendimentos por faixa etária",
            labels={"faixa_idade": "Faixa etária", "atendimentos": "Atendimentos"},
        )
        st.plotly_chart(fig6b, use_container_width=True)

with c7:
    desc_by_serv = (
        df.groupby("servico", as_index=False)["desconto"].sum().sort_values("desconto", ascending=False)
    )
    fig7 = px.bar(
        desc_by_serv,
        x="servico",
        y="desconto",
        title="Descontos por serviço (R$)",
        labels={"servico": "Serviço", "desconto": "R$ em descontos"},
    )
    fig7.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig7, use_container_width=True)

# Row 5: Heatmap Dia x Hora
c8 = st.container()
with c8:
    if len(df):
        pivot = (
            df.pivot_table(index="dia_semana", columns="hora", values="id", aggfunc="count", fill_value=0)
            .reset_index()
        )
        fig8 = px.imshow(
            pivot.set_index("dia_semana"),
            aspect="auto",
            color_continuous_scale="Blues",
            title="Mapa de calor: atendimentos por dia x hora",
        )
        fig8.update_xaxes(title="Hora do dia")
        fig8.update_yaxes(title="Dia da semana")
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("Sem dados para exibir o heatmap no filtro selecionado.")

# Row 6: Receita por forma de pagamento
c9 = st.container()
with c9:
    rev_pay = (
        df.groupby("forma_pagamento", as_index=False)["preco_final"].sum().sort_values("preco_final", ascending=False)
    )
    fig9 = px.bar(
        rev_pay,
        x="forma_pagamento",
        y="preco_final",
        title="Faturamento por forma de pagamento",
        labels={"forma_pagamento": "Forma", "preco_final": "R$"},
    )
    st.plotly_chart(fig9, use_container_width=True)

# Row 7: Ticket médio por serviço
c10 = st.container()
with c10:
    avg_ticket = (
        df.groupby("servico", as_index=False)["preco_final"].mean().sort_values("preco_final", ascending=False)
    )
    fig10 = px.bar(
        avg_ticket,
        x="servico",
        y="preco_final",
        title="Ticket médio por serviço (R$)",
        labels={"servico": "Serviço", "preco_final": "R$"},
    )
    fig10.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig10, use_container_width=True)

# Data table
st.markdown("---")
with st.expander("Ver dados filtrados"):
    st.dataframe(df.sort_values("data", ascending=False), height=400, use_container_width=True)

st.caption("Construído com Streamlit + Plotly | Dados: atendimentos_manicure_com_horario.json")
