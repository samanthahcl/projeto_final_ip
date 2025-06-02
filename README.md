PyCaderno: Seu Caderno Interativo de Python com Quiz e Assistente Gemini

Bem-vindo ao PyCaderno! Este é um projeto de aplicação web educacional desenvolvido com Python (Flask), HTML, CSS e JavaScript. Ele foi feito para ajudar estudantes de Python a revisar conceitos fundamentais e testar seus conhecimentos de forma interativa. Além disso, o PyCaderno conta com um assistente integrado à API do Google Gemini para responder às suas dúvidas de programação em tempo real!

 Funcionalidades
O PyCaderno oferece um conjunto de ferramentas para otimizar seu aprendizado em Python:

Caderno de Estudos: Resumos claros e concisos sobre os tópicos essenciais de Python:
Estruturas de seleção (if, elif, else)
Estruturas de repetição (for, while)
Vetores e Matrizes (listas e listas aninhadas)
Funções e Procedimentos
Tratamento de exceções (try, except, else, finally)
Quiz Interativo: Teste seus conhecimentos com um quiz dinâmico sobre os tópicos abordados.
Glossário de Termos: Adicione e consulte termos e definições de programação para enriquecer seu vocabulário técnico.
Assistente Gemini: Tire suas dúvidas de programação instantaneamente. Basta digitar sua pergunta e o Gemini fornecerá explicações e exemplos.
Design Responsivo: Acesse o PyCaderno de qualquer dispositivo (desktop, tablet ou celular) com uma experiência de usuário otimizada.
 Tecnologias Utilizadas
O PyCaderno foi construído usando uma combinação de tecnologias de backend e frontend:

Backend (Python):

Python: A linguagem de programação principal, que orquestra a lógica do servidor, a manipulação de dados e a integração com APIs.
Flask: Um microframework web leve que lida com o roteamento das URLs, a gestão das requisições e respostas HTTP, e a renderização dos templates HTML.
google-generativeai: A biblioteca oficial do Google para interagir com a API do Gemini, permitindo a comunicação com o modelo de IA.
csv: Módulo embutido do Python usado para ler e escrever dados no arquivo bd_glossario.csv, que armazena os termos do glossário.
Frontend (HTML, CSS, JavaScript):

HTML5: Usado para estruturar o conteúdo de todas as páginas do site, desde os resumos do caderno até a interface do quiz e do assistente Gemini.
CSS3: Responsável pela estilização visual do PyCaderno. Inclui um tema personalizado em tons de verde, garantindo uma identidade visual coesa e agradável.
JavaScript: Adiciona interatividade às páginas, gerenciando a lógica do quiz (como carregar perguntas, verificar respostas e calcular pontuações) e a comunicação assíncrona com o backend para o assistente Gemini.
Bootstrap 5.3.2: Um framework CSS amplamente utilizado que fornece componentes pré-estilizados e um sistema de grid responsivo, agilizando o desenvolvimento do layout e garantindo que o site se adapte bem a diferentes tamanhos de tela.
 Estrutura do Site e Conteúdo de Cada Seção
A estrutura do projeto é organizada para facilitar a manutenção e o desenvolvimento. 


A integração com a API do Google Gemini é um ponto central do PyCaderno, permitindo que os estudantes obtenham ajuda em tempo real. Veja como ela funciona:

Configuração no Backend (app.py):

A biblioteca google.generativeai é importada e configurada com uma chave de API (GEMINI_API_KEY_HARDCODED). É crucial que você substitua o placeholder pela sua chave de API real.
O código tenta inicializar um modelo Gemini (preferencialmente 'models/gemini-1.5-flash-latest') e verifica se ele está disponível. Mensagens de log são exibidas no console para indicar o status da configuração.
Endpoint do Gemini (/gerar_resposta_gemini):

No arquivo app.py, existe uma rota (@app.route('/gerar_resposta_gemini', methods=['POST'])) que funciona como um endpoint da API.
Quando o frontend precisa de uma resposta do Gemini, ele envia uma requisição POST para esta rota, contendo o prompt (a pergunta do usuário) em formato JSON.
Chamada à API Gemini:

Dentro da função gerar_resposta_gemini_api(), o Flask recebe o prompt do usuário.
Ele então faz a chamada response = model.generate_content(prompt_usuario), enviando o prompt para o modelo Gemini configurado.
A resposta gerada pelo Gemini é extraída (response.text).
Resposta ao Frontend:

O texto gerado pelo Gemini é então encapsulado em um JSON (jsonify({"generated_text": texto_gerado})) e enviado de volta ao frontend.
O backend inclui tratamento de erros robusto para casos de falha na comunicação com a API do Gemini, prompts vazios ou outros problemas inesperados, garantindo que o usuário receba um feedback adequado.
Interação no Frontend (prompt_gemini.html e JavaScript associado):

A página prompt_gemini.html fornece uma interface (um textarea para o prompt e um botão de envio).
O JavaScript nesta página captura o input do usuário, envia a requisição assíncrona (fetch ou XMLHttpRequest) para o endpoint /gerar_resposta_gemini no backend.
Após receber a resposta, o JavaScript atualiza dinamicamente a interface do usuário para exibir o texto gerado pelo Gemini.
 Como Executar a Aplicação Flask Localmente
Para colocar o PyCaderno para rodar em sua máquina, siga estes passos:

Clone o Repositório: Se ainda não o fez, comece clonando o projeto do GitHub para o seu computador.

Bash

git clone https://github.com/samanthahcl/projeto_final_ip.
cd pycaderno
Crie e Ative um Ambiente Virtual (Recomendado):
Isso isola as dependências do seu projeto, evitando conflitos com outras instalações Python.

Bash

python -m venv venv
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
Instale as Dependências:
Com o ambiente virtual ativado, instale as bibliotecas Flask e google-generativeai.

Bash

pip install Flask google-generativeai
Obtenha sua Chave da API do Google Gemini:

Visite Google AI Studio.
Crie uma nova chave de API e copie-a.
Configure a Chave da API:
Abra o arquivo app.py e localize a linha GEMINI_API_KEY_HARDCODED = "AIzaSyD0fv4Dcc_MyK9-S0Uecop3A765A0FA27Q".
Substitua o valor atual pela sua chave de API real.

Python

# Exemplo:
GEMINI_API_KEY_HARDCODED = "SUA_CHAVE_DE_API_DO_GEMINI_AQUI"
Lembre-se: Nunca exponha sua chave de API em repositórios públicos!

Execute o Aplicativo Flask:
A partir da pasta raiz do projeto (onde app.py está), execute o seguinte comando:

Bash

python app.py
Você verá mensagens no seu terminal indicando que o servidor Flask está rodando, geralmente em http://127.0.0.1:5000/.

Acesse no Navegador:
Abra seu navegador web e navegue até a URL fornecida pelo Flask (normalmente http://127.0.0.1:5000/).

 Principais Partes do Código Python (app.py)
O arquivo app.py é o coração do backend. Aqui estão suas seções mais importantes:

Importações:

Python

import csv
from flask import Flask, render_template, url_for, request, redirect, jsonify
import google.generativeai as genai
Importa os módulos necessários: csv para manipulação de arquivos, Flask e suas funções para a construção da aplicação web, e google.generativeai para a integração com o Gemini.

Configuração da API do Gemini:

Python

GEMINI_API_KEY_HARDCODED = "SUA_CHAVE_API_AQUI" # Sua chave aqui
# ... lógica para configurar e inicializar o modelo Gemini ...
model = genai.GenerativeModel(model_name_to_use) # Exemplo de inicialização
Esta seção configura sua chave de API e tenta inicializar o modelo de linguagem do Gemini. Há validações para garantir que a chave foi inserida e que um modelo funcional seja carregado.

Rotas (Endpoints):
As rotas conectam URLs a funções Python que processam as requisições. Exemplos:

@app.route('/'): Rota para a página inicial, que renderiza index.html.
@app.route('/glossario'): Lê bd_glossario.csv e passa os dados para glossario.html.
@app.route('/criar_termo', methods=['POST']): Processa dados de formulário para adicionar um novo termo ao bd_glossario.csv.
@app.route('/gerar_resposta_gemini', methods=['POST']): A rota chave para a integração Gemini. Ela recebe um prompt do frontend, chama a API do Gemini (model.generate_content(prompt)), e retorna a resposta. Inclui validações e tratamento de exceções para a comunicação com a API.
Lógica do Glossário:
As funções glossario() e criar_termo() gerenciam a leitura e escrita no arquivo bd_glossario.csv, permitindo a funcionalidade de adicionar e listar termos do glossário.

Execução da Aplicação:

Python

if _name_ == '_main_':
    app.run(debug=True)
Este bloco garante que o servidor Flask seja iniciado apenas quando o script app.py é executado diretamente. debug=True é útil para desenvolvimento, pois recarrega o servidor automaticamente e exibe mensagens de erro detalhadas. Para produção, debug deve ser False.