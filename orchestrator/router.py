from crews.travel_crew import TravelCrew

class Router:
    def route(self, user_input: str):
        if "viagem" in user_input.lower():
            crew = TravelCrew()
            return crew.run(user_input)

        return "Não entendi a solicitação."