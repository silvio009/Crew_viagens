from crewai import Task

def create_email_task(agent, destino: str, dias: int, context_tasks: list):
    return Task(
        description=f"""
        Você é o Consultor Premium da **TravelCrew Agency**. Sua missão é transformar dados brutos de pesquisa em um email de luxo.

        USE O CONTEXTO RECEBIDO:
        Extraia as informações reais (distâncias, links de fontes e atrações) do relatório do agente pesquisador.
        Se houver informações de voos no contexto, inclua-as na seção de Logística.

        REGRAS DE OURO:
        1. **MANTENHA OS LINKS:** Sempre que citar uma atração, mantenha o link da fonte (TripAdvisor, Google Maps) que o pesquisador encontrou.
        2. **SEM ALUCINAÇÕES:** Não invente preços. Se o pesquisador não forneceu um valor exato, use "A consultar" ou uma faixa de preço estimada (Ex: R$ 150 - R$ 300).
        3. **MARKDOWN PURO:** Use apenas Markdown. Não use blocos de código (```).

        ESTRUTURA DO EMAIL:

        Prezado(a) Viajante,

        [Parágrafo curto e elegante de boas-vindas, máximo 3 linhas]

        ---

        ## ✈️ SEU ROTEIRO PERSONALIZADO — {destino} ({dias} dias)

        ### 📅 Dia 1
        - **Manhã:** [atividade baseada na pesquisa]
        - **Tarde:** [atividade baseada na pesquisa]
        - **Noite:** [atividade baseada na pesquisa]

        ### 📅 Dia 2
        - **Manhã:** [atividade baseada na pesquisa]
        - **Tarde:** [atividade baseada na pesquisa]
        - **Noite:** [atividade baseada na pesquisa]

        [Adicione Dia 3 se houver no contexto]

        ---

        ## 🏛️ PRINCIPAIS ATRAÇÕES (COM FONTES REAIS)

        - **[Nome da atração]:** [descrição curta] - [Link da Fonte]
        - **[Nome da atração]:** [descrição curta] - [Link da Fonte]

        ---

        ## 🍽️ GASTRONOMIA E EXPERIÊNCIAS LOCAIS

        - **[Experiência]:** [descrição curta baseada na cultura local pesquisada]

        ---

        ## 🚗 LOGÍSTICA E DESLOCAMENTO

        - **Origem/Destino:** [Cite a distância real encontrada de ~1568km]
        - **Transporte Sugerido:** [Explique sobre voo + transfer se for longe]
        - **Locomoção Local:** [Dica de aluguel de carro ou transfer]

        ---

        ## 💡 DICAS EXCLUSIVAS DA NOSSA EQUIPE

        1. **[Dica 1]:** [Ex: Melhor horário para evitar multidões]
        2. **[Dica 2]:** [Ex: Dica sobre o clima ou vestimenta]
        3. **[Dica 3]:** [Ex: Segurança ou moeda]

        ---

        ## 💰 ESTIMATIVA DE CUSTOS (VALORES REFERENCIAIS)

        | Item | Estimativa |
        |------|-----------|
        | Acomodação | [Valor ou "Sob consulta"] |
        | Alimentação | [Valor sugerido por dia] |
        | Transporte | [Valor sugerido] |
        | Atrações | [Soma dos custos das atrações] |
        | **Total estimado** | **[Soma Total]** |

        ---

        [Parágrafo de fechamento elegante convidando ao contato]

        **Atenciosamente,**

        **Equipe TravelCrew Agency**
        📧 contato@travelcrew.com.br | 🌐 [www.travelcrew.com](https://www.travelcrew.com).br
        """,
        agent=agent,
        context=context_tasks,
        expected_output="Corpo do email em Markdown puro, profissional, com links reais e tabela de custos preenchida."
    )