import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Consilius | Dashboard", layout="wide", page_icon="📊")

# ── Estilo visual ───────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0f1117; color: #e8eaf6; }
  [data-testid="stSidebar"] { background: #1a1d2e; }
  h1, h2, h3 { color: #7c83fd; }
  .metric-card {
    background: #1e2235; border-radius: 12px; padding: 18px 24px;
    border-left: 4px solid #7c83fd; margin-bottom: 8px;
  }
  .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Dados de exemplo (substitua por banco de dados real se desejar) ─────────
@st.cache_data
def load_data():
    membros = [
        "Ana Lima", "Bruno Souza", "Carla Dias", "Diego Melo", "Ester Nunes",
        "Felipe Costa", "Gabi Torres", "Hugo Silva"
    ]
    areas = ["Projetos", "Marketing", "Financeiro", "RH", "Jurídico", "TI", "Projetos", "Marketing"]
    cargos = ["Trainee", "Analista", "Analista", "Diretor", "Trainee", "Analista", "Diretor", "Trainee"]

    data = {
        "Membro": membros,
        "Área": areas,
        "Cargo": cargos,
        "Presença (%)": [90, 75, 85, 95, 60, 88, 70, 82],
        "Tarefas Entregues": [18, 12, 15, 22, 8, 19, 14, 11],
        "Tarefas Totais": [20, 16, 18, 23, 15, 21, 18, 14],
        "Projetos Ativos": [3, 2, 2, 4, 1, 3, 2, 1],
        "Avaliação 360 (0-10)": [8.5, 7.0, 8.0, 9.2, 6.5, 8.8, 7.5, 7.8],
        "Horas Capacitação": [12, 6, 10, 15, 4, 14, 8, 9],
        "NPS Interno (0-10)": [8.0, 7.5, 8.5, 9.5, 6.0, 9.0, 7.0, 8.0],
    }
    df = pd.DataFrame(data)
    df["Taxa de Entrega (%)"] = (df["Tarefas Entregues"] / df["Tarefas Totais"] * 100).round(1)
    df["Score Geral"] = (
        df["Presença (%)"] * 0.20 +
        df["Taxa de Entrega (%)"] * 0.30 +
        df["Avaliação 360 (0-10)"] * 10 * 0.25 +
        df["NPS Interno (0-10)"] * 10 * 0.15 +
        (df["Horas Capacitação"] / 15 * 100).clip(0, 100) * 0.10
    ).round(1)
    return df

df = load_data()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Single_line_emblem_of_Brazil.svg/240px-Single_line_emblem_of_Brazil.svg.png", width=50)
    st.title("Consilius")
    st.caption("Empresa Júnior — Painel de Pessoas")
    st.divider()

    area_sel = st.multiselect("Filtrar por Área", options=sorted(df["Área"].unique()), default=sorted(df["Área"].unique()))
    cargo_sel = st.multiselect("Filtrar por Cargo", options=sorted(df["Cargo"].unique()), default=sorted(df["Cargo"].unique()))
    st.divider()
    st.caption(f"📅 {date.today().strftime('%d/%m/%Y')}")

df_f = df[df["Área"].isin(area_sel) & df["Cargo"].isin(cargo_sel)]

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.title("📊 Dashboard de Pessoas — Consilius")
st.caption("Acompanhamento de KPIs individuais e coletivos da equipe")
st.divider()

# ── KPIs gerais ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("👥 Membros", len(df_f))
c2.metric("✅ Presença Média", f"{df_f['Presença (%)'].mean():.0f}%")
c3.metric("📦 Taxa de Entrega", f"{df_f['Taxa de Entrega (%)'].mean():.0f}%")
c4.metric("⭐ Avaliação 360", f"{df_f['Avaliação 360 (0-10)'].mean():.1f}/10")
c5.metric("🏆 Score Médio", f"{df_f['Score Geral'].mean():.1f}")

st.divider()

# ── Gráficos ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Score Geral por Membro")
    fig = px.bar(
        df_f.sort_values("Score Geral", ascending=True),
        x="Score Geral", y="Membro", orientation="h",
        color="Score Geral", color_continuous_scale="Blues",
        text="Score Geral"
    )
    fig.update_layout(paper_bgcolor="#1e2235", plot_bgcolor="#1e2235", font_color="#e8eaf6", coloraxis_showscale=False)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribuição por Área")
    fig2 = px.pie(
        df_f, names="Área", hole=0.5,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig2.update_layout(paper_bgcolor="#1e2235", font_color="#e8eaf6")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Presença vs. Taxa de Entrega")
    fig3 = px.scatter(
        df_f, x="Presença (%)", y="Taxa de Entrega (%)",
        size="Projetos Ativos", color="Área", text="Membro",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig3.update_layout(paper_bgcolor="#1e2235", plot_bgcolor="#1e2235", font_color="#e8eaf6")
    fig3.update_traces(textposition="top center")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Horas de Capacitação por Membro")
    fig4 = px.bar(
        df_f.sort_values("Horas Capacitação", ascending=False),
        x="Membro", y="Horas Capacitação",
        color="Cargo", color_discrete_sequence=["#7c83fd", "#a5d8ff", "#74c0fc"]
    )
    fig4.update_layout(paper_bgcolor="#1e2235", plot_bgcolor="#1e2235", font_color="#e8eaf6")
    st.plotly_chart(fig4, use_container_width=True)

# ── Radar de desempenho ──────────────────────────────────────────────────────
st.subheader("🎯 Radar de Desempenho Individual")
membro_sel = st.selectbox("Selecione um membro", df_f["Membro"].tolist())
row = df_f[df_f["Membro"] == membro_sel].iloc[0]

categorias = ["Presença", "Entrega", "Avaliação 360", "NPS Interno", "Capacitação"]
valores = [
    row["Presença (%)"],
    row["Taxa de Entrega (%)"],
    row["Avaliação 360 (0-10)"] * 10,
    row["NPS Interno (0-10)"] * 10,
    min(row["Horas Capacitação"] / 15 * 100, 100)
]

fig5 = go.Figure(go.Scatterpolar(
    r=valores + [valores[0]],
    theta=categorias + [categorias[0]],
    fill="toself", fillcolor="rgba(124,131,253,0.25)",
    line=dict(color="#7c83fd", width=2)
))
fig5.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], color="#aaa"),
        bgcolor="#1e2235"
    ),
    paper_bgcolor="#1e2235", font_color="#e8eaf6",
    showlegend=False, height=400
)
st.plotly_chart(fig5, use_container_width=True)

# ── Tabela completa ──────────────────────────────────────────────────────────
st.subheader("📋 Tabela de KPIs Completa")
cols_show = ["Membro", "Área", "Cargo", "Presença (%)", "Taxa de Entrega (%)",
             "Projetos Ativos", "Avaliação 360 (0-10)", "Horas Capacitação", "NPS Interno (0-10)", "Score Geral"]
st.dataframe(
    df_f[cols_show].sort_values("Score Geral", ascending=False).reset_index(drop=True),
    use_container_width=True, height=320
)

# ── Adicionar membro ──────────────────────────────────────────────────────────
with st.expander("➕ Adicionar / Editar Membro (demo)"):
    st.info("Em produção, conecte a um banco de dados (ex: SQLite, Google Sheets ou Supabase) para persistência real.")
    nm = st.text_input("Nome")
    ar = st.selectbox("Área", ["Projetos", "Marketing", "Financeiro", "RH", "Jurídico", "TI"])
    cg = st.selectbox("Cargo", ["Trainee", "Analista", "Diretor"])
    if st.button("Salvar (demo)"):
        st.success(f"Membro {nm} registrado com sucesso! (apenas demonstração)")