import requests
import whois
from datetime import datetime
import re
import time

def analisar_url(url):
    resultado = {
        "url": url,
        "score": 100,
        "nivel": "Seguro",
        "avisos": []
    }

    print(f"\n🔍 Escaneando: {url}")
    print("=" * 50)

    # 1. Checa idade do domínio
    try:
        dominio = re.findall(r'https?://([^/]+)', url)[0]
        print(f"Verificando domínio: {dominio}")
        w = whois.whois(dominio)

        data_criacao = w.creation_date
        if isinstance(data_criacao, list):
            data_criacao = data_criacao[0]

        dias = (datetime.now() - data_criacao).days
        print(f"Domínio criado há {dias} dias")

        if dias < 30:
            resultado["score"] -= 50
            resultado["avisos"].append(f"DOMÍNIO NOVO: Criado há {dias} dias. Golpista ama domínio novo.")
        elif dias < 90:
            resultado["score"] -= 20
            resultado["avisos"].append(f"Domínio recente: {dias} dias.")
    except Exception as e:
        resultado["score"] -= 20
        resultado["avisos"].append("Não consegui ver idade do domínio. Suspeito.")

    # 2. Palavras de golpe no site
    try:
        print("Analisando conteúdo do site...")
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        texto = r.text.lower()
        golpes = ["ganhe dinheiro rápido", "lucro garantido", "método secreto", "vagas limitadas", "últimas horas", "clique aqui", "investimento sem risco"]
        for palavra in golpes:
            if palavra in texto:
                resultado["score"] -= 25
                resultado["avisos"].append(f'Termo suspeito encontrado: "{palavra}"')
    except:
        resultado["score"] -= 15
        resultado["avisos"].append("Site demorou pra responder ou bloqueou. Estranho.")

    # 3. Checa HTTPS
    if not url.startswith("https://"):
        resultado["score"] -= 30
        resultado["avisos"].append("Site sem HTTPS. Dados não criptografados.")

    # 4. Score final
    if resultado["score"] < 40:
        resultado["nivel"] = "PERIGO - Provável Golpe"
    elif resultado["score"] < 70:
        resultado["nivel"] = "ATENÇÃO - Suspeito"

    return resultado

# Versão 1.1 - Loop infinito
if __name__ == "__main__":
    print("🔵 BEM-VINDO AO GOLPERADAR v1.1 - DONOLAXP SECURITY 🔵")
    print("Digite 'sair' para encerrar o programa\n")

    while True:
        url_teste = input("Cole a URL pra testar: ")

        if url_teste.lower() == 'sair':
            print("\nEncerrando GolpeRadar. Valeu, DONOLAXP! 🚗💙")
            break

        if not url_teste.startswith(('http://', 'https://')):
            url_teste = 'https://' + url_teste
            print(f"Adicionando https:// → {url_teste}")

        resultado = analisar_url(url_teste)

        print("\n" + "=" * 50)
        if resultado["score"] >= 70:
            print(f"🟢 RESULTADO FINAL: {resultado['nivel']}")
        elif resultado["score"] >= 40:
            print(f"🟡 RESULTADO FINAL: {resultado['nivel']}")
        else:
            print(f"🔴 RESULTADO FINAL: {resultado['nivel']}")

        print(f"SCORE: {resultado['score']}/100")
        print("\nAVISOS:")
        if resultado['avisos']:
            for aviso in resultado['avisos']:
                print(f"⚠️ {aviso}")
        else:
            print("✅ Nenhum aviso. Parece seguro.")
        print("=" * 50 + "\n")
        time.sleep(1)