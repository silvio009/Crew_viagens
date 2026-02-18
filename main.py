from crews.travel_crew import TravelCrew

if __name__ == "__main__":
    destino = input("Digite o destino da viagem: ")
    dias = int(input("Quantos dias você vai ficar? "))

    crew = TravelCrew()
    resultado = crew.run(destino, dias)

    print("\n=== RESULTADO ===\n")
    print(resultado)