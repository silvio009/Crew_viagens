import os
import sqlite3
import hashlib
import chainlit as cl
import smtplib
from email.mime.text import MIMEText
from crews.travel_crew import CompleteTravelCrew
from dotenv import load_dotenv
import asyncio

load_dotenv()

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
conn.commit()

def registrar_usuario(username, password, name="Usuário", role="user"):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, name, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def autenticar_usuario(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT username, name, role FROM usuarios WHERE username=? AND password_hash=?",
        (username, password_hash)
    )
    return cursor.fetchone()

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    user = autenticar_usuario(username, password)
    if not user:
        return None
    username, name, role = user
    return cl.User(
        identifier=username,
        metadata={"name": name, "role": role}
    )

async def enviar_email(destinatario, assunto, corpo):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")
    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destinatario
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)

crew = CompleteTravelCrew()

@cl.on_chat_start
async def start():
    cl.user_session.set("estado", "origem")
    cl.user_session.set("origem", "")
    cl.user_session.set("destino", "")
    cl.user_session.set("dias", 0)
    cl.user_session.set("ultimo_roteiro", "")
    cl.user_session.set("distancia_km", 0)

    app_user = cl.user_session.get("user")
    await cl.Message(
        content=f"👋 Olá {app_user.metadata['name']}! Vamos planejar sua viagem.\nDigite sua cidade de origem para começar."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    user_msg = message.content.strip()
    estado = cl.user_session.get("estado")

    if estado == "origem":
        cl.user_session.set("origem", user_msg)
        cl.user_session.set("estado", "destino")
        await cl.Message(content="🏔️ Qual é o destino da sua viagem?").send()

    elif estado == "destino":
        cl.user_session.set("destino", user_msg)
        cl.user_session.set("estado", "dias")
        await cl.Message(content="⏳ Quantos dias você pretende ficar?").send()

    elif estado == "dias":
        try:
            dias = int(user_msg)
            cl.user_session.set("dias", dias)
            origem = cl.user_session.get("origem")
            destino = cl.user_session.get("destino")

            msg = cl.Message(content="⏳ Gerando seu roteiro, aguarde...")
            await msg.send()

            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(None, crew.run, origem, destino, dias)

            roteiro = resultado["relatorio_destino"]
            distancia = resultado["distancia_km"]

            cl.user_session.set("ultimo_roteiro", roteiro)
            cl.user_session.set("distancia_km", distancia)

            await cl.Message(content=f"📄 Aqui está o seu roteiro:\n\n{roteiro}").send()

            if distancia > 350:
                cl.user_session.set("estado", "perguntar_voos")
                await cl.Message(content="✈️ Detectei que o destino é distante. Deseja buscar voos? (sim/não)").send()
            else:
                cl.user_session.set("estado", "email")
                await cl.Message(content="✉️ Deseja receber este roteiro por e-mail? Se sim, digite seu e-mail.").send()

        except ValueError:
            await cl.Message(content="⚠️ Por favor, digite um número válido de dias.").send()

    elif estado == "perguntar_voos":
        if user_msg.lower() in ["sim", "s"]:
            cl.user_session.set("estado", "voo_ida")
            await cl.Message(content="📅 Digite a data de ida (AAAA-MM-DD):").send()
        else:
            cl.user_session.set("estado", "email")
            await cl.Message(content="✉️ Deseja receber este roteiro por e-mail? Se sim, digite seu e-mail.").send()

    elif estado == "voo_ida":
        cl.user_session.set("voo_ida", user_msg)
        cl.user_session.set("estado", "voo_volta")
        await cl.Message(content="📅 Digite a data de volta (AAAA-MM-DD):").send()

    elif estado == "voo_volta":
        cl.user_session.set("voo_volta", user_msg)
        origem = cl.user_session.get("origem")
        destino = cl.user_session.get("destino")
        dias = cl.user_session.get("dias")
        ida = cl.user_session.get("voo_ida")
        volta = user_msg

        msg = cl.Message(content="✈️ Buscando voos, aguarde...")
        await msg.send()

        loop = asyncio.get_event_loop()
        resultado_voos = await loop.run_in_executor(
            None, lambda: crew.run(origem, destino, dias, buscar_voos=True, ida=ida, volta=volta)
        )

        if resultado_voos["voos"]:
            await cl.Message(content=f"✈️ Voos encontrados:\n\n{resultado_voos['voos']}").send()

        cl.user_session.set("estado", "email")
        await cl.Message(content="✉️ Deseja receber este roteiro por e-mail? Se sim, digite seu e-mail.").send()

    elif estado == "email":
        roteiro = cl.user_session.get("ultimo_roteiro")
        await enviar_email(user_msg, "Seu roteiro de viagem", roteiro)
        await cl.Message(content="✅ Roteiro enviado com sucesso!").send()
        cl.user_session.set("estado", "origem")
        await cl.Message(content="🔄 Para planejar uma nova viagem, digite sua cidade de origem.").send()

    else:
        await cl.Message(content="⚠️ Não entendi. Por favor, digite sua cidade de origem.").send()