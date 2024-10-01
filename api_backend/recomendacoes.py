import spacy
import nltk
import requests
from spacy.matcher import Matcher
from nltk.corpus import stopwords
from geopy.geocoders import OpenCage
from bs4 import BeautifulSoup

nltk.download('stopwords')

class AgenteProcessorTexto:
    def __init__(self):
        self.nlp = spacy.load("pt_core_news_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self.matcher.add("RECOMENDACOES", [
            [{"LOWER": {"IN": ["restaurante", "gastronomia", "comida"]}}, {"IS_ALPHA": True}],
            [{"LOWER": "comida"}, {"LOWER": {"IN": ["japonesa", "mexicana"]}}],
            [{"LOWER": "visitar"}, {"IS_ALPHA": True}],
            [{"LOWER": "pontos"}, {"LOWER": "turísticos"}],
        ])
        self.stop_words = set(stopwords.words('portuguese'))

    def processar_texto(self, texto):
        doc = self.nlp(texto)
        local = None
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                local = ent.text
                break

        tokens_filtrados = [token for token in doc if token.text.lower() not in self.stop_words]
        doc_filtrado = self.nlp(" ".join([token.text for token in tokens_filtrados]))

        recomendacoes = []
        matches = self.matcher(doc_filtrado)
        for _, start, end in matches:
            span = doc_filtrado[start:end]
            recomendacoes.append(span.text)
        return local, list(set(recomendacoes))
    
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