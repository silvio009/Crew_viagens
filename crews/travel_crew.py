from crewai import Crew, Process
import unicodedata
import re
from dotenv import load_dotenv

from agents.travel_researcher import create_travel_researcher
from agents.guide_agent import create_guide_agent 
from agents.flight_agent import create_flight_agent
from agents.email_agent import create_email_agent

from tasks.travel_research_tasks.structured_research_task import create_structured_research_task
from tasks.travel_research_tasks.guide_generation_task import create_guide_generation_task

from tasks.flight_task import create_flight_task
from tasks.email_task import create_email_task
from tools.email_tool import enviar_email

load_dotenv()


class CompleteTravelCrew:

    @staticmethod
    def remover_acentos(texto: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    @staticmethod
    def extrair_distancia_km(texto: str) -> float:
        texto_str = str(texto)

        match = re.search(r'"distancia_km"\s*:\s*"?(\\d+[\\.,]?\\d*)', texto_str)
        if match:
            valor = match.group(1).replace('.', '').replace(',', '.')
            return float(valor)

        matches = re.findall(r'(\\d+[\\.,]?\\d*)\\s*km', texto_str, re.IGNORECASE)
        if matches:
            distancias = [float(m.replace('.', '').replace(',', '.')) for m in matches]
            return max(distancias)

        return 9999

    def run(self, origem: str, destino: str, dias: int):

        origem = self.remover_acentos(origem)
        destino = self.remover_acentos(destino)


        # PESQUISA (70B)

        researcher = create_travel_researcher()

        structured_task = create_structured_research_task(
            researcher, origem, destino, dias
        )

        crew_research = Crew(
            agents=[researcher],
            tasks=[structured_task],
            process=Process.sequential,
            verbose=True
        )

        resultado_structured = crew_research.kickoff()

        json_pesquisa = resultado_structured.raw  


        # GERAÇÃO DO GUIA (8B)
  
        guide_agent = create_guide_agent()

        guide_task = create_guide_generation_task(
            agent=guide_agent,
            destino=destino,
            dias=dias,
            json_pesquisa=json_pesquisa  
        )

        crew_guide = Crew(
            agents=[guide_agent],
            tasks=[guide_task],
            process=Process.sequential,
            verbose=True
        )

        resultado_guia = crew_guide.kickoff()



        # DECISÃO SOBRE VOOS

        distancia = self.extrair_distancia_km(json_pesquisa)

        resultado_voos = None
        flight_task = None

        if distancia <= 350:
            print("\n🚗 Destino próximo. Recomendado carro ou transporte público.")
        else:
            resposta = input("\n✈️ Distância longa detectada. Deseja buscar voos? (sim/não): ").strip().lower()
            if resposta == "sim":
                ida = input("Data de ida (AAAA-MM-DD): ").strip()
                volta = input("Data de volta (AAAA-MM-DD): ").strip()

                flight_agent = create_flight_agent()
                flight_task = create_flight_task(flight_agent, origem, destino, ida, volta)

                crew_flight = Crew(
                    agents=[flight_agent],
                    tasks=[flight_task],
                    verbose=True
                )

                resultado_voos = crew_flight.kickoff()


        # ENVIO DE EMAIL

        enviar = input("\n📧 Deseja receber o roteiro por email? (sim/não): ").strip().lower()

        if enviar == "sim":
            email_usuario = input("Digite o seu email: ").strip()
            email_agent = create_email_agent()

            contexto_email = [resultado_guia.raw]
            if resultado_voos:
                contexto_email.append(resultado_voos.raw)

            email_task = create_email_task(
                agent=email_agent,
                destino=destino,
                dias=dias,
                context_tasks=contexto_email
            )

            crew_email = Crew(
                agents=[email_agent],
                tasks=[email_task],
                verbose=True
            )

            corpo_email_obj = crew_email.kickoff()
            corpo_final = corpo_email_obj.raw

            enviar_email(
                destinatario=email_usuario,
                assunto=f"✈️ Seu Roteiro para {destino} está pronto!",
                corpo=corpo_final
            )

        return {
            "relatorio_destino": resultado_guia.raw,
            "voos": resultado_voos.raw if resultado_voos else None
        }