from flask import Flask, render_template, request, jsonify
from api_backend.recomendacoes import AgenteCoordenador, AgenteAtlasObscura, AgenteCidadeBrasil, AgenteFoursquare, AgenteProcessorTexto, AgenteYelp, genai
import asyncio
import api_backend.config as config

app = Flask(__name__)

coordenador = AgenteCoordenador("agente_coordenador@localhost", "123456")
agente_atlas_obscura = AgenteAtlasObscura("agente_atlas_obscura@localhost", "123456")
agente_yelp = AgenteYelp("agente_yelp@localhost", "123456")
agente_foursquare = AgenteFoursquare("agente_foursquare@localhost", "123456")
agente_cidade_brasil = AgenteCidadeBrasil("agente_cidade_brasil@localhost", "123456")
agente_processor = AgenteProcessorTexto("agente_processor@localhost", "123456")

messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
async def submit():
    user_input = request.form.get('user_input')

    if user_input:
        messages.append({"sender": "user", "text": user_input})

        agente_processor.texto_param = user_input

        await coordenador.start(auto_register=True)
        await agente_atlas_obscura.start(auto_register=True)
        await agente_yelp.start(auto_register=True)
        await agente_foursquare.start(auto_register=True)
        await agente_cidade_brasil.start(auto_register=True)
        await agente_processor.start(auto_register=True)

        await asyncio.sleep(5)
    
        await agente_processor.stop()
        await agente_yelp.stop()
        await agente_foursquare.stop()
        await agente_cidade_brasil.stop()
        await agente_atlas_obscura.stop()
        await coordenador.stop()

        return jsonify({"text": config.resposta_gerada})

    return jsonify({"text": "Entrada de usuário inválida"}), 400

if __name__ == '__main__':
    app.run(debug=True)