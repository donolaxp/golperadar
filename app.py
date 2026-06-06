from flask import Flask, render_template, request, jsonify  ✅ CORRETA
import requests
import whois
from datetime import datetime
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # ✅ ESSAS 3 LINHAS NOVAS

@app.route('/verificar', methods=['POST'])
def verificar():
    data = request.get_json()
    url = data.get('url', '')
    resultado = analisar_url(url)  # Usa sua função que já existe
    return jsonify(resultado)

def analisar_url(url):
    resultado = {
        "url": url,
        "score": 100,
        "nivel": "Seguro",
        "avisos": [],
        "cor": "green"
    }

    try:
        dominio = re.findall(r'https?://([^/]+)', url)[0]
        w = whois.whois(dominio)
        data_criacao = w.creation_date
        if isinstance(data_criacao, list):
            data_criacao = data_criacao[0]
        dias = (datetime.now() - data_criacao).days
        if dias < 30:
            resultado["score"] -= 50
            resultado["avisos"].append(f"DOMÍNIO NOVO: Criado há {dias} dias.")
        elif dias < 90:
            resultado["score"] -= 20
            resultado["avisos"].append(f"Domínio recente: {dias} dias.")
    except:
        resultado["score"] -= 20
        resultado["avisos"].append("Não consegui ver idade do domínio.")

    try:
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        texto = r.text.lower()
        golpes = ["ganhe dinheiro rápido", "lucro garantido", "método secreto", "vagas limitadas", "últimas horas", "clique aqui", "investimento sem risco"]
        for palavra in golpes:
            if palavra in texto:
                resultado["score"] -= 25
                resultado["avisos"].append(f'Termo suspeito: "{palavra}"')
    except:
        resultado["score"] -= 15
        resultado["avisos"].append("Site demorou pra responder ou bloqueou.")

    if not url.startswith("https://"):
        resultado["score"] -= 30
        resultado["avisos"].append("Site sem HTTPS.")

    if resultado["score"] < 40:
        resultado["nivel"] = "PERIGO - Provável Golpe"
        resultado["cor"] = "red"
    elif resultado["score"] < 70:
        resultado["nivel"] = "ATENÇÃO - Suspeito"
        resultado["cor"] = "orange"

    return resultado

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GolpeRadar - DONOLAXP Security</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; text-align: center; padding: 20px; }
      .container { max-width: 600px; margin: 0 auto; background: #1a1a1a; padding: 30px; border-radius: 15px; box-shadow: 0 0 20px #0088ff50; }
        h1 { color: #0088ff; }
        input { width: 80%; padding: 12px; border-radius: 8px; border: 2px solid #0088ff; background: #2a2a2a; color: #fff; font-size: 16px; }
        button { padding: 12px 30px; background: #0088ff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; }
        button:hover { background: #0066cc; }
      .resultado { margin-top: 30px; padding: 20px; border-radius: 10px; }
      .green { background: #0d4d0d; border: 2px solid #00ff00; }
      .orange { background: #4d3d00; border: 2px solid #ffaa00; }
      .red { background: #4d0000; border: 2px solid #ff0000; }
      .score { font-size: 48px; font-weight: bold; margin: 10px 0; }
      .aviso { text-align: left; margin: 10px 0; padding: 10px; background: #00000050; border-radius: 5px; }
      .footer { margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ GOLPERADAR</h1>
        <p>Analisador de sites suspeitos by DONOLAXP Security</p>
        <form method="POST">
            <input type="text" name="url" placeholder="Cole a URL aqui. Ex: site-suspeito.com" required>
            <br>
            <button type="submit">🔍 ESCANEAR AGORA</button>
        </form>

        {% if resultado %}
        <div class="resultado {{ resultado.cor }}">
            <h2>{{ resultado.nivel }}</h2>
            <div class="score">{{ resultado.score }}/100</div>
            <p>URL: {{ resultado.url }}</p>
            <h3>AVISOS:</h3>
            {% if resultado.avisos %}
                {% for aviso in resultado.avisos %}
                <div class="aviso">⚠️ {{ aviso }}</div>
                {% endfor %}
            {% else %}
                <div class="aviso">✅ Nenhum aviso. Parece seguro.</div>
            {% endif %}
        </div>
        {% endif %}

        <div class="footer">DONOLAXP Security v2.0 Web | Rumo à ISH 🚗💙</div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    resultado = None
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        resultado = analisar_url(url)
    return render_template_string(HTML, resultado=resultado)

if __name__ == '__main__':
    print("🔵 GOLPERADAR WEB INICIADO!")
    print("Acesse: http://127.0.0.1:5000")
    app.run(debug=True)
