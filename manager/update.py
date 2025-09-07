#atualizar db com novas tabelas, de necessario
# Conectar ao banco de dados (cria o arquivo se não existir)
file_path = "../xp_data.db"
import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect(file_path)
cursor = conn.cursor()

# --- Adicionar colunas ---
# Substitua "sua_tabela" pelo nome real da sua tabela (ex: "usuarios", "players")
nome_tabela = "xp_data"  # 👈 NOME DA SUA TABULA AQUI!

# Adiciona coluna "money"
cursor.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN money INTEGER DEFAULT 0")  # DEFAULT 0 para valores iniciais
# Adiciona coluna "rep"
cursor.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN rep INTEGER DEFAULT 0")

# --- Criar índices ---
cursor.execute(f"CREATE INDEX idx_money ON {nome_tabela} (money)")
cursor.execute(f"CREATE INDEX idx_rep ON {nome_tabela} (rep)")

# Salvar e fechar
conn.commit()
conn.close()
