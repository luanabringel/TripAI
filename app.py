from flask import Flask, render_template, request, redirect, url_for
from api_backend.recomendacoes import *

app = Flask(__name__)
agente_processor = AgenteProcessorTexto()
agente_yelp = AgenteYelp(yelp_api_key='EVcoTuv6Im8ApisNLkhYcG68F0U1-9PhtC9FYuXQEhGcs9wxs5dAUDptJVcCQKci8lKmT96IavnLb-n_KCh8GXP3EiBC1pFLeLoJW2fBceq_Ln0CzbHBVcaLU-X4ZnYx',
                             opencage_api_key='755a7d3d5d8743728e809342a7291d5a')
agente_foursquare = AgenteFoursquare(foursquare_api_key='fsq3MZABriF086Ggov3imwdz1lULdW/uvYXFiwr/Rz9pmOo=')
agente_cidade_brasil = AgenteCidadeBrasil()
agente_atlas_obscura = AgenteAtlasObscura()
genai.configure(api_key='AIzaSyAyLDHhupk6bAIaXuSnRIDusM7zA7bmO9M')

coordenador = AgenteCoordenador({
    'Yelp': agente_yelp,
    'Foursquare': agente_foursquare,
    'Cidade Brasil': agente_cidade_brasil,
    'Atlas Obscura': agente_atlas_obscura
})

messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form.get('user_input')
    if user_input:
        messages.append({"sender": "user", "text": user_input})
        local, recomendacoes = agente_processor.processar_texto(user_input)
        informacoes = coordenador.coletar_informacoes(local, recomendacoes)
        resposta_gemini = coordenador.gerar_resposta_com_gemini(local, informacoes)
        messages.append({"sender": "bot", "text": resposta_gemini})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    