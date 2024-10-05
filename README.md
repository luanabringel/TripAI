<h1 align="center">TripAI :airplane: 🏝️ </h1>

Projeto de construção de um sistema multiagente para recomendações de locais, com base nas preferências do usuário e o destino desejado.
Diga o seu destino e nós iremos recomendar lugares que combinam com você! Este sistema utiliza uma arquitetura de multiagentes para analisar suas preferências pessoais e fornecer sugestões personalizadas de locais. Ao integrar dados de várias APIs, como Yelp e Foursquare, e considerar fatores como interesses, atividades e características do destino, desejamos que você encontre experiências que realmente ressoem com seu estilo.

### Índice

[Configuração do ambiente de trabalho](#Configurar-o-ambiente-de-trabalho)

[Inicialização da aplicação](#Iniciar-a-aplicação)

[Documentação do Projeto](#Documentação-do-Projeto)

[Status do Projeto](#status-do-Projeto)


------
#### Configurar o ambiente de trabalho

Para configurar o ambiente de trabalho pela primeira vez, utilizar os seguintes comandos:

```
# 1. Instalar o pacote do ambiente virtual

 - No Unix
apt install python3.10-venv


# 2. Criar o ambiente virtual

python -m venv .venv


# 3. Ativar o ambiente virtual
 
 - No Windows:
.venv\Scripts\activate

 - No Unix ou MacOS:
source .venv/bin/activate

# 4. Instalar as dependências

pip install -r requirements/requirements.txt

# 5. Instalar a biblioteca SpaCy

python -m spacy download pt_core_news_sm

ou

!python -m spacy download pt_core_news_sm

# 6. Instalar o Flask assíncrono

pip install flask[async]

# 7. Instalar o framework SPADE

pip install spade

por favor, ignore o erro de conflito do Jinja2.
```
------
#### Iniciar a aplicação

Para iniciar a aplicação, usar os seguintes comandos:

```
python app.py
```
------
### Documentação do Projeto

Para entender melhor como foi desenvolvido e o objetivo do projeto, por favor, leia o documento abaixo:

```
https://docs.google.com/document/d/181PjTpi2p64JFqyvcroRWFLdVAZjwsdgfiSmtaQx0E4/edit?usp=sharing
```
------
#### Status do Projeto

Desenvolvido ao final da disciplina de Processamento de Linguagem Natural - Prof. Leandro Balby.
