from crewai import Task

def create_guide_generation_task(agent, destino, dias, json_pesquisa):
    """
    Cria uma Task para gerar um guia de viagem fluido, aproveitando todos os dados do JSON.
    """
    return Task(
        description=f"""
Você receberá dados estruturados reais sobre {destino}.
s
DADOS:
{json_pesquisa}

Sua missão é transformar esses dados em um guia de viagem fluido,
envolvente e profissional, escrito em Markdown.

REGRAS OBRIGATÓRIAS:

1. Use todas as informações presentes nos dados de forma narrativa.
2. Não invente informações.
3. Se algum campo estiver ausente, escreva "Informação não disponível".
4. Não mencione que recebeu um JSON.
5. Não explique o processo.
6. Não use ferramentas externas.

IMPORTANTE:
- Reescreva de forma natural e elegante.
- Inclua detalhes como tempo médio de visita, avaliações, faixa de preço, diferenciais de restaurantes, categorias de hotéis, motivos de visita.
- Evite repetições e estrutura mecânica.
- Conecte informações de forma narrativa, mostrando valor de cada atração, restaurante e hotel.

ESTRUTURA OBRIGATÓRIA:

## Guia Completo de Viagem: {destino}

## 📍 Visão Geral
Apresente o destino de forma fluida, incluindo distância,
tempo médio e principais rotas de maneira natural.

## 🚗 Como Chegar
Explique as rotas e o deslocamento em formato descritivo.

## 🗺️ Roteiro Sugerido para {dias} Dias
Distribua as atrações de forma estratégica entre os dias.
Descreva cada atração em parágrafos curtos, incluindo:
- Nome do local em negrito
- Tempo médio de visita
- Motivo de visita
- Qualquer detalhe interessante dos dados

## 🍽️ Onde Comer
Descreva os restaurantes incluindo:
- Nome em negrito
- Tipo de comida
- Diferencial do local
- Faixa de preço
- Avaliação
Tudo em 2–3 linhas de texto fluido.

## 🏨 Onde Ficar
Descreva os hotéis incluindo:
- Nome em negrito
- Categoria (Econômico/Intermediário/Luxo)
- Preço médio por noite
- Localização e avaliação
- Ao final de cada hotel, adicione o link:
  🔗 [Ver preços no Google Hotels](https://www.google.com/travel/hotels?q=NOME_DO_HOTEL+{destino})
  Substitua NOME_DO_HOTEL pelo nome real do hotel com espaços trocados por +
  Exemplo: Hotel Fasano → https://www.google.com/travel/hotels?q=Hotel+Fasano+Rio+de+Janeiro
Tudo em 2–3 linhas de texto fluido.

## 📚 Fontes
Liste apenas os nomes das fontes presentes nos dados.

FORMATAÇÃO:
- Markdown correto
- Use negrito apenas para nomes de locais
- Texto claro, fluido e profissional

Produza um guia com tom editorial, como se fosse de uma agência de turismo.
""",
        expected_output="Guia fluido e profissional em Markdown.",
        agent=agent
    )