import csv
from flask import Flask, render_template, url_for, request, redirect, jsonify # Adicionado jsonify
# import os # Não estritamente necessrio se for hardcodar a chave, mas útil para a estrutura try/except
import google.generativeai as genai # Biblioteca do Gemini

app = Flask(__name__)

# --- Configuração da API do Gemini ---
# ATENÇÃO: SUBSTITUA "SUA_CHAVE_API_AQUI" PELA SUA CHAVE REAL.
# LEMBRE-SE DE REMOVER ANTES DE ENVIAR PARA O GITHUB OU COMPARTILHAR O CÓDIGO.
GEMINI_API_KEY_HARDCODED = "AIzaSyD0fv4Dcc_MyK9-S0Uecop3A765A0FA27Q"  # Sua chave aqui

model = None
try:
    if not GEMINI_API_KEY_HARDCODED or GEMINI_API_KEY_HARDCODED == "SUA_CHAVE_API_AQUI":
        print("ALERTA: A chave da API do Gemini não foi definida ou ainda está com o valor placeholder.")
        print("Por favor, substitua 'SUA_CHAVE_API_AQUI' pela sua chave real no arquivo app.py.")
    else:
        genai.configure(api_key=GEMINI_API_KEY_HARDCODED)
        print("INFO: API Key do Gemini (hardcoded) configurada.")

        # --- INÍCIO DO TRECHO PARA LISTAR MODELOS ---
        print("=" * 50)
        print("Modelos disponíveis que suportam 'generateContent':")
        models_found = False
        available_models_for_generation = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- Nome: {m.name} (Display Name: {m.display_name})")
                available_models_for_generation.append(m.name)
                models_found = True

        if not models_found:
            print(
                "NENHUM modelo encontrado que suporte 'generateContent'. Verifique sua API Key, permissões ou região.")
        else:
            print(f"Sugestões de modelos para usar: {available_models_for_generation}")
        print("=" * 50)
        # --- FIM DO TRECHO PARA LISTAR MODELOS ---

        # Escolha o modelo que deseja usar.
        # ATUALIZE A LINHA ABAIXO com um nome da lista impressa no console!
        # Exemplo: model_name_to_use = 'models/gemini-1.5-flash-latest'
        # Exemplo: model_name_to_use = 'models/gemini-1.0-pro-latest'
        # Exemplo: model_name_to_use = 'models/gemini-pro' # Se ele aparecer na lista

        # Tente um destes se aparecerem na sua lista, ou o que for mais apropriado:
        model_name_to_use = 'models/gemini-1.5-flash-latest'  # Boa opntenha o seu original se ele aparecer na lista

        if model_name_to_use in available_models_for_generation:
            print(f"INFO: Tentando inicializar o modelo: {model_name_to_use}")
            model = genai.GenerativeModel(model_name_to_use)
            print(f"INFO: Modelo {model.model_name} configurado com sucesso.")
        elif available_models_for_generation:
            suggested_model = available_models_for_generation[0]
            print(
                f"AVISO: O modelo '{model_name_to_use}' não foi encontrado na lista de modelos disponíveis que suportam 'generateContent'.")
            print(f"INFO: Tentando usar o primeiro modelo disponível da lista: {suggested_model}")
            model = genai.GenerativeModel(suggested_model)
            print(f"INFO: Modelo {model.model_name} configurado com sucesso.")
        else:
            print(
                f"ERRO: Nenhum modelo adequado encontrado ou o modelo '{model_name_to_use}' não está disponível. O modelo não será inicializado.")
            model = None

except Exception as e:
    print(f"ERRO CRTICO: Falha ao configurar a API do Gemini ou listar modelos: {e}")
    model = None  # Garante que o modelo é None se a configuração falhar


# --- Fim da Configuração da API do Gemini ---


@app.route('/')
def ola():
    return render_template('index.html')

@app.route('/sobre_equipe')
def sobre_equipe():
    return render_template('sobre_equipe.html')

@app.route('/glossario')
def glossario():
    glossario_de_termos = []
    try:
        with open('bd_glossario.db', 'r', newline='', encoding='utf-8') as arquivo:
            reader = csv.reader(arquivo, delimiter=';')
            for linha in reader:
                glossario_de_termos.append(linha)
    except FileNotFoundError:
        print("AVISO: Arquivo bd_glossario.db não encontrado. O glossário estará vazio.")
    except Exception as e:
        print(f"ERRO ao ler o arquivo bd_glossario.db: {e}")
    return render_template('glossario.html', glossario=glossario_de_termos)

@app.route('/novo_termo')
def novo_termo():
    return render_template('novo_termo.html')

@app.route('/criar_termo', methods=['POST'])
def criar_termo():
    try:
        termo = request.form['termo']
        definicao = request.form['definicao']

        with open('bd_glossario.db', 'a', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo, delimiter=';')
            writer.writerow([termo, definicao])
        return redirect(url_for('glossario'))
    except KeyError:
        print("ERRO: 'termo' ou 'definicao' ausentes no formulário.")
        # Idealmente, retornar uma página de erro ou uma mensagem para o usuário
        return "Erro: Dados do formulário incompletos.", 400
    except Exception as e:
        print(f"ERRO ao criar termo: {e}")
        return "Erro interno ao salvar o termo.", 500

@app.route('/prompt_gemini')
def prompt_gemini_page(): # Renomeado para não conflitar com a rota da API
    return render_template('prompt_gemini.html')

# ... (outras importações e rotas)

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

# ... (resto do seu app.py, como if __name__ == '__main__':)

# NOVA ROTA PARA LIDAR COM A REQUISIÇÃO DO GEMINI
@app.route('/gerar_resposta_gemini', methods=['POST'])
def gerar_resposta_gemini_api():
    if not model: # Verifica se o modelo foi inicializado corretamente
        print("ERRO: Modelo Gemini não inicializado. Verifique a configuração da API Key.")
        return jsonify({"error": "Serviço Gemini não está disponível no momento devido a um problema de configuração."}), 503 # Service Unavailable

    try:
        dados_requisicao = request.get_json()
        if not dados_requisicao or 'prompt' not in dados_requisicao:
            return jsonify({"error": "Nenhum prompt fornecido na requisição."}), 400

        prompt_usuario = dados_requisicao['prompt']
        if not prompt_usuario.strip(): # Verifica se o prompt não está vazio ou só com espaços
            return jsonify({"error": "O prompt não pode estar vazio."}), 400

        print(f"INFO: Recebido prompt para Gemini: '{prompt_usuario}'")

        # --- CHAMADA REAL À API DO GEMINI ---
        try:
            # Para chat contínuo, você usaria model.start_chat() e chat.send_message()
            # Para uma única pergunta/resposta, generate_content é mais direto.
            response = model.generate_content(prompt_usuario)
            texto_gerado = response.text # Acessa o texto da resposta
            print(f"INFO: Resposta do Gemini: '{texto_gerado[:100]}...'") # Loga parte da resposta
            return jsonify({"generated_text": texto_gerado})

        except Exception as e:
            # Captura erros específicos da API do Gemini ou erros de rede
            print(f"ERRO ao chamar a API do Gemini: {e}")
            # Você pode querer inspecionar 'e' para dar mensagens de erro mais específicas
            return jsonify({"error": f"Ocorreu um erro ao comunicar com o serviço Gemini: {str(e)}"}), 502 # Bad Gateway (ou 500)

    except Exception as e:
        # Captura outros erros inesperados no processamento da rota
        print(f"ERRO inesperado na rota /gerar_resposta_gemini: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor ao processar sua solicitação."}), 500

if __name__ == '__main__':
    # Certifique-se de que o debug=True seja usado apenas em desenvolvimento

    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import csv
import google.generativeai as genai

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Termo

# --- Configuração do Gemini ---
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






