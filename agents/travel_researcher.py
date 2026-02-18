from crewai import Agent
from config.llm import get_llm

def create_travel_researcher():

    return Agent(
        role="Especialista em Planejamento de Viagens Internacionais",
        goal="""
        Produzir pesquisas precisas e atualizadas.
        Priorizar eficiência, autenticidade cultural
        e experiência do usuário.
        """,
        backstory="""
        Consultor de turismo global com 15 anos
        de experiência em planejamento estratégico.
        """,
        llm=get_llm(),
        verbose=False,
        allow_delegation=False
    )