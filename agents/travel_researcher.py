from crewai import Agent
from config.llm import get_research_llm
from tools.web_tools import get_search_tool

def create_travel_researcher():
    return Agent(
        role="Especialista em Pesquisa Turística",
        goal="Pesquisar dados reais e verificáveis usando ferramenta de busca.",
        backstory="""
        Você é um pesquisador turístico profissional.
        Sua reputação depende de dados reais, verificáveis e atualizados.
        Você sempre utiliza ferramentas de busca antes de responder.
        Você nunca inventa fontes.
        """,
        tools=[get_search_tool()],
        verbose=True,
        memory=False,
        max_iter=5,
        allow_delegation=False,
        llm=get_research_llm()
    )