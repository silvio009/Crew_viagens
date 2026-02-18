from crewai import Crew
from agents.travel_researcher import create_travel_researcher
from agents.flight_agent import create_flight_agent
from tasks.research_tasks import create_destination_research_task
from tasks.flight_task import create_flight_task

class CompleteTravelCrew:
    def run(self, origem: str, destino: str, dias: int):

        researcher = create_travel_researcher()
        research_task = create_destination_research_task(researcher, destino, dias,origem)

        crew_research = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )
        resultado_research = crew_research.kickoff()

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