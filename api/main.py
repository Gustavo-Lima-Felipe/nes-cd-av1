import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine
from modelo import executar_previsao_github

app = FastAPI(title="GitHub Analytics API", description="Intermediário de dados e predições")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password123@db:5432/github_analytics")
engine = create_engine(DATABASE_URL)

class PredictRequest(BaseModel):
    repo_nome: str
    t0: str
    horizonte: int
    modelo: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dados")
def get_dados(linguagem: str = Query(None)):
    query = """
        SELECT r.nome, r.linguagem, r.stars, r.forks, h.data, h.stars_acumulado, h.commits_dia 
        FROM repositorios r
        JOIN historico_atividade h ON r.id = h.repositorio_id
    """
    if linguagem:
        query += f" WHERE r.linguagem = '{linguagem}'"
        
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

@app.get("/resumo")
def get_resumo():
    # Retorna agregação de estrelas e commits por linguagem (Métricas agregadas)
    query = """
        SELECT linguagem, COUNT(id) as total_repos, SUM(stars) as soma_estrelas 
        FROM repositorios GROUP BY linguagem
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

@app.post("/prever")
def prever_crescimento(req: PredictRequest):
    query = f"""
        SELECT h.data, h.stars_acumulado 
        FROM historico_atividade h
        JOIN repositorios r ON r.id = h.repositorio_id
        WHERE r.nome = '{req.repo_nome}'
    """
    df = pd.read_sql(query, engine)
    return executar_previsao_github(df, req.t0, req.horizonte, req.modelo)