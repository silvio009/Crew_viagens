import os
import sqlite3
import re
import hashlib
import chainlit as cl
import smtplib
import urllib.request
import urllib.parse
import json
from email.mime.text import MIMEText
from crews.travel_crew import CompleteTravelCrew
from tools.email_tool import enviar_email
from dotenv import load_dotenv
import asyncio

load_dotenv()

os.makedirs("public", exist_ok=True)
with open("public/config.js", "w") as f:
    f.write(f"window._owKey = '{os.getenv('OPENWEATHER_API_KEY')}';")




def validar_entrada(tipo: str, valor: str) -> tuple[bool, str]:
    erros = {
        "cidade_origem": f"'{valor}' não parece ser uma cidade de origem válida. Tente novamente.",
        "cidade_destino": f"'{valor}' não parece ser um destino válido. Tente novamente.",
        "dias": "Por favor, digite um número válido de dias entre 1 e 60.",
    }

    if tipo == "dias":
        try:
            dias = int(valor)
            if 1 <= dias <= 60:
                return True, ""
            return False, erros[tipo]
        except ValueError:
            return False, erros[tipo]

    if tipo in ("cidade_origem", "cidade_destino"):
        try:
            query = urllib.parse.quote(valor)
            req = urllib.request.Request(
                f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1&featuretype=city",
                headers={"User-Agent": "TravelCrewApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())

                tipos_validos = {
                    "city", "town", "village", "municipality",
                    "state", "country", "region", "county",
                    "administrative", "suburb", "island"
                }

                for resultado in data:
                    classe = resultado.get("class", "")
                    tipo_resultado = resultado.get("type", "")
                    if classe in ("place", "boundary", "natural") and tipo_resultado in tipos_validos:
                        return True, ""

                return False, erros[tipo]

        except Exception as e:
            print(f"Erro validação Nominatim: {e}")
            return True, ""

    return True, ""
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


ROTEIRO_MOCK = """
  ## Guia Completo de Viagem: Rio de Janeiro                                                                                         
                                                                                                                                     
  ## 📍 Visão Geral                                                                                                                  
  O Rio de Janeiro é uma cidade linda e vibrante, localizada na costa sudeste do Brasil. Com uma distância de 430 km da capital      
  federal, é um destino popular para turistas de todo o mundo. O tempo médio para visitar a cidade é de 6 a 8 horas, dependendo do   
  tráfego e da rota escolhida. A principal rota para chegar ao Rio é a BR-116, que oferece uma visão deslumbrante da cidade e da     
  costa.                                                                                                                             
                                                                                                                                     
  ## 🚗 Como Chegar                                                                                                                  
  Para chegar ao Rio de Janeiro, é possível pegar a BR-116, que é a principal rota de acesso à cidade. A distância é de 430 km e o   
  tempo médio de viagem é de 6 a 8 horas, dependendo do tráfego e da rota escolhida. É importante notar que a BR-116 é uma rodovia   
  importante e pode ter tráfego intenso, especialmente durante as horas de pico.                                                     
                                                                                                                                     
  ## 🗺️ Roteiro Sugerido para 2 Dias                                                                                                 
                                                                                                                                     
  ### Dia 1                                                                                                                          
                                                                                                                                     
  * **Corcovado - Cristo Redentor** (2 horas)                                                                                        
  O Cristo Redentor é um dos principais pontos turísticos do Rio de Janeiro e uma das sete maravilhas do mundo. Localizado no topo   
  do Corcovado, oferece uma visão deslumbrante da cidade e da costa. O motivo de visita é conhecer o Cristo Redentor e aproveitar a  
  vista incrível.                                                                                                                    
  * **Praia de Ipanema** (3 horas)                                                                                                   
  A Praia de Ipanema é uma das principais praias do Rio de Janeiro e um destino popular para turistas. Localizada na zona sul da     
  cidade, oferece areia branca e águas cristalinas. O motivo de visita é conhecer a Praia de Ipanema e aproveitar o sol e a areia.   
                                                                                                                                     
  ### Dia 2                                                                                                                          
                                                                                                                                     
  * **Bondinho Pão de Açúcar** (2 horas)                                                                                             
  O Bondinho Pão de Açúcar é um dos principais pontos turísticos do Rio de Janeiro e oferece uma visão deslumbrante da cidade e da   
  costa. Localizado no topo do Pão de Açúcar, é um destino popular para turistas. O motivo de visita é conhecer o Pão de Açúcar e    
  aproveitar a vista incrível.                                                                                                       
  * **Praia de Copacabana** (3 horas)                                                                                                
  A Praia de Copacabana é uma das principais praias do Rio de Janeiro e um destino popular para turistas. Localizada na zona sul da  
  cidade, oferece areia branca e águas cristalinas. O motivo de visita é conhecer a Praia de Copacabana e aproveitar o sol e a       
  areia.                                                                                                                             
                                                                                                                                     
  ## 🍽️ Onde Comer                                                                                                                   
                                                                                                                                     
  * **Oseille** (Restaurante francês)                                                                                                
  O Oseille é um restaurante francês localizado no coração do Rio de Janeiro. Oferece comida francesa de alta qualidade e um         
  ambiente elegante. O diferencial é a comida francesa de alta qualidade e o ambiente elegante. A faixa de preço é de R$ 50-R$ 100   
  e a avaliação é de 4,5 estrelas.                                                                                                   
  * **Ristorante Hotel Cipriani** (Restaurante italiano)                                                                             
  O Ristorante Hotel Cipriani é um restaurante italiano localizado no Hotel Cipriani. Oferece comida italiana de alta qualidade e    
  um ambiente elegante. O diferencial é a comida italiana de alta qualidade e o ambiente elegante. A faixa de preço é de R$ 50-R$    
  100 e a avaliação é de 4,5 estrelas.                                                                                               
  * **Rudä** (Restaurante contemporâneo)                                                                                             
  O Rudä é um restaurante contemporâneo localizado no coração do Rio de Janeiro. Oferece comida contemporânea de alta qualidade e    
  um ambiente elegante. O diferencial é a comida contemporânea de alta qualidade e o ambiente elegante. A faixa de preço é de R$     
  50-R$ 100 e a avaliação é de 4,5 estrelas.                                                                                         
  * **Casa Horto** (Restaurante brasileiro)                                                                                          
  A Casa Horto é um restaurante brasileiro localizado no coração do Rio de Janeiro. Oferece comida brasileira de alta qualidade e    
  um ambiente elegante. O diferencial é a comida brasileira de alta qualidade e o ambiente elegante. A faixa de preço é de R$ 30-R$  
  60 e a avaliação é de 4,5 estrelas.                                                                                                
  * **Fairmont** (Restaurante internacional)                                                                                         
  O Fairmont é um restaurante internacional localizado no Hotel Fairmont. Oferece comida internacional de alta qualidade e um        
  ambiente elegante. O diferencial é a comida internacional de alta qualidade e o ambiente elegante. A faixa de preço é de R$ 50-R$  
  100 e a avaliação é de 4,5 estrelas.                                                                                               
                                                                                                                                     
  ## 🏨 Onde Ficar                                                                                                                   
                                                                                                                                     
  * **Fairmont** (Luxo)                                                                                                              
  O Fairmont é um hotel de luxo localizado no coração do Rio de Janeiro. Oferece quartos elegantes e um ambiente sofisticado. A      
  categoria é de luxo e o preço médio é de R$ 500-R$ 1.000. A avaliação é de 4,5 estrelas e a localização é no centro do Rio de      
  Janeiro.                                                                                                                           
  * **Hotel Cipriani** (Intermediário)                                                                                               
  O Hotel Cipriani é um hotel intermediário localizado no coração do Rio de Janeiro. Oferece quartos confortáveis e um ambiente      
  elegante. A categoria é de intermediário e o preço médio é de R$ 200-R$ 400. A avaliação é de 4,5 estrelas e a localização é no    
  centro do Rio de Janeiro.                                                                                                          
  * **Ibis Rio de Janeiro** (Econômico)                                                                                              
  O Ibis Rio de Janeiro é um hotel econômico localizado no coração do Rio de Janeiro. Oferece quartos simples e um ambiente          
  prático. A categoria é de econômico e o preço médio é de R$ 100-R$ 200. A avaliação é de 4 estrelas e a localização é no centro    
  do Rio de Janeiro.                                                                                                                 
                                                                                                                                     
  ## 📚 Fontes                                                                                                                       
  TripAdvisor  
"""


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
    
def formatar_roteiro(texto: str) -> str:
    linhas_brutas = texto.split("\n")
    linhas_limpas = []
    buffer_texto = []

    for linha in linhas_brutas:
        l = linha.strip()
        if l.startswith(("#", "*", "-", "+", "•")) or not l:
            if buffer_texto:
                linhas_limpas.append(" ".join(buffer_texto))
                buffer_texto = []
            if l:
                linhas_limpas.append(l)
            else:
                linhas_limpas.append("")
        else:
            buffer_texto.append(l)
    
    if buffer_texto:
        linhas_limpas.append(" ".join(buffer_texto))

    resultado = []
    for linha in linhas_limpas:
        if not linha:
            resultado.append("")
            continue

        if linha.startswith("# ") or (linha.startswith("## ") and "Guia" in linha):
            titulo = linha.lstrip("#").strip()
            resultado.append(f"## {titulo}")

        elif linha.startswith("## "):
            titulo = linha.lstrip("#").strip()
            resultado.append(f"\n---\n### {titulo}")

        elif linha.startswith("### "):
            titulo = linha.lstrip("#").strip()
            resultado.append(f"\n**📅 {titulo}**")

        elif linha.startswith(("*", "-", "•")):
            linha_limpa = linha.lstrip("*-• ").replace("**", "").strip()
            partes = re.split(r' — | - | \(', linha_limpa, 1)
            
            if len(partes) > 1:
                nome = partes[0].strip()
                resto = partes[1].rstrip(")").strip()
                resultado.append(f"\n• **{nome}** ({resto})")
            else:
                resultado.append(f"\n• **{linha_limpa}**")

        else:
            linha_limpa = linha.replace("**", "").strip()
            resultado.append(f"\n{linha_limpa}")

    saida = "\n".join(resultado)
    saida = re.sub(r'\n{3,}', '\n\n', saida)
    
    return saida.strip()

USE_MOCK = True

crew = CompleteTravelCrew()


@cl.on_chat_start
async def start():
    cl.user_session.set("estado", "origem")
    cl.user_session.set("origem", "")
    cl.user_session.set("destino", "")
    cl.user_session.set("dias", 0)
    cl.user_session.set("ultimo_roteiro", "")
    cl.user_session.set("corpo_email", "")

    app_user = cl.user_session.get("user")
    nome = app_user.metadata['name']
    cl.user_session.set("nome_usuario", nome)

@cl.on_message
async def main(message: cl.Message):
    user_msg = message.content.strip()
    estado = cl.user_session.get("estado")

    if estado == "origem":
        loop = asyncio.get_event_loop()
        valida, motivo = await loop.run_in_executor(None, validar_entrada, "cidade_origem", user_msg)
        if not valida:
            await cl.Message(content=f"⚠️ {motivo}").send()
            return
        cl.user_session.set("origem", user_msg)
        cl.user_session.set("estado", "destino")
        await cl.Message(content="🏔️ Qual é o destino da sua viagem?").send()

    elif estado == "destino":
        loop = asyncio.get_event_loop()
        valida, motivo = await loop.run_in_executor(None, validar_entrada, "cidade_destino", user_msg)
        if not valida:
            await cl.Message(content=f"⚠️ {motivo}").send()
            return
        cl.user_session.set("destino", user_msg)
        cl.user_session.set("estado", "dias")
        await cl.Message(content="⏳ Quantos dias você pretende ficar?").send()

    elif estado == "dias":
        loop = asyncio.get_event_loop()
        valida, motivo = await loop.run_in_executor(None, validar_entrada, "dias", user_msg)
        if not valida:
            await cl.Message(content=f"⚠️ {motivo}").send()
            return
        try:
            dias = int(user_msg)
            cl.user_session.set("dias", dias)
            origem = cl.user_session.get("origem")
            destino = cl.user_session.get("destino")

            loader = cl.Message(content="Pesquisando e gerando seu roteiro")
            await loader.send()

            if USE_MOCK:
                await asyncio.sleep(4)
                roteiro_bruto = ROTEIRO_MOCK
                corpo_email = ROTEIRO_MOCK  # mock usa o mesmo conteúdo
            else:
                loop = asyncio.get_event_loop()
                resultado = await loop.run_in_executor(
                    None, crew.run, origem, destino, dias
                )
                roteiro_bruto = resultado["relatorio_destino"]
                corpo_email = resultado["corpo_email"]

            await loader.remove()

            roteiro_formatado = formatar_roteiro(roteiro_bruto)
            cl.user_session.set("ultimo_roteiro", roteiro_formatado)
            cl.user_session.set("corpo_email", corpo_email)

            msg = cl.Message(content="")
            await msg.send()

            palavras = roteiro_formatado.split(" ")
            buffer = ""
            for i, palavra in enumerate(palavras):
                buffer += palavra + " "
                if i % 5 == 0:
                    msg.content = buffer
                    await msg.update()
                    await asyncio.sleep(0.05)

            msg.content = roteiro_formatado
            await msg.update()

            cl.user_session.set("estado", "email")
            await cl.Message(
                content="✉️ Deseja receber este roteiro por e-mail? Se sim, digite seu e-mail."
            ).send()

        except ValueError:
            await cl.Message(content="⚠️ Por favor, digite um número válido de dias.").send()

    elif estado == "email":
        if "@" not in user_msg or "." not in user_msg:
            await cl.Message(content="⚠️ Por favor, digite um e-mail válido.").send()
            return

        corpo = cl.user_session.get("corpo_email")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, enviar_email, user_msg, "✈️ Seu Roteiro de Viagem está pronto!", corpo
        )
        await cl.Message(content="✅ Roteiro enviado com sucesso!").send()
        cl.user_session.set("estado", "origem")
        await cl.Message(content="🔄 Para planejar uma nova viagem, digite sua cidade de origem.").send()

    else:
        cl.user_session.set("estado", "origem")
        await cl.Message(
            content="⚠️ Não entendi. Por favor, digite sua cidade de origem."
        ).send()