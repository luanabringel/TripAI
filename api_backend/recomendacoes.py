import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import json
import requests
import spacy
from spacy.matcher import Matcher
from bs4 import BeautifulSoup
import google.generativeai as genai
from geopy.geocoders import OpenCage
from markupsafe import Markup
import api_backend.config as config


class AgenteProcessorTexto(Agent):
    class ProcessarTextoBehaviour(OneShotBehaviour):
        def __init__(self, texto):
            super().__init__()
            self.texto = texto

        async def run(self):
            nlp = spacy.load("pt_core_news_sm")
            matcher = Matcher(nlp.vocab)
            matcher.add("RECOMENDACOES", [
                [{"LOWER": {"IN": ["restaurante", "culinária", "comida", "gastronomia", "cozinha"]}}, {"IS_ALPHA": True}],
                [{"LOWER": "comida"}, {"LOWER": {"IN": ["japonesa", "mexicana", "italiana", "brasileira", "francesa"]}}],
                [{"LOWER": "culinária"}, {"LOWER": {"IN": ["local", "regional", "internacional"]}}],
                [{"LOWER": "visitar"}, {"IS_ALPHA": True}],
                [{"LOWER": {"IN": ["museu", "galeria", "exposições", "obras"]}}, {"IS_ALPHA": True}],
                [{"LOWER": "pontos"}, {"LOWER": "turísticos"}],
                [{"LOWER": {"IN": ["vistas", "locais", "lugares", "ambientes"]}}, {"LOWER": {"IN": ["bonitos", "tranquilos"]}}],
                [{"LOWER": "ao"}, {"LOWER": "ar"}, {"LOWER": "livre"}],
                [{"LOWER": {"IN": ["parque", "praia", "trilha", "natureza"]}}, {"IS_ALPHA": True}],
                [{"LOWER": "bares"}],
                [{"LOWER": {"IN": ["pub", "boteco", "balada", "nightclub"]}}],
            ])

            doc = nlp(self.texto)
            stop_words = set(spacy.lang.pt.stop_words.STOP_WORDS)
            tokens_filtrados = [token for token in doc if token.text.lower() not in stop_words and not token.is_punct]
            doc_filtrado = nlp(" ".join([token.text for token in tokens_filtrados]))

            recomendacoes = []
            matches = matcher(doc_filtrado)
            for match_id, start, end in matches:
                span = doc_filtrado[start:end]
                recomendacoes.append(span.text)

            recomendacoes = list(set(recomendacoes))

            local = None
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    if local is None or (len(ent.text.split()) > 1 or ent.text.istitle()):
                        local = ent.text

            msg_atlas_obscura = Message(to="agente_atlas_obscura@localhost")
            msg_atlas_obscura.body = json.dumps({"cidade": local, "preferencias": recomendacoes}, ensure_ascii=False)
            msg_atlas_obscura.set_metadata("performative", "inform")
            msg_atlas_obscura.set_metadata("thread", "atlas_obscura_request")
            await self.send(msg_atlas_obscura)

            msg = Message(to="agente_yelp@localhost")
            msg.body = json.dumps({"cidade": local, "preferencias": recomendacoes}, ensure_ascii=False)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("thread", "yelp_request")
            await self.send(msg)

            msg_foursquare = Message(to="agente_foursquare@localhost")
            msg_foursquare.body = json.dumps({"cidade": local, "preferencias": recomendacoes}, ensure_ascii=False)
            msg_foursquare.set_metadata("performative", "inform")
            msg_foursquare.set_metadata("thread", "foursquare_request")
            await self.send(msg_foursquare)

            msg_cidade_brasil = Message(to="agente_cidade_brasil@localhost")
            msg_cidade_brasil.body = json.dumps({"cidade": local, "preferencias": recomendacoes}, ensure_ascii=False)
            msg_cidade_brasil.set_metadata("performative", "inform")
            msg_cidade_brasil.set_metadata("thread", "cidade_brasil_request")
            await self.send(msg_cidade_brasil)


    async def setup(self):
        processar_behaviour = self.ProcessarTextoBehaviour(self.texto_param)
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "processar_texto_request")
        self.add_behaviour(processar_behaviour, template)


class AgenteAtlasObscura(Agent):
    class AtlasObscuraBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                dados = json.loads(msg.body)
                cidade = dados['cidade'].replace(" ", "-").lower()

                url = f'https://www.atlasobscura.com/things-to-do/{cidade}-brazil/places'
                
                response = requests.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    locais = [item.text.strip() for item in soup.find_all('div', class_='CardText')]
                    
                    msg_resposta = Message(to="agente_coordenador@localhost")
                    msg_resposta.body = json.dumps({
                        "source": "Atlas Obscura",
                        "data": locais
                    })
                    msg_resposta.set_metadata("performative", "inform")
                    msg_resposta.set_metadata("thread", "coordenador_request")
                    await self.send(msg_resposta)

                       
                    
    async def setup(self):
        atlas_obscura_behaviour = self.AtlasObscuraBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "atlas_obscura_request")
        self.add_behaviour(atlas_obscura_behaviour, template)
        

class AgenteYelp(Agent):
    class YelpBehaviour(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.yelp_api_key = 'EVcoTuv6Im8ApisNLkhYcG68F0U1-9PhtC9FYuXQEhGcs9wxs5dAUDptJVcCQKci8lKmT96IavnLb-n_KCh8GXP3EiBC1pFLeLoJW2fBceq_Ln0CzbHBVcaLU-X4ZnYx'
            self.opencage_api_key = '755a7d3d5d8743728e809342a7291d5a'

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                dados = json.loads(msg.body)
                cidade = dados['cidade']
                preferencias = dados['preferencias']

                geolocator = OpenCage(api_key=self.opencage_api_key)
                location = geolocator.geocode(cidade)
                if location:
                    latitude, longitude = location.latitude, location.longitude

                    headers = {'Authorization': f'Bearer {self.yelp_api_key}'}
                    resultados = []
                    for categoria in preferencias:
                        url = 'https://api.yelp.com/v3/businesses/search'
                        params = {'term': categoria, 'latitude': latitude, 'longitude': longitude, 'limit': 10}
                        response = requests.get(url, headers=headers, params=params)
                        if response.status_code == 200:
                            resultados += response.json().get('businesses', [])

                    msg_resposta = Message(to="agente_coordenador@localhost")
                    msg_resposta.body = json.dumps({"Yelp": resultados})
                    msg_resposta.set_metadata("performative", "inform")
                    msg_resposta.set_metadata("thread", "coordenador_request")
                    await self.send(msg_resposta)

                    msg_resposta = Message(to="agente_coordenador@localhost")
                    msg_resposta.body = json.dumps({
                        "source": "Yelp",
                        "data": resultados
                    })
                    msg_resposta.set_metadata("performative", "inform")
                    msg_resposta.set_metadata("thread", "coordenador_request")
                    await self.send(msg_resposta)


    async def setup(self):
        request_behaviour = self.YelpBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "yelp_request")
        self.add_behaviour(request_behaviour, template)


class AgenteFoursquare(Agent):
    class FoursquareBehaviour(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.foursquare_api_key = 'fsq3MZABriF086Ggov3imwdz1lULdW/uvYXFiwr/Rz9pmOo='

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                dados = json.loads(msg.body)
                cidade = dados['cidade']
                preferencias = dados['preferencias']

                url = "https://api.foursquare.com/v3/places/search"
                params = {"query": preferencias, "near": cidade, "limit": 10, "sort": "relevance"}
                headers = {"Accept": "application/json", "Authorization": f'{self.foursquare_api_key}'}
                response = requests.get(url, params=params, headers=headers)

                locais = response.json().get('results', [])

                msg_resposta = Message(to="agente_coordenador@localhost")
                msg_resposta.body = json.dumps({
                    "source": "Foursquare",
                    "data": locais
                })
                msg_resposta.set_metadata("performative", "inform")
                msg_resposta.set_metadata("thread", "coordenador_request")
                await self.send(msg_resposta)

    async def setup(self):
        foursquare_behaviour = self.FoursquareBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "foursquare_request")
        self.add_behaviour(foursquare_behaviour, template)


class AgenteCidadeBrasil(Agent):
    class CidadeBrasilBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                dados = json.loads(msg.body)
                cidade = dados['cidade']

                url = f'https://www.cidade-brasil.com.br/municipio-{cidade}.html'
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    categorias = []
                    for section in soup.find_all('div', class_='ctn-loisir-illustration'):
                        for category in section.find_all('a'):
                            categorias.append(category.text.strip())

                    msg_resposta = Message(to="agente_coordenador@localhost")
                    msg_resposta.body = json.dumps({
                        "source": "Cidade Brasil",
                        "data": categorias
                    })
                    msg_resposta.set_metadata("performative", "inform")
                    msg_resposta.set_metadata("thread", "coordenador_request")
                    await self.send(msg_resposta)
                        

    async def setup(self):
        cidade_brasil_behaviour = self.CidadeBrasilBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "cidade_brasil_request")
        self.add_behaviour(cidade_brasil_behaviour, template)


class AgenteCoordenador(Agent):
    class CoordenadorBehaviour(OneShotBehaviour):
        async def run(self):
            tasks = [
                self.receive_message("Atlas Obscura", timeout=20),
                self.receive_message("Yelp", timeout=20),
                self.receive_message("Foursquare", timeout=20),
                self.receive_message("Cidade Brasil", timeout=20)
            ]
            
            messages = await asyncio.gather(*tasks)

            dados_finais = {source: msg for source, msg in zip(["Atlas Obscura", "Yelp", "Foursquare", "Cidade Brasil"], messages) if msg}

            resposta = await self.gerar_recomendacoes(dados_finais)
            config.resposta_gerada = resposta

        async def receive_message(self, source_name, timeout):
            msg = await self.receive(timeout=timeout)
            if msg:
                return json.loads(msg.body)
            else:
                return None

        async def gerar_recomendacoes(self, dados_finais):
            if dados_finais:
                try:
                    genai.configure(api_key='AIzaSyAyLDHhupk6bAIaXuSnRIDusM7zA7bmO9M')
                    prompt = f"Baseado nos seguintes dados, gere recomendações: {dados_finais}"
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    resposta = "Aqui estão suas recomendações com Gemini:\n"
                    for chunk in response:
                        resposta += chunk.text.replace('*', '').replace('**', '').replace('##', '')
                        if resposta[-1] in [".", ":"]:
                            resposta += '\n'
                    
                    resposta_html = ''.join([f'<p>{paragrafo.strip()}</p>' for paragrafo in resposta.split('\n') if paragrafo.strip()])
                    return Markup(resposta_html)
                
                except Exception as e:
                    return Markup(f"Ocorreu um erro ao gerar recomendações: {str(e)}")

            else:
                return Markup("Nenhum dado recebido para gerar recomendações.")

    async def setup(self):
        coordenador_behaviour = self.CoordenadorBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("thread", "coordenador_request")
        self.add_behaviour(coordenador_behaviour, template)
