from flask import Flask, render_template, request, jsonify
import validators
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# BLINDAGEM 1: Rate Limiting - ninguém derruba seu site
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour", "20 per minute"],  # Limite global
    storage_uri="memory://",
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisar', methods=['POST'])
@limiter.limit("5 per minute")  # BLINDAGEM 2: Máx 5 análises/min por IP
def analisar():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        # BLINDAGEM 3: Corta input gigante
        if len(url) > 2048:
            return jsonify({
                'score': 0,
                'status': 'Erro',
                'avisos': ['URL muito longa. Máximo 2048 caracteres.']
            }), 400
        
        # BLINDAGEM 4: Remove espaços e força string
        url = str(url).strip()[:2048]
        
        if not url:
            return jsonify({
                'score': 0,
                'status': 'Erro',
                'avisos': ['URL não fornecida']
            }), 400
        
        if not validators.url(url):
            return jsonify({
                'score': 0,
                'status': 'Erro',
                'avisos': ['URL inválida. Use http:// ou https://']
            }), 400
        
        # SUA LÓGICA DE ANÁLISE AQUI - NÃO MUDOU NADA
        score = 80
        avisos = []
        
        if 'promocao' in url.lower() or 'gratis' in url.lower():
            score -= 30
            avisos.append('Palavras suspeitas: promoção, grátis')
        if 'bit.ly' in url or 'tinyurl' in url:
            score -= 15
            avisos.append('Link encurtado detectado')
        if not url.startswith('https://'):
            score -= 20
            avisos.append('Site sem HTTPS - conexão insegura')
            
        status = 'Seguro' if score >= 70 else 'Atenção' if score >= 40 else 'Perigoso'
        
        return jsonify({
            'score': max(score, 0),
            'status': status,
            'avisos': avisos if avisos else ['Nenhum problema detectado']
        })
        
    except Exception as e:
        # BLINDAGEM 5: Não vaza erro interno pro hacker
        return jsonify({
            'score': 0,
            'status': 'Erro',
            'avisos': ['Erro ao processar. Tente novamente.']
        }), 500

if __name__ == '__main__':
    app.run(debug=False)  # BLINDAGEM 6: Debug OFF em produção