from crewai import Agent
from config.llm import get_generation_llm

def create_guide_agent():
    return Agent(
        role="Redator de Guia Turístico",
        goal="Transformar dados estruturados em guia organizado",
        backstory="Especialista em transformar dados em conteúdo claro e profissional.",
        llm=get_generation_llm(),
        verbose=True
    )