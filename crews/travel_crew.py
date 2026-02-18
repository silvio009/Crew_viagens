from crewai import Crew
import unicodedata
import re
from agents.travel_researcher import create_travel_researcher
from agents.flight_agent import create_flight_agent
from tasks.research_tasks import create_destination_research_task
from tasks.flight_task import create_flight_task

class CompleteTravelCrew:

    @staticmethod
    def remover_acentos(texto: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    @staticmethod
    def extrair_distancia_km(texto: str) -> float:
        matches = re.findall(r'(\d+[\.,]?\d*)\s*km', str(texto), re.IGNORECASE)
        if matches:
            distancias = [float(m.replace('.', '').replace(',', '.')) for m in matches]
            return max(distancias)
        return 9999  # se não encontrar, assume distância longa

    def run(self, origem: str, destino: str, dias: int):
        origem = self.remover_acentos(origem)
        destino = self.remover_acentos(destino)

        researcher = create_travel_researcher()
        research_task = create_destination_research_task(researcher, destino, dias, origem)

        crew_research = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )
        resultado_research = crew_research.kickoff()

        # Extrai a distância da resposta do LLM
        distancia = self.extrair_distancia_km(resultado_research)
        print(f"\nDistância identificada: {distancia:.0f} km")

        if distancia <= 350:
            print("\nEste destino é relativamente próximo. Recomendamos ir de carro ou transporte público, pois pode ser mais prático e econômico do que pegar um voo.")
            return {"relatorio_destino": resultado_research}

        resposta = input("\nDeseja buscar voos para este destino? (sim/não): ").strip().lower()
        if resposta != "sim":
            return {"relatorio_destino": resultado_research}

        ida = input("Data de ida (AAAA-MM-DD): ").strip()
        volta = input("Data de volta (AAAA-MM-DD): ").strip()

        flight_agent = create_flight_agent()
        flight_task = create_flight_task(
            flight_agent,
            origem,
            destino,
            ida,
            volta
        )

        crew_flight = Crew(
            agents=[flight_agent],
            tasks=[flight_task],
            verbose=True
        )
        resultado_voos = crew_flight.kickoff()

        return {
            "relatorio_destino": resultado_research,
            "voos": resultado_voos
        }