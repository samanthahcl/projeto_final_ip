import csv
from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)

@app.route('/')
def ola():
    # return '<h1> Olá, mundo! </h1>'
    return render_template('index.html')

@app.route('/sobre_equipe')
def sobre_equipe():
    return render_template('sobre_equipe.html')

@app.route('/glossario')
def glossario():
    glossario_de_termos = []

    with open('bd_glossario.csv', 'r', newline='', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo, delimiter=';')
        for linha in reader:
            glossario_de_termos.append(linha)

    return render_template('glossario.html', glossario=glossario_de_termos)

@app.route('/novo_termo')
def novo_termo():
    return render_template('novo_termo.html')

@app.route('/criar_termo', methods=['POST'])
def criar_termo():
    termo = request.form['termo']
    definicao = request.form['definicao']

    with open('bd_glossario.csv', 'a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo, delimiter=';')
        writer.writerow([termo, definicao])

    return redirect(url_for('glossario'))

@app.route('/prompt_gemini')
def prompt_gemini():
    return render_template('prompt_gemini.html')

if __name__ == '__main__':
    app.run(debug=True)
