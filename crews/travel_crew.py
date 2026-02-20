from crewai import Crew, Process
import unicodedata
import re
from dotenv import load_dotenv

from agents.travel_researcher import create_travel_researcher
from agents.guide_agent import create_guide_agent
from agents.flight_agent import create_flight_agent

from tasks.travel_research_tasks.structured_research_task import create_structured_research_task
from tasks.travel_research_tasks.guide_generation_task import create_guide_generation_task
from tasks.flight_task import create_flight_task

load_dotenv()


class CompleteTravelCrew:

    @staticmethod
    def remover_acentos(texto: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    @staticmethod
    def extrair_distancia_km(texto: str) -> float:
        texto_str = str(texto)

        match = re.search(r'"distancia_km"\s*:\s*"?(\d+[.,]?\d*)', texto_str)
        if match:
            valor = match.group(1).replace('.', '').replace(',', '.')
            return float(valor)

        matches = re.findall(r'(\d+[.,]?\d*)\s*km', texto_str, re.IGNORECASE)
        if matches:
            distancias = [float(m.replace('.', '').replace(',', '.')) for m in matches]
            return max(distancias)

        return 9999

    def run(self, origem: str, destino: str, dias: int, buscar_voos: bool = False, ida: str = None, volta: str = None):

        origem = self.remover_acentos(origem)
        destino = self.remover_acentos(destino)

        # PESQUISA
        researcher = create_travel_researcher()
        structured_task = create_structured_research_task(researcher, origem, destino, dias)

        crew_research = Crew(
            agents=[researcher],
            tasks=[structured_task],
            process=Process.sequential,
            verbose=True
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
            verbose=True
        )

        resultado_guia = crew_guide.kickoff()

        # VOOS (opcional, sem input())
        resultado_voos = None
        distancia = self.extrair_distancia_km(json_pesquisa)

        if distancia > 350 and buscar_voos and ida and volta:
            flight_agent = create_flight_agent()
            flight_task = create_flight_task(flight_agent, origem, destino, ida, volta)

            crew_flight = Crew(
                agents=[flight_agent],
                tasks=[flight_task],
                verbose=True
            )

            resultado_voos = crew_flight.kickoff()

        return {
            "relatorio_destino": resultado_guia.raw,
            "voos": resultado_voos.raw if resultado_voos else None,
            "distancia_km": distancia
        }