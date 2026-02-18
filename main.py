from crews.travel_crew import CompleteTravelCrew

if __name__ == "__main__":
    print("=== Planejador de Viagens ===\n")

    origem = input("Digite a cidade de origem: ").strip()
    destino = input("Digite a cidade de destino: ").strip()
    dias = int(input("Quantos dias você pretende ficar? ").strip())

    crew = CompleteTravelCrew()
    resultado = crew.run(origem, destino, dias)

    print("\n=== RESULTADO FINAL ===\n")
    
    print("📍 Relatório do destino:\n")
    print(resultado["relatorio_destino"])


    if "voos" in resultado:
        print("\n✈️ Opções de voos:\n")
        print(resultado["voos"])