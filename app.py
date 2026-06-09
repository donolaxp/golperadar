from flask import Flask, render_template, request
from scanner import analisar_url

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    resultado = None
    if request.method == "POST":
        url = request.form["url"]
        resultado = analisar_url(url)
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)