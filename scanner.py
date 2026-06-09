import requests
import socket
import whois
from urllib.parse import urlparse, quote
from datetime import datetime

# Lista de palavras que golpista AMA usar
PALAVRAS_SUSPEITAS = [
    'banco', 'brasil', 'seguro', 'gratis', 'promocao', 'urgente', 
    'premio', 'ganhador', 'iphone', 'pix', 'bradesco', 'itau', 
    'caixa', 'santander', 'nubank', 'receita', 'gov', 'serasa'
]

# Domínios oficiais de bancos BR pra comparar
DOMINIOS_OFICIAIS = {
    'bb.com.br': 'Banco do Brasil',
    'bradesco.com.br': 'Bradesco',
    'itau.com.br': 'Itaú',
    'santander.com.br': 'Santander',
    'caixa.gov.br': 'Caixa',
    'nubank.com.br': 'Nubank'
}

def analisar_url(url):
    if not url.startswith('http'):
        url = 'https://' + url
    
    resultado = {
        "url": url,
        "dominio": "Erro",
        "idade_dominio": "Erro",
        "ssl_valido": "Erro",
        "ip_real": "Erro",
        "redirecionamentos": "Erro",
        "risco": "INDEFINIDO",
        "porcentagem": "0%",
        "classe_risco": "risco-alto",
        "link_reclame_aqui": "#",
        "alerta_phishing": ""
    }
    
    pontos_risco = 0
    dominio_existe = True

    try:
        parsed_url = urlparse(url)
        dominio = parsed_url.netloc
        if dominio.startswith('www.'):
            dominio = dominio[4:]
        resultado["dominio"] = dominio
        resultado["link_reclame_aqui"] = f"https://www.reclameaqui.com.br/busca/?q={quote(dominio)}"

        # 1. IP Real - SE NÃO ACHAR, JÁ É ALTO RISCO
        try:
            ip = socket.gethostbyname(dominio)
            resultado["ip_real"] = ip
        except socket.gaierror:
            resultado["ip_real"] = "Não encontrado - DOMÍNIO NÃO EXISTE"
            pontos_risco = 100 # MATA DIRETO
            dominio_existe = False
        
        # Se domínio nem existe, nem testa o resto
        if dominio_existe:
            # 2. Check Anti-Phishing v2.4
            dominio_lower = dominio.lower()
            
            # Regra 1: Palavras suspeitas no domínio
            palavras_encontradas = [p for p in PALAVRAS_SUSPEITAS if p in dominio_lower]
            if palavras_encontradas:
                pontos_risco += 40
                resultado["alerta_phishing"] = f"Alerta: Palavras suspeitas detectadas: {', '.join(palavras_encontradas)}"
            
            # Regra 2: Se parece banco mas não é o oficial
            for oficial in DOMINIOS_OFICIAIS:
                if oficial.split('.')[0] in dominio_lower and dominio!= oficial:
                    pontos_risco += 50
                    resultado["alerta_phishing"] += f" | Possível phishing de {DOMINIOS_OFICIAIS[oficial]}. Site oficial: {oficial}"

            # 3. Idade do Domínio via Whois
            try:
                w = whois.whois(dominio)
                if w.creation_date:
                    if isinstance(w.creation_date, list):
                        creation_date = w.creation_date[0]
                    else:
                        creation_date = w.creation_date
                    
                    idade_dias = (datetime.now() - creation_date).days
                    resultado["idade_dominio"] = f"{idade_dias} dias"
                    
                    if idade_dias < 30:
                        pontos_risco += 30
                    elif idade_dias < 180:
                        pontos_risco += 15
                else:
                    resultado["idade_dominio"] = "Desconhecida / Protegida"
                    pontos_risco += 10 # Whois bloqueado é suspeito
            except Exception:
                resultado["idade_dominio"] = "Desconhecida / Bloqueado"
                pontos_risco += 10

            # 4. Verificar SSL
            try:
                r = requests.get(url, timeout=5, verify=True)
                if r.url.startswith('https'):
                    resultado["ssl_valido"] = "Sim"
                else:
                    resultado["ssl_valido"] = "Não"
                    pontos_risco += 40
            except requests.exceptions.SSLError:
                resultado["ssl_valido"] = "Não - Certificado Inválido"
                pontos_risco += 40
            except Exception:
                resultado["ssl_valido"] = "Não - Erro de Conexão"
                pontos_risco += 40

            # 5. Redirecionamentos
            try:
                r = requests.get(url, timeout=5, allow_redirects=True)
                if len(r.history) > 1:
                    resultado["redirecionamentos"] = f"Sim - {len(r.history)} saltos"
                    pontos_risco += 20
                else:
                    resultado["redirecionamentos"] = "Não"
            except Exception:
                resultado["redirecionamentos"] = "Erro ao testar"

        # 6. Cálculo Final de Risco - v2.4
        if pontos_risco >= 100:
            resultado["risco"] = "ALTO"
            resultado["porcentagem"] = "100%"
            resultado["classe_risco"] = "risco-alto"
        elif pontos_risco == 0:
            resultado["risco"] = "SEGURO"
            resultado["porcentagem"] = "0%"
            resultado["classe_risco"] = "risco-seguro"
        elif pontos_risco < 30:
            resultado["risco"] = "BAIXO"
            resultado["porcentagem"] = f"{pontos_risco}%"
            resultado["classe_risco"] = "risco-baixo"
        elif pontos_risco < 70:
            resultado["risco"] = "MÉDIO"
            resultado["porcentagem"] = f"{pontos_risco}%"
            resultado["classe_risco"] = "risco-medio"
        else:
            resultado["risco"] = "ALTO"
            resultado["porcentagem"] = f"{pontos_risco}%"
            resultado["classe_risco"] = "risco-alto"

    except Exception as e:
        resultado["url"] = f"Erro ao analisar: {str(e)}"
        resultado["risco"] = "ALTO"
        resultado["porcentagem"] = "100%"

    return resultado