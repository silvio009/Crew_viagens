from crewai import Task


def create_destination_research_task(agent, destination: str):

    description = f"""
    Pesquisar profundamente o destino: {destination}.

    Inclua obrigatoriamente:

    - Principais atrações culturais
    - Experiências locais autênticas
    - Logística de transporte
    - Dicas práticas para viajantes
    - Recomendações estratégicas

    Priorize precisão, clareza e utilidade.
    """

    return Task(
        description=description,
        expected_output="""
        Relatório estruturado em markdown com seções claras:

        ## Visão Geral
        ## Atrações Principais
        ## Experiências Locais
        ## Logística
        ## Recomendações
        """,
        agent=agent
    )