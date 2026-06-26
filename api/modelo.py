import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

def executar_previsao_github(df: pd.DataFrame, t0_str: str, horizonte: int, tipo_modelo: str):
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data').reset_index(drop=True)
    df['tempo_idx'] = np.arange(len(df))
    
    t0 = pd.to_datetime(t0_str)
    treino = df[df['data'] <= t0]
    teste = df[df['data'] > t0]
    
    if len(treino) < 5:
        return {"erro": "Dados históricos insuficientes antes de t0."}
        
    X_treino = treino[['tempo_idx']]
    y_treino = treino['stars_acumulado']
    
    # Seleção de dois modelos distintos (Critério 3)
    if tipo_modelo == "Random Forest":
        model = RandomForestRegressor(n_estimators=50, random_state=42)
    else:
        model = LinearRegression()
        
    model.fit(X_treino, y_treino)
    
    # Avaliação no intervalo pós-t0
    mae, rmse = 0.0, 0.0
    if not teste.empty:
        X_teste = teste[['tempo_idx']]
        y_teste = teste['stars_acumulado']
        preds_teste = model.predict(X_teste)
        mae = mean_absolute_error(y_teste, preds_teste)
        rmse = root_mean_squared_error(y_teste, preds_teste)
        
    # Geração das datas futuras com base no Horizonte informado
    ultimo_idx = df['tempo_idx'].max()
    X_futuro = np.array([[ultimo_idx + i] for i in range(1, horizonte + 1)])
    datas_futuras = [df['data'].max() + pd.Timedelta(days=i) for i in range(1, horizonte + 1)]
    preds_futuras = model.predict(X_futuro)
    
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "historico": [{"data": str(r['data'].date()), "stars": int(r['stars_acumulado'])} for _, r in df.iterrows()],
        "previsoes": [{"data": str(d.date()), "previsao": float(p)} for d, p in zip(datas_futuras, preds_futuras)]
    }