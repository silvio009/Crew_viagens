import sqlite3
import hashlib

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

username = "silvio"
senha = "senha123"
name = "Silvio Luiz"
role = "user"

senha_hash = hashlib.sha256(senha.encode()).hexdigest()

cursor.execute(
    "INSERT INTO usuarios (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
    (username, senha_hash, name, role)
)
conn.commit()
conn.close()

print("Usuário criado com sucesso!")