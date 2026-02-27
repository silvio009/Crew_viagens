# TravelCrew Agency

Plataforma de planejamento de viagens com **agentes de IA colaborativos**, interface conversacional em **Chainlit**, autenticação de usuários e envio automático do roteiro por e-mail em formato profissional.

---

## Sumário

- [Visão geral](#visão-geral)
- [Principais funcionalidades](#principais-funcionalidades)
- [Arquitetura da solução](#arquitetura-da-solução)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Stack tecnológica](#stack-tecnológica)
- [Pré-requisitos](#pré-requisitos)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Como executar o projeto](#como-executar-o-projeto)
- [Fluxo funcional da aplicação](#fluxo-funcional-da-aplicação)
- [Módulos principais](#módulos-principais)
- [Banco de dados e autenticação](#banco-de-dados-e-autenticação)
- [Integrações externas](#integrações-externas)
- [Boas práticas e observações de produção](#boas-práticas-e-observações-de-produção)
- [Solução de problemas](#solução-de-problemas)
- [Roadmap sugerido](#roadmap-sugerido)

---

## Visão geral

O **TravelCrew Agency** é um sistema orientado a agentes que transforma uma conversa com o usuário em um **roteiro completo de viagem**. O fluxo combina pesquisa de dados, geração editorial do guia e composição de e-mail corporativo.

A aplicação foi construída para oferecer:

- experiência conversacional para coleta de dados da viagem;
- validação de destino, quantidade de dias e datas de ida/volta;
- geração automatizada de guia em Markdown com sugestões de atrações, restaurantes e hotéis;
- envio do conteúdo final por e-mail com template HTML estilizado;
- painel visual complementar de clima por período na interface.

---

## Principais funcionalidades

- **Autenticação com usuário e senha** (persistência em SQLite).
- **Cadastro de conta** em rota dedicada (`/registro`) com UI customizada.
- **Coleta guiada dos parâmetros da viagem** via chat (origem, destino, dias, datas).
- **Validação de cidades** usando Nominatim/OpenStreetMap.
- **Pipeline com múltiplos agentes CrewAI**:
  - Agente pesquisador (coleta dados factuais);
  - Agente redator (cria guia fluido);
  - Agente de comunicação (monta e-mail final).
- **Envio de e-mail automático** via SMTP (Gmail SSL).
- **Widget de clima** para o período informado (OpenWeather API).
- **Customização visual da UI Chainlit** (CSS e JS próprios).

---

## Arquitetura da solução

A execução principal acontece em `app.py`, que integra:

1. **Camada de interface** (Chainlit + assets em `public/`);
2. **Camada de orquestração de agentes** (`CompleteTravelCrew`);
3. **Camada de persistência/autenticação** (SQLite);
4. **Camada de integração externa** (busca web, clima, envio de e-mail).

### Pipeline de agentes

1. **Pesquisa estruturada**: coleta logística + experiência do destino e retorna JSON.
2. **Geração de guia**: converte JSON em documento editorial em Markdown.
3. **Geração de e-mail**: reutiliza o guia e adapta para mensagem profissional.

Esse encadeamento garante separação de responsabilidades e facilita evolução dos prompts/tarefas por módulo.

---

## Estrutura do projeto

```text
Crew_viagens/
├── app.py                                  # Entrada principal da aplicação (Chainlit + fluxo de chat)
├── main.py                                 # Execução local simples via terminal
├── registro_app.py                         # App FastAPI para cadastro de usuários
├── insert.py                               # Script utilitário para inserir usuário no SQLite
├── requirements.txt                        # Dependências Python
├── Readme.md                               # Documentação do projeto
│
├── agents/
│   ├── travel_researcher.py                # Agente de pesquisa
│   ├── guide_agent.py                      # Agente gerador de guia
│   └── email_agent.py                      # Agente redator de e-mail
│
├── tasks/
│   ├── email_task.py                       # Prompt/tarefa para composição do e-mail
│   └── travel_research_tasks/
│       ├── structured_research_task.py     # Prompt/tarefa de pesquisa estruturada
│       └── guide_generation_task.py        # Prompt/tarefa de geração do guia
│
├── crews/
│   └── travel_crew.py                      # Orquestração sequencial dos agentes
│
├── tools/
│   ├── web_tools.py                        # Integra ferramenta de busca (Serper)
│   └── email_tool.py                       # Envio de e-mail com HTML + Markdown
│
├── config/
│   └── llm.py                              # Configuração dos modelos LLM (Groq)
│
├── memory/
│   └── context_store.py                    # Stub para camada futura de memória
│
├── orchestrator/
│   └── router.py                           # Esboço de roteamento de intenção
│
├── public/
│   ├── app.js                              # Scripts de UI, clima e melhorias de UX
│   ├── style.css                           # Estilos customizados da interface
│   ├── favicon.png                         # Ícone da aplicação
│   └── logo_name.png                       # Identidade visual
│
└── chainlit.md                             # Tela de boas-vindas do Chainlit
```

---

## Stack tecnológica

- **Python 3.10+**
- **Chainlit** (UI conversacional)
- **CrewAI** e **CrewAI Tools** (agentes e ferramentas)
- **Groq API** (LLMs para pesquisa e geração)
- **FastAPI / Starlette / Uvicorn** (rota de registro e middleware)
- **SQLite** (persistência de usuários)
- **SMTP Gmail + Markdown** (envio de e-mail em texto e HTML)
- **OpenWeather API** (previsão de clima)
- **Nominatim (OpenStreetMap)** (validação de cidades)

---

## Pré-requisitos

Antes de iniciar, garanta:

- Python instalado (recomendado 3.10 ou superior);
- acesso à internet para APIs externas;
- chave válida da Groq;
- chave válida da OpenWeather;
- credenciais SMTP para disparo de e-mail.

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com as variáveis abaixo:

```env
# LLM (Groq)
GROQ_API_KEY=...

# Busca web (Serper)
SERPER_API_KEY=...

# Clima
OPENWEATHER_API_KEY=...

# E-mail
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA=sua_senha_ou_app_password
```

> Observação: para Gmail, use preferencialmente **App Password** com verificação em duas etapas.

---

## Como executar o projeto

### 1) Instalar dependências

```bash
pip install -r requirements.txt
```

### 2) Iniciar a aplicação

```bash
chainlit run app.py -w
```

- O Chainlit iniciará a interface web.
- A rota de cadastro (`/registro`) é tratada na mesma execução via middleware/servidor auxiliar já configurado.

### 3) Acessar no navegador

Use a URL exibida no terminal (normalmente `http://localhost:8000`).

---

## Fluxo funcional da aplicação

1. Usuário autentica com login/senha.
2. Sistema solicita origem, destino e dias.
3. Sistema valida cidade e número de dias.
4. Sistema solicita data de ida e data de volta.
5. Aplicação gera `public/config.js` com parâmetros necessários ao front (clima).
6. Orquestrador (`CompleteTravelCrew`) executa os três estágios de agentes.
7. Resultado é formatado e exibido progressivamente no chat.
8. Usuário informa e-mail para receber o roteiro.
9. Sistema envia versão elegante em HTML + texto alternativo.

---

## Módulos principais

### `app.py`

- Configura middleware para cadastro em `/registro`.
- Inicializa/garante tabela `usuarios` no SQLite.
- Implementa autenticação (`@cl.password_auth_callback`).
- Controla estado conversacional com `cl.user_session`.
- Executa pipeline de IA de forma assíncrona.
- Publica dados para o front consumir clima por período.

### `crews/travel_crew.py`

- Define a classe `CompleteTravelCrew`.
- Remove acentos de origem/destino para robustez de busca.
- Orquestra três crews sequenciais:
  1. pesquisa,
  2. geração de guia,
  3. composição de e-mail.

### `agents/` e `tasks/`

- Encapsulam papéis de agentes e instruções de output.
- Separação facilita manutenção de prompt engineering por etapa.
- Tarefa de pesquisa força retorno em JSON válido e com limites de itens.

### `tools/email_tool.py`

- Converte Markdown em HTML.
- Aplica template visual corporativo.
- Envia mensagem multipart (texto + HTML) via SMTP SSL.

### `public/app.js` e `public/style.css`

- Ajustam experiência visual do Chainlit.
- Injetam componentes e comportamentos personalizados.
- Buscam clima por destino e período informado.

---

## Banco de dados e autenticação

### Banco

- Banco local: `usuarios.db`.
- Tabela principal: `usuarios`.
- Campos: `id`, `username`, `password_hash`, `name`, `role`.

### Segurança aplicada

- Senhas são armazenadas com hash SHA-256.

### Ponto de atenção

- Para ambiente de produção, recomenda-se evoluir para:
  - hash forte com salt (ex.: `bcrypt`/`argon2`);
  - gestão de sessão/token;
  - hardening de validação e limitação de tentativas.

---

## Integrações externas

- **Groq**: inferência LLM para pesquisa e geração textual.
- **Serper**: mecanismo de busca web usado pelo agente pesquisador.
- **OpenWeather**: previsão e clima atual para o destino.
- **Nominatim**: validação de cidades de origem/destino.
- **SMTP Gmail**: entrega do roteiro por e-mail.

---

## Boas práticas e observações de produção

- Isolar segredos com `.env` e cofre de segredos em produção.
- Implementar logs estruturados para observabilidade.
- Adicionar testes automatizados para funções críticas (validação, auth, parser).
- Tratar rate limits e indisponibilidades das APIs externas.
- Substituir SQLite por banco gerenciado em cenários de escala.
- Versionar prompts com estratégia de avaliação contínua.

---

## Solução de problemas

### Erro de autenticação ou login

- Verifique se o usuário existe no banco `usuarios.db`.
- Use `insert.py` para inserir usuário de teste (se necessário).

### E-mail não enviado

- Confirme `EMAIL_REMETENTE` e `EMAIL_SENHA`.
- Para Gmail, valide App Password e bloqueios de segurança.

### Clima não aparece na interface

- Verifique `OPENWEATHER_API_KEY`.
- Confirme se destino e datas foram capturados corretamente no fluxo.

### Respostas de IA incompletas

- Cheque `GROQ_API_KEY` e `SERPER_API_KEY`.
- Observe eventuais limites de uso das APIs.

---

