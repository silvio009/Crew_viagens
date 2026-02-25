from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import sqlite3

registro = FastAPI()

registro.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("usuarios.db")
    return conn

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Criar Conta - TravelCrew Agency</title>
    <link rel="icon" href="/public/favicon.png" type="image/png" />
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Segoe UI',sans-serif; display:flex; height:100vh; overflow:hidden; }}
        .left {{ width:50%; background:#1a1a1a; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:60px 80px; }}
        .left h1 {{ color:#fff; font-size:1.1rem; font-weight:700; text-align:center; margin-bottom:28px; line-height:1.4; }}
        .group {{ width:100%; margin-bottom:12px; }}
        label {{ display:block; color:#ccc; font-size:0.88rem; margin-bottom:6px; }}
        input {{ width:100%; padding:10px 15px; background:#2a2a2a; border:1px solid #3a3a3a; border-radius:8px; color:#fff; font-size:0.9rem; outline:none; }}
        input:focus {{ border-color:#d4d803; }}
        .btn {{ width:100%; padding:11px; background:#d4d803; color:#111; font-size:0.95rem; font-weight:700; border:none; border-radius:8px; cursor:pointer; margin-top:4px; }}
        .btn:hover {{ background:#bfc202; }}
        .link {{ margin-top:18px; color:#aaa; font-size:0.88rem; text-align:center; }}
        .link a {{ color:#d4d803; text-decoration:none; font-weight:500; }}
        .msg {{ padding:12px; border-radius:8px; font-size:0.85rem; margin-bottom:14px; width:100%; text-align:center; }}
        .erro {{ background:#3a1a1a; border:1px solid #ff4444; color:#ff6b6b; }}
        .ok {{ background:#1a3a1a; border:1px solid #44ff44; color:#6bff6b; }}
        .right {{ width:50%; background:#2d2d2d; display:flex; justify-content:center; align-items:center; }}
        .right img {{ width:320px; }}

        @media (max-width: 768px) {{
            body {{ flex-direction:column; height:auto; min-height:100vh; overflow:auto; }}
            .right {{ display:none; }}
            .left {{ width:100%; padding:40px 24px; min-height:100vh; justify-content:center; }}
            .left h1 {{ font-size:1rem; }}
        }}
    </style>
</head>
<body>
    <div class="left">
        <h1>Crie sua conta para planejar sua próxima experiência de viagem</h1>
        {{msg}}
        <form method="post" style="width:100%">
            <div class="group">
                <label>Usuário</label>
                <input name="username" type="text" required />
            </div>
            <div class="group">
                <label>Nome completo</label>
                <input name="name" type="text" required />
            </div>
            <div class="group">
                <label>Senha</label>
                <input name="password" type="password" required />
            </div>
            <button class="btn" type="submit">Criar conta</button>
        </form>
        <p class="link">Já possui conta? <a href="/login">Fazer login</a></p>
    </div>
    <div class="right">
        <img src="/public/logo_name.png" alt="TravelCrew" onerror="this.style.display='none'" />
    </div>
</body>
</html>
"""

@registro.get("/registro", response_class=HTMLResponse)
async def form():
    return HTML.format(msg="")

@registro.post("/registro", response_class=HTMLResponse)
async def submit(username: str = Form(...), name: str = Form(...), password: str = Form(...)):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, name, "user")
        )
        conn.commit()
        msg = '<div class="msg ok">✅ Conta criada! <a href="http://localhost:8000/login" style="color:#d4d803">Fazer login</a></div>'
        return HTML.format(msg=msg)
    except sqlite3.IntegrityError:
        msg = '<div class="msg erro">❌ Usuário já existe. Tente outro nome.</div>'
        return HTML.format(msg=msg)
    finally:
        conn.close()