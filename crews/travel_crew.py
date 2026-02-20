from crewai import Crew, Process
import unicodedata
import re
from dotenv import load_dotenv

from agents.travel_researcher import create_travel_researcher
from agents.guide_agent import create_guide_agent
from agents.email_agent import create_email_agent

from tasks.travel_research_tasks.structured_research_task import create_structured_research_task
from tasks.travel_research_tasks.guide_generation_task import create_guide_generation_task
from tasks.email_task import create_email_task

load_dotenv()


class CompleteTravelCrew:

    @staticmethod
    def remover_acentos(texto: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    def run(self, origem: str, destino: str, dias: int):

        origem = self.remover_acentos(origem)
        destino = self.remover_acentos(destino)

        # PESQUISA
        researcher = create_travel_researcher()
        structured_task = create_structured_research_task(researcher, origem, destino, dias)

        crew_research = Crew(
            agents=[researcher],
            tasks=[structured_task],
            process=Process.sequential,
            verbose=False
        )

        resultado_structured = crew_research.kickoff()
        json_pesquisa = resultado_structured.raw

        # GERAÇÃO DO GUIA
        guide_agent = create_guide_agent()
        guide_task = create_guide_generation_task(
            agent=guide_agent,
            destino=destino,
            dias=dias,
            json_pesquisa=json_pesquisa
        )

        crew_guide = Crew(
            agents=[guide_agent],
            tasks=[guide_task],
            process=Process.sequential,
            verbose=False
        )

        resultado_guia = crew_guide.kickoff()

        # EMAIL
        email_agent = create_email_agent()
        email_task = create_email_task(
            agent=email_agent,
            destino=destino,
            dias=dias,
            context_tasks=[resultado_guia.raw]
        )

        crew_email = Crew(
            agents=[email_agent],
            tasks=[email_task],
            process=Process.sequential,
            verbose=False
        )

        resultado_email = crew_email.kickoff()

        return {
            "relatorio_destino": resultado_guia.raw,
            "corpo_email": resultado_email.raw,
        }