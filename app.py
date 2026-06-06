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
        return jsonify({'score': 0, 'status': 'Erro', 'avisos': ['URL não informada']}), 400
        
    if not validators.url(url):
        return jsonify({'score': 0, 'status': 'Erro', 'avisos': ['URL inválida']}), 400
    
    score = 80
    avisos = []
    if 'promocao' in url.lower() or 'promo' in url.lower():
        score -= 30
        avisos.append('Palavra suspeita: promoção')
    if 'bit.ly' in url.lower() or 'tinyurl' in url.lower():
        score -= 25
        avisos.append('Link encurtado suspeito')
    if not url.startswith('https://'):
        score -= 20
        avisos.append('Site sem HTTPS')
        
    status = 'Seguro' if score >= 70 else 'Atenção' if score >= 40 else 'Perigoso'
    
    return jsonify({
        'score': max(score, 0), 
        'status': status, 
        'avisos': avisos if avisos else ['Nenhum problema detectado']
    })

if __name__ == '__main__':
    app.run(debug=False)