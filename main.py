from crews.travel_crew import CompleteTravelCrew

if __name__ == "__main__":
    print("=== Planejador de Viagens ===\n")

    # Origem e destino fixos
    origem = "São Paulo"
    destino = "Campos do Jordão"
    dias = int(input("Quantos dias você pretende ficar? ").strip())

    crew = CompleteTravelCrew()
    resultado = crew.run(origem, destino, dias)

    print("\n=== RESULTADO FINAL ===\n")
    
    print("Relatório do destino:\n")
    print(resultado["relatorio_destino"])

    if resultado.get("voos"):
        print("\nOpções de voos:\n")
        print(resultado["voos"])