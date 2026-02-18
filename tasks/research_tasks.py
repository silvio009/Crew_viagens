from crewai import Task

def create_destination_research_task(agent, destination, days):
    return Task(
        description=f"""
        Use a ferramenta de busca web intensivamente.

        Produza um relatório estratégico profissional para {destination}
        ({days} dias).

        OBRIGATÓRIO:

        - Pesquisar cidades e atrações num raio de 50km
        - Identificar atrações turísticas reais e verificáveis
        - Priorizar experiências culturais locais
        - Evitar descrições genéricas de resort
        - Validar cada atração com busca web

        Para cada atração informe:

        - distância a partir do hotel
        - tempo médio de visita
        - melhor horário
        - custo estimado
        - alternativa em caso de chuva

        Se a atração estiver fora do destino principal,
        explique a logística de deslocamento.

        Estruture:

        1. Roteiro dia a dia com horários sugeridos
        2. Atrações reais com contexto
        3. Experiências autênticas locais
        4. Logística prática
        5. Recomendações estratégicas

        Não invente informações.
        Seja específico.
        Pense como um planejador de viagem profissional.
        """,
        expected_output="Relatório estratégico detalhado em markdown",
        agent=agent
    )