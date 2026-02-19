from crewai import Agent
from config.llm import get_generation_llm
from crewai.tools import tool

from tools.airports_tool import buscar_aeroportos

@tool
def aeroportos_tool(cidade: str) -> str:
    """
    Busca os aeroportos mais próximos de uma cidade fornecida.

    Parâmetros:
    - cidade (str): Nome da cidade para buscar aeroportos próximos.

    Retorna:
    - str: Lista de aeroportos encontrados.
    """
    return buscar_aeroportos(cidade)



def create_flight_agent():
    return Agent(
        role="Especialista em Passagens Aéreas",
        goal="""
        Encontrar os melhores voos disponíveis
        com base na cidade de origem,
        destino e datas.
        """,
        backstory="""
        Especialista em logística aérea e
        busca de passagens internacionais.
        """,
        tools=[aeroportos_tool],
        llm=get_generation_llm(),
        verbose=True,
        allow_delegation=False
    )