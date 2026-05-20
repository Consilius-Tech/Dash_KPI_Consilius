import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import requests

st.set_page_config(page_title="Consilius | Sistema Interno", layout="wide", page_icon="♟️", initial_sidebar_state="collapsed")

API_BASE_URL = "http://api.sistema-interno.com"

def obter_dados_kpi():
    try:
        response = requests.get(f"{API_BASE_URL}/kpis")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except requests.exceptions.RequestException:
        pass
    
    membros = ["Ana Lima", "Bruno Souza", "Carla Dias", "Diego Melo", "Ester Nunes", "Felipe Costa", "Gabi Torres", "Hugo Silva"]
    areas = ["Office", "BASE", "FACE", "Office", "BASE", "FACE", "Office", "BASE"]
    cargos = ["Diretor", "Funcionário", "Funcionário", "Diretor", "Funcionário", "Funcionário", "Diretor", "Funcionário"]
    data = {
        "Membro": membros, "Área": areas, "Cargo": cargos,
        "Entrega Antes do Prazo": [8, 7, 9, 10, 6, 8, 7, 8],
        "Participação das Reuniões": [9, 8, 10, 9, 7, 9, 8, 9],
        "Ajudar outros membros": [10, 7, 8, 9, 6, 8, 7, 8],
        "Feedbacks Positivos": [9, 6, 9, 10, 7, 8, 8, 7],
        "Contribuição Metas": [8, 8, 9, 9, 6, 9, 7, 8]
    }
    return pd.DataFrame(data)

def enviar_dados_kpi(payload):
    try:
        response = requests.post(f"{API_BASE_URL}/kpis", json=payload)
        return response.status_code in [200, 201]
    except requests.exceptions.RequestException:
        return False

def autenticar_usuario(usuario, senha):
    try:
        response = requests.post(f"{API_BASE_URL}/login", json={"user": usuario, "pass": senha})
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return usuario == "admin" and senha == "admin"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "db" not in st.session_state:
    st.session_state["db"] = obter_dados_kpi()

def calcular_score(df):
    df["Score Geral"] = df[["Entrega Antes do Prazo", "Participação das Reuniões", "Ajudar outros membros", "Feedbacks Positivos", "Contribuição Metas"]].mean(axis=1).round(1)
    return df

st.session_state["db"] = calcular_score(st.session_state["db"])

if not st.session_state["logged_in"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("♟️ Consilius | Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar_usuario(usuario, senha):
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
else:
    with st.sidebar:
        st.title("♟️ Consilius")
        st.caption("Painel Interno")
        st.divider()
        tela = st.radio("Navegação", ["Dashboard", "Inserção de Dados"])
        st.divider()
        if tela == "Dashboard":
            area_sel = st.multiselect("Filtrar por Área", options=["Office", "BASE", "FACE"], default=["Office", "BASE", "FACE"])
            cargo_sel = st.multiselect("Filtrar por Cargo", options=["Diretor", "Funcionário"], default=["Diretor", "Funcionário"])
        st.divider()
        st.caption(f"📅 {date.today().strftime('%d/%m/%Y')}")
        if st.button("Sair"):
            st.session_state["logged_in"] = False
            st.rerun()

    if tela == "Dashboard":
        df_f = st.session_state["db"][st.session_state["db"]["Área"].isin(area_sel) & st.session_state["db"]["Cargo"].isin(cargo_sel)]
        st.title("📊 Dashboard de Pessoas")
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("👥 Membros", len(df_f))
        c2.metric("🏆 Score Médio", f"{df_f['Score Geral'].mean():.1f}" if not df_f.empty else "0.0")
        c3.metric("🎯 Destaque", df_f.loc[df_f['Score Geral'].idxmax(), 'Membro'] if not df_f.empty else "-")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Score Geral")
            if not df_f.empty:
                fig = px.bar(df_f.sort_values("Score Geral", ascending=True), x="Score Geral", y="Membro", orientation="h", color="Score Geral", color_continuous_scale="Blues", text="Score Geral")
                fig.update_layout(coloraxis_showscale=False)
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Indicadores de Engajamento")
            if not df_f.empty:
                df_eng = df_f[["Membro", "Participação das Reuniões", "Entrega Antes do Prazo"]].melt(id_vars="Membro", var_name="Indicador", value_name="Nota")
                fig2 = px.bar(df_eng, x="Nota", y="Membro", color="Indicador", barmode="group", color_discrete_sequence=["#7c83fd", "#a5d8ff"])
                st.plotly_chart(fig2, use_container_width=True)
        st.subheader("🎯 Radar de Desempenho")
        if not df_f.empty:
            membro_sel = st.selectbox("Selecione um membro", df_f["Membro"].tolist())
            row = df_f[df_f["Membro"] == membro_sel].iloc[0]
            categorias = ["Entrega Antes do Prazo", "Participação das Reuniões", "Ajudar outros membros", "Feedbacks Positivos", "Contribuição Metas"]
            valores = [row[cat] for cat in categorias]
            fig3 = go.Figure(go.Scatterpolar(r=valores + [valores[0]], theta=categorias + [categorias[0]], fill="toself", fillcolor="rgba(124,131,253,0.25)", line=dict(color="#7c83fd", width=2)))
            fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=400)
            st.plotly_chart(fig3, use_container_width=True)
        st.subheader("📋 Base Consolidada")
        df_show = df_f.sort_values("Score Geral", ascending=False).reset_index(drop=True)
        df_show.index = df_show.index + 1
        st.dataframe(df_show, use_container_width=True, height=320)

    elif tela == "Inserção de Dados":
        st.title("💾 Banco de Dados - Inserção de KPIs")
        st.divider()
        with st.form("form_insercao"):
            nm = st.text_input("Nome do Membro")
            col_a, col_b = st.columns(2)
            ar = col_a.selectbox("Área", ["Office", "BASE", "FACE"])
            cg = col_b.selectbox("Cargo", ["Funcionário", "Diretor"])
            st.subheader("Avaliação (0 a 10)")
            c1, c2, c3, c4, c5 = st.columns(5)
            k1 = c1.number_input("Entrega no Prazo", 0, 10, 5)
            k2 = c2.number_input("Reuniões", 0, 10, 5)
            k3 = c3.number_input("Ajuda", 0, 10, 5)
            k4 = c4.number_input("Feedbacks", 0, 10, 5)
            k5 = c5.number_input("Metas", 0, 10, 5)
            if st.form_submit_button("Registrar Dados"):
                novo_dado = pd.DataFrame({"Membro": [nm], "Área": [ar], "Cargo": [cg], "Entrega Antes do Prazo": [k1], "Participação das Reuniões": [k2], "Ajudar outros membros": [k3], "Feedbacks Positivos": [k4], "Contribuição Metas": [k5]})
                payload = novo_dado.to_dict(orient="records")[0]
                
                if enviar_dados_kpi(payload):
                    st.success("Registro enviado com sucesso para o sistema principal.")
                else:
                    st.warning("Sistema principal não respondeu. Dado salvo apenas localmente na sessão.")
                
                st.session_state["db"] = pd.concat([st.session_state["db"], novo_dado], ignore_index=True)