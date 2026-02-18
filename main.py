from dotenv import load_dotenv
from crews.travel_crew import TravelCrew

# Carrega variáveis de ambiente
load_dotenv()

if __name__ == "__main__":

    destination = input("Digite o destino da viagem: ")

    crew = TravelCrew()
    result = crew.run(destination)

    print("\n=== RESULTADO ===\n")
    print(result)