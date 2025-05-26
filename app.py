from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def ola():
    #return '<h1> Olá, mundo! </h1>'
    return render_template('index.html')
app.run()