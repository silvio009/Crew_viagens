from crewai import Crew
from agents.travel_researcher import create_travel_researcher
from tasks.research_tasks import create_destination_research_task


class TravelCrew:
    def run(self, destination: str):

        researcher = create_travel_researcher()

        research_task = create_destination_research_task(
            researcher,
            destination
        )

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )

        return crew.kickoff()