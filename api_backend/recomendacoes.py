import spacy
import nltk
import requests
from spacy.matcher import Matcher
from nltk.corpus import stopwords
from geopy.geocoders import OpenCage
from bs4 import BeautifulSoup
import google.generativeai as genai

nltk.download('stopwords')

class AgenteProcessorTexto:
    def __init__(self):
        self.nlp = spacy.load("pt_core_news_sm")
        self.matcher = Matcher(self.nlp.vocab)

        self.matcher.add("RECOMENDACOES", [
            [{"LOWER": {"IN": ["restaurante", "culinária", "comida", "gastronomia", "cozinha"]}}, {"IS_ALPHA": True}],
            [{"LOWER": "comida"}, {"LOWER": {"IN": ["japonesa", "mexicana", "italiana", "brasileira", "francesa"]}}],
            [{"LOWER": "culinária"}, {"LOWER": {"IN": ["local", "regional", "internacional"]}}],

            [{"LOWER": "visitar"}, {"IS_ALPHA": True}],
            [{"LOWER": {"IN": ["museu", "galeria", "exposições", "obras"]}}, {"IS_ALPHA": True}],
            [{"LOWER": "apreciar"}, {"IS_ALPHA": True}],

            [{"LOWER": "pontos"}, {"LOWER": "turísticos"}],
            [{"LOWER": {"IN": ["vistas", "locais", "lugares", "ambientes"]}}, {"LOWER": {"IN": ["bonitos", "tranquilos"]}}],

            [{"LOWER": "ao"}, {"LOWER": "ar"}, {"LOWER": "livre"}],
            [{"LOWER": {"IN": ["parque", "praia", "trilha", "natureza"]}}, {"IS_ALPHA": True}],
        ])

        self.stop_words = {
            'de', 'da', 'do', 'dos', 'das', 'e', 'para', 'o', 'a', 'os', 'as', 'um', 'uma', 'em', 'por', 'com',
            'que', 'é', 'na', 'no', 'nos', 'nas', 'eu', 'meu', 'minha', 'seu', 'sua', 'seus', 'suas',
            'vou', 'são', 'quero', 'estou', 'ele', 'ela', 'eles', 'elas', 'isso', 'aquilo', 'assim', 'como',
            'também'
            }

    def processar_texto(self, texto):
        doc = self.nlp(texto)

        local = None
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                if local is None or (ent.text.lower() != local.lower() and len(ent.text.split()) == 1):
                    local = ent.text
                    break

        tokens_filtrados = [token for token in doc if token.text.lower() not in self.stop_words and not token.is_punct]
        doc_filtrado = self.nlp(" ".join([token.text for token in tokens_filtrados]))

        recomendacoes = []
        matches = self.matcher(doc_filtrado)
        for match_id, start, end in matches:
            span = doc_filtrado[start:end]
            recomendacoes.append(span.text)

        recomendacoes = list(set(recomendacoes))
        return local, recomendacoes
    
class AgenteYelp:
    def __init__(self, yelp_api_key, opencage_api_key):
        self.yelp_api_key = yelp_api_key
        self.opencage_api_key = opencage_api_key

    def buscar_no_yelp(self, cidade, categorias):
        geolocator = OpenCage(api_key=self.opencage_api_key)
        location = geolocator.geocode(cidade)
        if location:
            latitude, longitude = location.latitude, location.longitude
        else:
            return None

        headers = {'Authorization': f'Bearer {self.yelp_api_key}'}
        resultados = []
        for categoria in categorias:
            url = 'https://api.yelp.com/v3/businesses/search'
            params = {'term': categoria, 'latitude': latitude, 'longitude': longitude, 'limit': 10}
            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    resultados += response.json().get('businesses', [])
            except requests.exceptions.RequestException as e:
                print(f"Erro no Yelp: {e}")
        return resultados

class AgenteFoursquare:
  def __init__(self, foursquare_api_key):
        self.foursquare_api_key = foursquare_api_key

  def buscar_no_foursquare(self, destino, preferencias):
      url = "https://api.foursquare.com/v3/places/search"

      params = {
          "query": preferencias,
          "near": destino,
          "limit": 10,
          "sort": "relevance"
      }

      headers = {
          "Accept": "application/json",
          "Authorization": f'{self.foursquare_api_key}'
      }

      try:
          response = requests.get(url, params=params, headers=headers)
          response.raise_for_status()

          locais = response.json()
          return locais.get('results', [])

      except requests.exceptions.HTTPError as err:
          print(f"Erro na requisição: {err}")
          return None
      except Exception as e:
          print(f"Ocorreu um erro: {e}")
          return None

class AgenteCidadeBrasil:
    def __init__(self):
        self.url_base = 'https://www.cidade-brasil.com.br'

    def buscar_no_cidade_brasil(self, cidade):
        url = f'{self.url_base}/municipio-{cidade}.html'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            categorias = []
            for section in soup.find_all('div', class_='ctn-loisir-illustration'):
                for category in section.find_all('a'):
                    categorias.append(category.text.strip())
            return categorias
        return []
    
class AgenteAtlasObscura:
    def buscar_no_atlas_obscura(self, cidade):
        url = f'https://www.atlasobscura.com/things-to-do/{cidade}-brazil/places'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            lugares = [place.text.strip() for place in soup.find_all('h3', class_="Card__heading")]
            return lugares
        return []
    
class AgenteCoordenador:
    def __init__(self, agentes):
        self.agentes = agentes

    def coletar_informacoes(self, cidade, preferencias):
        informacoes = {}
        for nome_agente, agente in self.agentes.items():
            if nome_agente == 'Cidade Brasil':
                resultados = agente.buscar_no_cidade_brasil(cidade)
            elif nome_agente == 'Atlas Obscura':
                resultados = agente.buscar_no_atlas_obscura(cidade)
            elif nome_agente == 'Yelp':
                resultados = agente.buscar_no_yelp(cidade, preferencias)
            else:
                resultados = agente.buscar_no_foursquare(cidade, preferencias)
            informacoes[nome_agente] = resultados
        return informacoes

    def gerar_resposta(self, informacoes):
        resposta = "Aqui estão suas recomendações:\n"
        for fonte, locais in informacoes.items():
            resposta += f"Fonte: {fonte}\n"
            if locais:
              for local in locais:
                  if isinstance(local, dict):
                      resposta += f"- {local.get('name', 'Local não informado')} em {local.get('location', 'Localização não informada')}\n"
                  else:
                      resposta += f"- {local}\n"
        return resposta

    def gerar_resposta_com_gemini(self, cidade, preferencias):
        locais = self.coletar_informacoes(cidade, preferencias)
        input_text = f"Recomende os seguintes locais em {cidade}: {', '.join(locais)}. O usuário gostaria de experimentar {', '.join(preferencias)}."
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_text, stream=True)

        resposta = "Aqui estão suas recomendações com Gemini:\n"
        for chunk in response:
            resposta += chunk.text.replace('*', '').replace('**', '') + '\n'
        return resposta


nlp = spacy.load("pt_core_news_sm")
if __name__ == "__main__":
    agente_processor = AgenteProcessorTexto()
    agente_yelp = AgenteYelp(yelp_api_key='EVcoTuv6Im8ApisNLkhYcG68F0U1-9PhtC9FYuXQEhGcs9wxs5dAUDptJVcCQKci8lKmT96IavnLb-n_KCh8GXP3EiBC1pFLeLoJW2fBceq_Ln0CzbHBVcaLU-X4ZnYx',
                             opencage_api_key='755a7d3d5d8743728e809342a7291d5a')
    agente_foursquare = AgenteFoursquare(foursquare_api_key='fsq3MZABriF086Ggov3imwdz1lULdW/uvYXFiwr/Rz9pmOo=')
    agente_cidade_brasil = AgenteCidadeBrasil()
    agente_atlas_obscura = AgenteAtlasObscura()

    coordenador = AgenteCoordenador({
        'Yelp': agente_yelp,
        'Foursquare': agente_foursquare,
        'Cidade Brasil': agente_cidade_brasil,
        'Atlas Obscura': agente_atlas_obscura
    })

    # Exemplo de uso
    texto_usuario = "Quero visitar João Pessoa e experimentar comida japonesa."
    local, recomendacoes = agente_processor.processar_texto(texto_usuario)
    informacoes = coordenador.coletar_informacoes(local, recomendacoes)
    resposta = coordenador.gerar_resposta(informacoes)
    resposta_gemini = coordenador.gerar_resposta_com_gemini(informacoes)
    print(resposta)