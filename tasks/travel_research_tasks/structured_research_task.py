from crewai import Task

def create_structured_research_task(agent, origem, destino, dias):
    return Task(
        description=f"""
Você deve utilizar a ferramenta de busca NO MÁXIMO DUAS VEZES.

⚠️ REGRA CRÍTICA:
- Não faça mais de 2 chamadas de busca.
- Não faça buscas adicionais.
- Não explique o que está fazendo.

BUSCA 1 (logística):
Pesquise em uma única consulta:
- Distância entre {origem} e {destino}
- Tempo médio de deslocamento
- Principais rotas rodoviárias utilizadas

BUSCA 2 (experiência):
Pesquise em uma única consulta:
- 5 principais atrações turísticas em {destino}
- 5 restaurantes bem avaliados
- 3 hotéis (1 econômico, 1 intermediário, 1 luxo)

Priorize:
- Sites oficiais
- Google Maps
- TripAdvisor
- Booking
- Guias reconhecidos

LIMITE DE ITENS (OBRIGATÓRIO):
- Máximo 5 atrações
- Máximo 5 restaurantes
- Máximo 3 hotéis

RETORNE EXCLUSIVAMENTE UM JSON VÁLIDO NO FORMATO:

{{
  "distancia_km": "",
  "tempo_medio": "",
  "principais_rotas": "",
  "atracoes": [
    {{
      "nome": "",
      "descricao_curta": "",
      "motivo_visita": "",
      "tempo_medio_visita": "",
      "fonte": ""
    }}
  ],
  "restaurantes": [
    {{
      "nome": "",
      "tipo": "",
      "avaliacao": "",
      "faixa_preco": "",
      "diferencial": "",
      "fonte": ""
    }}
  ],
  "hoteis": [
    {{
      "nome": "",
      "categoria": "",
      "preco_medio": "",
      "avaliacao": "",
      "localizacao": "",
      "fonte": ""
    }}
  ]
}}

========================
REGRAS FINAIS:
- Não use Markdown
- Não escreva explicações
- Não escreva texto antes ou depois do JSON
- Não inclua comentários
- Se não encontrar algum dado, escreva "Informação não disponível"
- O JSON deve ser válido e parseável

Retorne apenas o JSON.
""",
        expected_output="JSON estruturado completo e válido.",
        agent=agent
    )