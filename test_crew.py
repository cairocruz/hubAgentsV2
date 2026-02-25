import os
import logging
logging.basicConfig(level=logging.DEBUG)
os.environ["CREWAI_DEBUG"] = "true"
from agents.risk_analysis_crew import RiskAnalysisCrew

responses = [
    "Ele me xingou algumas vezes durante discussões",
    "Sim, ele quebrou objetos na casa quando ficou irritado",
    "Ele não gosta quando eu saio com minhas amigas",
    "Tenho uma amiga próxima que me apoia",
    "Estou preocupada com o comportamento dele ultimamente"
]

try:
    print("Testando RiskAnalysisCrew...")
    crew = RiskAnalysisCrew(responses=responses)
    result = crew.kickoff()
    print("Sucesso!")
    print(result)
except Exception as e:
    import traceback
    traceback.print_exc()
