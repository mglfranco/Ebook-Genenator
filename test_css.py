from api.pdf_engine import generate_pdf
import os

os.makedirs("output", exist_ok=True)

chapters1 = [{"title": "Business 101", "content": "Paragrafo corporativo focado em produtividade."}]
generate_pdf("Teste Corporativo", "Autor", "Corporativo Clean", chapters1, [None], "output/test_corporate_root.pdf")

chapters2 = [{"title": "O Relogio Mágico", "content": "Apenas um paragrafo vintage. Teste de tipografia Palatino."}]
generate_pdf("Teste Vintage", "Autor QA", "Vintage / Retrô", chapters2, [None], "output/test_vintage_root.pdf")

print("Gerados com sucesso!")
