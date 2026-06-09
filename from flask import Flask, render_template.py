from flask import Flask, render_template, request
from scanner import analisar_url, gerar_relatorio_pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisar', methods=['POST'])
def analisar():
    url = request.form['url']
    
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    
    resultado = analisar_url(url)
    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)