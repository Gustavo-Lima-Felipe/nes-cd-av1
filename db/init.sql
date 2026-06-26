CREATE TABLE IF NOT EXISTS repositorios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    linguagem VARCHAR(50),
    data_criacao DATE NOT NULL,
    stars INT DEFAULT 0,
    forks INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS historico_atividade (
    id SERIAL PRIMARY KEY,
    repositorio_id INT REFERENCES repositorios(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    stars_acumulado INT NOT NULL,
    commits_dia INT DEFAULT 0
);