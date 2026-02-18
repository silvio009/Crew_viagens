from amadeus import Client
import os
from crewai.tools import tool

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

def buscar_aeroportos(cidade: str) -> str:
    """
    Busca os aeroportos mais próximos da cidade informada usando a API Amadeus.

    Parâmetros:
    - cidade (str): Nome da cidade para busca de aeroportos.

    Retorna:
    - str: Lista de até 5 aeroportos encontrados com nome e código IATA.
    """
    try:
        response = amadeus.reference_data.locations.get(
            keyword=cidade,
            subType="AIRPORT"
        )
        aeroportos = [f"{a['name']} ({a['iataCode']})" for a in response.data[:5]]
        return "Aeroportos encontrados:\n" + "\n".join(aeroportos)
    except Exception as e:
        return f"Erro ao buscar aeroportos: {e}"