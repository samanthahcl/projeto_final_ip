import csv
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash # Adicionado jsonify
# import os # Não estritamente necessrio se for hardcodar a chave, mas útil para a estrutura try/except
import google.generativeai as genai # Biblioteca do Gemini

app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_muito_segura_aqui'

GLOSSARIO_FILE = 'bd_glossario.db'


GEMINI_API_KEY_HARDCODED = "AIzaSyC4va-n3rrvAK5leTswcGHDYlt9gTgYT3g"  # Sua chave aqui
model = None
try:
    if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "SUA_CHAVE_API_AQUI":
        print("ALERTA: A chave da API do Gemini não foi definida ou ainda está com o valor placeholder.")

    else:
        genai.configure(api_key=GEMINI_API_KEY_HARDCODED)
        print("INFO: API Key do Gemini (hardcoded) configurada.")


        available_models_for_generation = [m.name for m in genai.list_models() if
                                           'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash-latest' in available_models_for_generation:
            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            print(f"INFO: Modelo {model.model_name} configurado com sucesso.")
        elif available_models_for_generation:
            model = genai.GenerativeModel(available_models_for_generation[0])
            print(f"INFO: Modelo {model.model_name} (fallback) configurado com sucesso.")
        else:
            print("ERRO: Nenhum modelo Gemini adequado encontrado.")
            model = None
except Exception as e:
    print(f"ERRO CRCO: Falha ao configurar a API do Gemini ou listar modelos: {e}")
    model = None




def ler_glossario_csv():
    """Lê todos os termos do arquivo CSV."""
    termos = []
    try:
        with open(GLOSSARIO_FILE, 'r', newline='', encoding='utf-8') as arquivo:
            reader = csv.reader(arquivo, delimiter=';')
            for linha in reader:
                if linha and len(linha) >= 2:  # Garante que a linha tem termo e definição
                    termos.append([linha[0], linha[1]])
    except FileNotFoundError:
        print(f"AVISO: Arquivo {GLOSSARIO_FILE} não encontrado. Será criado um novo se necessário.")
    except Exception as e:
        print(f"ERRO ao ler o arquivo {GLOSSARIO_FILE}: {e}")
    return termos


def escrever_glossario_csv(termos):
    """Escreve a lista de termos de volta para o arquivo CSV."""
    try:
        with open(GLOSSARIO_FILE, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo, delimiter=';')
            writer.writerows(termos)
        return True
    except Exception as e:
        print(f"ERRO ao escrever no arquivo {GLOSSARIO_FILE}: {e}")
        return False



@app.route('/')
def ola():
    return render_template('index.html')


@app.route('/sobre_equipe')
def sobre_equipe():
    return render_template('sobre_equipe.html')




@app.route('/glossario')
def glossario_page():  # Rota atualizada que você pediu
    glossario_de_termos = ler_glossario_csv()
    return render_template('glossario.html', glossario=glossario_de_termos)


@app.route('/glossario/adicionar', methods=['POST'])
def adicionar_termo_glossario():
    if request.method == 'POST':
        novo_termo_texto = request.form.get('termo')
        nova_definicao_texto = request.form.get('definicao')

        if novo_termo_texto and nova_definicao_texto:
            termos_atuais = ler_glossario_csv()
            termo_existe = any(item[0].lower() == novo_termo_texto.lower() for item in termos_atuais)

            if not termo_existe:
                termos_atuais.append([novo_termo_texto, nova_definicao_texto])
                if escrever_glossario_csv(termos_atuais):
                    flash(f"Termo '{novo_termo_texto}' adicionado com sucesso!", "success")
                else:
                    flash("Erro ao salvar o novo termo no arquivo.", "danger")
            else:
                flash(f"O termo '{novo_termo_texto}' já existe no glossário.", "warning")
        else:
            flash("Termo e definição sbrigatórios.", "danger")
    return redirect(url_for('glossario_page'))


@app.route('/glossario/atualizar', methods=['POST'])
def atualizar_termo_glossario():
    if request.method == 'POST':
        identificador_original = request.form.get('identificador_original_termo')
        termo_atualizado_texto = request.form.get('termo')
        definicao_atualizada_texto = request.form.get('definicao')

        if not identificador_original or not termo_atualizado_texto or not definicao_atualizada_texto:
            flash("Todos os campos são obrigatórios para atualização.", "danger")
            return redirect(url_for('glossario_page'))

        termos_atuais = ler_glossario_csv()
        termo_encontrado_para_atualizar = False


        novo_termo_conflita = False
        if termo_atualizado_texto.lower() != identificador_original.lower():  # Se o nome do termo foi alterado
            for item_idx, item_val in enumerate(termos_atuais):
                if item_val[0].lower() == termo_atualizado_texto.lower():
                    novo_termo_conflita = True
                    break

        if novo_termo_conflita:
            flash(f"O termo '{termo_atualizado_texto}' já existe. Escolha outro nome.", "warning")
            return redirect(url_for('glossario_page'))


        for i, item in enumerate(termos_atuais):
            if item[0] == identificador_original:  # Encontra pelo termo original
                termos_atuais[i][0] = termo_atualizado_texto
                termos_atuais[i][1] = definicao_atualizada_texto
                termo_encontrado_para_atualizar = True
                break

        if termo_encontrado_para_atualizar:
            if escrever_glossario_csv(termos_atuais):
                flash(f"Termo '{identificador_original}' atualizado para '{termo_atualizado_texto}'.", "success")
            else:
                flash("Erro ao salvar as alterações no arquivo.", "danger")
        else:
            flash(f"Termo original '{identificador_original}' não encontrado para atualização.", "danger")

    return redirect(url_for('glossario_page'))


@app.route('/glossario/apagar', methods=['POST'])
def apagar_termo_glossario():
    if request.method == 'POST':
        identificador_termo_apagar = request.form.get('identificador_termo_apagar')

        if identificador_termo_apagar:
            termos_atuais = ler_glossario_csv()
            # Cria uma nova lista sem o termo a ser apagado (comparaase-sensitive aqui, mas poderia ser case-insensitive)
            termos_atualizados = [item for item in termos_atuais if item[0] != identificador_termo_apagar]

            if len(termos_atualizados) < len(termos_atuais):  # Verifica se algum termo foi efetivamente removido
                if escrever_glossario_csv(termos_atualizados):
                    flash(f"Termo '{identificador_termo_apagar}' apagado com sucesso!", "success")
                else:
                    flash("Erro ao salvar as alterações no arquivo ap apagar.", "danger")
            else:
                flash(f"Termo '{identificador_termo_apagar}' não encontrado para apagar.", "warning")
        else:
            flash("Nenhum termo especificado para apagar.", "danger")

    return redirect(url_for('glossario_page'))



@app.route('/prompt_gemini')
def prompt_gemini_page():
    return render_template('prompt_gemini.html')


@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')


@app.route('/gerar_resposta_gemini', methods=['POST'])
def gerar_resposta_gemini_api():
    if not model:
        print("ERRO: Modelo Gemini não inicializado.")
        return jsonify({"error": "Serviço Gemini não está disponível."}), 503

    try:
        dados_requisicao = request.get_json()
        if not dados_requisicao or 'prompt' not in dados_requisicao:
            return jsonify({"error": "Nenhum prompt fornecido."}), 400

        prompt_usuario = dados_requisicao['prompt']
        if not prompt_usuario.strip():
            return jsonify({"error": "O prompt não pode estar vazio."}), 400

        print(f"INFO: Recebido prompt para Gemini: '{prompt_usuario}'")
        response = model.generate_content(prompt_usuario)
        texto_gerado = response.text
        print(f"INFO: Resposta do Gemini: '{texto_gerado[:100]}...'")
        return jsonify({"generated_text": texto_gerado})

    except Exception as e:
        print(f"ERRO ao chamar a API do Gemini ou processar a rota: {e}")
        return jsonify({"error": f"Ocorreu um erro: {str(e)}"}), 500




if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import csv
import google.generativeai as genai

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Termo


GEMINI_API_KEY_HARDCODED = "SUA_CHAVE_API_AQUI"
model = None
try:
    if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "SUA_CHAVE_API_AQUI":
        print("ALERTA: A chave da API do Gemini não foi definida ou está placeholder.")
    else:
        genai.configure(api_key=GEMINI_API_KEY_HARDCODED)
        print("API Key configurada.")
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            model = genai.GenerativeModel(available_models[0])
except Exception as e:
    print(f"Erro na configuração do Gemini: {e}")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/glossario')
def glossario():
    glossario_de_termos = Termo.query.all()
    return render_template('glossario.html', glossario=glossario_de_termos)

@app.route('/novo_termo')
def novo_termo():
    return render_template('novo_termo.html')

@app.route('/criar_termo', methods=['POST'])
def criar_termo():
    termo = request.form['termo']
    definicao = request.form['definicao']
    novo_termo = Termo(termo=termo, definicao=definicao)
    db.session.add(novo_termo)
    db.session.commit()
    return redirect(url_for('glossario'))

@app.route('/gerar_resposta_gemini', methods=['POST'])
def gerar_resposta_gemini_api():
    if not model:
        return jsonify({"error": "Serviço Gemini não disponível."}), 503
    dados_requisicao = request.get_json()
    prompt_usuario = dados_requisicao.get('prompt', '').strip()
    if not prompt_usuario:
        return jsonify({"error": "Prompt vazio."}), 400
    response = model.generate_content(prompt_usuario)
    return jsonify({"generated_text": response.text})

if __name__ == '__main__':
    app.run(debug=True)






