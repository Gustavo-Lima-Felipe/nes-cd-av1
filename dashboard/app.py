import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

API_URL = "http://api:8000"

st.set_page_config(page_title="GitHub Preditivo", layout="wide")
st.title("🐙 Dashboard Analytics GitHub - Engenharia & Engajamento")

# Validação do container de backend via Health Check
try:
    requests.get(f"{API_URL}/health").json()
except:
    st.error("Conexão interrompida com a API intermediária.")
    st.stop()

# Painel de Seleção Lateral
st.sidebar.header("Preditor de Crescimento (Stars)")
repo_alvo = st.sidebar.selectbox("Selecione o Repositório", ["react", "tensorflow", "fastapi", "kubernetes"])
modelo_ml = st.sidebar.selectbox("Algoritmo Preditivo", ["Regressão Linear", "Random Forest"])
horizonte_dias = st.sidebar.slider("Janela Futura (Dias)", 7, 90, 30)
data_corte_t0 = st.sidebar.date_input("Data de Divisão (t0)", pd.to_datetime("2026-02-01"))

# Consumo de Rotas HTTP da API
dados_completos = requests.get(f"{API_URL}/dados").json()
resumo_linguagens = requests.get(f"{API_URL}/resumo").json()
df_geral = pd.DataFrame(dados_completos)

# Requisitando predição temporal
payload = {"repo_nome": repo_alvo, "t0": str(data_corte_t0), "horizonte": horizonte_dias, "modelo": modelo_ml}
# 1. Faz a requisição de predição para a API FastAPI
res_predicao = requests.post(f"{API_URL}/prever", json=payload).json()

# 2. VALIDAÇÃO SEGURA: Só avança se a estrutura contiver o histórico e as previsões
if isinstance(res_predicao, dict) and "historico" in res_predicao and "previsoes" in res_predicao:
    
    st.subheader("🎯 Acurácia do Modelo Preditivo no Período de Validação")
    m_col1, m_col2 = st.columns(2)
    
    mae_val = res_predicao.get('mae', 0.0)
    rmse_val = res_predicao.get('rmse', 0.0)
    
    m_col1.metric("MAE (Erro Médio Absoluto)", f"{mae_val:.1f} Stars")
    m_col2.metric("RMSE (Raiz do Erro Quadrático)", f"{rmse_val:.1f}")

    st.subheader(f"📈 Evolução Temporal e Predição de Estrelas: Repo '{repo_alvo}'")
    
    # INDENTAÇÃO OBRIGATÓRIA: Estas linhas DEVEM ficar dentro do IF
    df_hist_plot = pd.DataFrame(res_predicao['historico'])
    df_pred_plot = pd.DataFrame(res_predicao['previsoes'])

    df_hist_plot['data'] = pd.to_datetime(df_hist_plot['data'])
    df_pred_plot['data'] = pd.to_datetime(df_pred_plot['data'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist_plot['data'], y=df_hist_plot['stars'], mode='lines', name='Histórico Real', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=df_pred_plot['data'], y=df_pred_plot['previsao'], mode='lines', name='Tendência Preditiva', line=dict(color='#ff7f0e', dash='dash')))
    
    # Marcador temporal usando string segura
    # 1. Converta a data para milissegundos (transforma a data em um número inteiro)
    t0_em_milissegundos = pd.to_datetime(data_corte_t0).timestamp() * 1000

    # 2. Passe esse número para o add_vline
    fig.add_vline(
        x=t0_em_milissegundos, 
        line_width=1.5, 
        line_dash="dot", 
        line_color="red", 
        annotation_text="Corte t0",
        annotation_position="top left"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    # Caso o banco esteja vazio ou a API falhe, exibe o aviso sem quebrar a tela
    st.warning("⚠️ Dados insuficientes no banco local para gerar o modelo preditivo.")
    st.info("👉 Mantenha este terminal rodando e execute o script populador em uma nova janela para buscar os dados reais da API do GitHub: `python db/carga_github.py`")