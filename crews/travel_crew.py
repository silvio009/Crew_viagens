from crewai import Crew
from agents.travel_researcher import create_travel_researcher
from tasks.research_tasks import create_destination_research_task

class TravelCrew:
    def run(self, destination: str, days: int):

        researcher = create_travel_researcher()

        research_task = create_destination_research_task(
            researcher,
            destination,
            days
        )

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )

        return crew.kickoff()