from crewai import Task

def create_flight_task(agent, origem, destino, ida, volta):
    return Task(
        description=f"""
        O usuário quer viajar de {origem} para {destino}.

        Datas:
        Ida: {ida}
        Volta: {volta}

        PASSOS OBRIGATÓRIOS:

        1. Buscar aeroportos próximos da cidade de origem
        2. Escolher melhor aeroporto
        3. Buscar voos de ida e volta
        4. Retornar opções organizadas

        Seja claro e estruturado.
        """,
        expected_output="Lista de voos com preços",
        agent=agent
    )