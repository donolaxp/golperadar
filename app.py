import requests
import socket
from datetime import datetime

from flask import Flask, render_template, request, jsonify
import validators
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Limite: 10 análises por minuto por IP
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per hour"]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisar', methods=['POST'])
@limiter.limit("10 per minute")
def analisar():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'score': 0, 'status': 'Erro', 'avisos': ['URL não informada']})

    if not validators.url(url):
        return jsonify({'score': 0, 'status': 'Erro', 'avisos': ['URL inválida']})

    score = 80
    avisos = []

    # 1. Checagens básicas
    if url.startswith('http://'):
        score -= 20
        avisos.append('Site sem HTTPS - Conexão insegura')

    if any(x in url for x in ['bit.ly', 'tinyurl']):
        score -= 25
        avisos.append('Link encurtado suspeito')

    suspeitas = ['promocao', 'promo', 'gratis', 'ganhe', 'ganhou', 'premio', 'casino', 'cassino', 'bet', 'aposta', 'pix']
    for palavra in suspeitas:
        if palavra in url.lower():
            score -= 15
            avisos.append(f'Palavra suspeita: {palavra}')
            break

    tlds_suspeitos = ['.xyz', '.tk', '.ml', '.ga', '.cf']
    for tld in tlds_suspeitos:
        if tld in url.lower():
            score -= 20
            avisos.append(f'Domínio suspeito: {tld}')
            break

    # 2. V3.0: WHOIS + GEOIP
    try:
        dominio = url.split('/')[2]

        # WHOIS - Idade do domínio
        whois = requests.get(f'https://api.whoisjson.com/v1/whois?domain={dominio}', timeout=3).json()
        data_criacao = whois.get('created_date', '')
        if data_criacao:
            criado_em = datetime.strptime(data_criacao[:10], '%Y-%m-%d')
            dias = (datetime.now() - criado_em).days
            if dias < 30:
                score -= 30
                avisos.append(f'Domínio criado há {dias} dias - Muito recente')

        # GEOIP - País do servidor
        ip = socket.gethostbyname(dominio)
        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=3).json()
        pais = geo.get('country', '')
        if pais and pais!= 'Brazil':
            score -= 20
            avisos.append(f'Servidor fora do Brasil: {pais}')

    except:
        avisos.append('Não foi possível verificar idade/país do domínio')

    # Resultado final - ISSO TEM QUE SER A ÚLTIMA COISA
    if score < 40:
        status = 'Perigoso'
    elif score < 70:
        status = 'Atenção'
    else:
        status = 'Seguro'

    score = max(0, score)
    return jsonify({'status': status, 'score': score, 'avisos': avisos})