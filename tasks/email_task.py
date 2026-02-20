from crewai import Task

def create_email_task(agent, destino: str, dias: int, context_tasks: list):
    conteudo_completo = "\n\n".join(context_tasks)
    
    return Task(
        description=f"""
Você é o Consultor Premium da **TravelCrew Agency**. Sua missão é transformar o guia de viagem
completo em um email elegante e profissional para o viajante.

CONTEÚDO DO GUIA E VOOS:
{conteudo_completo}

⚡ INSTRUÇÕES IMPORTANTES:
- Mantenha **100% do conteúdo do guia**, incluindo todas as seções.
- Se houver informações de voo, insira-as na seção de Logística.
- Não invente informações ou altere os dados existentes.
- Use apenas Markdown, sem blocos de código.

ESTRUTURA DO EMAIL:

Prezado(a) Viajante,

[Boas-vindas curtas e elegantes]

## ✈️ SEU ROTEIRO PERSONALIZADO — {destino} ({dias} dias)

[Insira aqui todo o conteúdo do guia]

## 💡 DICAS EXCLUSIVAS DA NOSSA EQUIPE

1. [Dica 1 breve]
2. [Dica 2 breve]
3. [Dica 3 breve]


## 💰 ESTIMATIVA DE CUSTOS (VALORES REFERENCIAIS)

| Item | Estimativa |
|------|-----------|
| Acomodação | [Valor extraído do guia"] |
| Alimentação | [Valor sugerido por dia baseado nos restaurantes do guia] |
| Transporte | [Valor sugerido"] |
| Atrações | [Soma dos custos das atrações ou "Gratuito/Sob consulta"] |
| **Total estimado** | **[Soma total para {dias} dia(s)]** |



 faça um pequeno Parágrafo de fechamento

**Atenciosamente,**  
**Equipe TravelCrew Agency**  
📧 contato@travelcrew.com.br | 🌐 [www.travelcrew.com](https://www.travelcrew.com)
""",
        agent=agent,
        expected_output="Email completo em Markdown, profissional, mantendo 100% do conteúdo do guia e links originais."
    )