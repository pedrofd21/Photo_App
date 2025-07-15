#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 10:24:35 2025

@author: pedrodorea
"""

############################

import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# === Page Setup ===
st.set_page_config(page_title="📊 Sumário Confinamento", layout="wide")
st.title("📊 Dashboard de Desempenho de Confinamento")

# === File Upload ===
uploaded_file = st.file_uploader("📤 Faça upload do arquivo .csv com os dados brutos", type="csv")

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()

    df_raw.columns = df_raw.columns.str.strip()
    df_raw['DATA DE ENTRADA'] = pd.to_datetime(df_raw['DATA DE ENTRADA'], errors='coerce')

    df = df_raw[df_raw['Analisa?'].str.strip().str.lower() == 'sim'].copy()
    df['Ano'] = df['DATA DE ENTRADA'].dt.year
    df['Mes'] = df['DATA DE ENTRADA'].dt.month

    selected_columns = {
        'DIAS CONF (CAB)': 'Dias Confinados',
        'PESO ENTRADA(KG)': 'Peso Entrada (kg)',
        'PESO SA?DA(KG)': 'Peso Saída (kg)',
        'PESO SA?DA(CARCAA)': 'Peso Carcaça (kg)',
        'RENDIMENTO CARCAA (SA?DA)': 'Rendimento Carcaça (%)',
        'GANHO DE PESO DIA(KG)': 'GMD (kg/cab/dia)',
        '@ PRODUZIDA (CAB)': '@ Produzida (/cab)',
        'CONSUMO MS(CAB/DIA)': 'Consumo MS/dia (kg/cab/dia)',
        'CONVERS?O ALIMENTAR': 'Conversão Alimentar (kg/kg)',
        'EFICI?NCIA BIOL?GICA': 'Eficiência Biológica (kg/kg)',
        'CONSUMO MS(CAB/PER?ODO)': 'Ingestão Total MS (kg)'
    }
    df = df.rename(columns=selected_columns)

    # === Sidebar Filters ===
    st.sidebar.subheader("🔎 Filtros")
    unique_years = sorted(df['Ano'].dropna().unique())
    selected_year = st.sidebar.selectbox("📅 Selecione o Ano", unique_years)
    df = df[df['Ano'] == selected_year]  # ✅ Filter the data by selected year

    show_by_month = st.sidebar.checkbox("📆 Mostrar Médias por Mês")
    show_by_year = st.sidebar.checkbox("📅 Mostrar Médias por Ano")

    # === Grouping Based on Checkbox Selections ===
    if show_by_year:
        group_cols = ['Ano']
    elif show_by_month:
        group_cols = ['Mes']
    else:
        group_cols = ['Ano', 'Mes']

    summary = (
        df
        .groupby(group_cols)[list(selected_columns.values())]
        .mean(numeric_only=True)
        .reset_index()
    )

    if not show_by_year and not show_by_month:
        count_df = (
            df
            .groupby(['Ano', 'Mes'])['COD. ANIMAL']
            .nunique()
            .reset_index()
            .rename(columns={'COD. ANIMAL': 'Quantidade de Animais'})
        )
        summary = pd.merge(count_df, summary, on=['Ano', 'Mes'])
        summary["Ano-Mes"] = pd.to_datetime(summary["Ano"].astype(str) + "-" + summary["Mes"].astype(str) + "-01")
        summary = summary.sort_values("Ano-Mes")

    # === Rounding Rules ===
    df_display = summary.copy()

    whole_cols = [
        "Dias Confinados", "Peso Entrada (kg)", "Peso Saída (kg)",
        "Peso Carcaça (kg)", "Eficiência Biológica (kg/kg)", "Ingestão Total MS (kg)"
    ]
    thousandth_cols = [
        "GMD (kg/cab/dia)", "@ Produzida (/cab)",
        "Consumo MS/dia (kg/cab/dia)", "Conversão Alimentar (kg/kg)"
    ]
    hundredth_cols = ["Rendimento Carcaça (%)"]

    for col in whole_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(0).astype("Int64")
    for col in thousandth_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(3)
    for col in hundredth_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(2)

    # === Sidebar Export Button Below Checkboxes ===
    def generate_excel_download(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Resumo')
        return output.getvalue()

    excel_data = generate_excel_download(df_display)
    b64 = base64.b64encode(excel_data).decode()
    export_button = f"""
        <div style="text-align:center">
            <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
            download="resumo_confinamento.xlsx">
                <button style="
                    padding: 0.5em 1em;
                    font-size: 16px;
                    background-color: #4CAF50;
                    color: White; 
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 10px;">
                    📤 Exportar Resumo
                </button>
            </a>
        </div>
    """
    st.sidebar.markdown(export_button, unsafe_allow_html=True)

    # === Display Table ===
    if show_by_year:
        st.subheader("📊 Médias por Ano")
    elif show_by_month:
        st.subheader("📊 Médias por Mês (todos os anos)")
    else:
        st.subheader(f"📅 Tabela de Médias Mensais - {selected_year}")

    st.dataframe(df_display, use_container_width=True)

    # === Charts (only for full monthly view) ===
    if not show_by_year and not show_by_month:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 GMD (kg/cab/dia)")
            st.line_chart(data=df_display, x="Ano-Mes", y="GMD (kg/cab/dia)")

        with col2:
            st.subheader("📈 Rendimento de Carcaça (%)")
            st.line_chart(data=df_display, x="Ano-Mes", y="Rendimento Carcaça (%)")

        st.subheader("📉 Eficiência Biológica (kg/kg)")
        st.line_chart(data=df_display, x="Ano-Mes", y="Eficiência Biológica (kg/kg)")

else:
    st.info("📤 Faça upload do arquivo .csv para visualizar o painel.")
