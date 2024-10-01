<h1 align="center">TripAI :airplane: 🏝️ </h1>

Projeto de construção de um sistema multiagente para recomendações de locais, com base nas preferências do usuário e o destino desejado.

### Índice

[Configuração do ambiente de trabalho](#Configurar-o-ambiente-de-trabalho)

[Inicialização da aplicação](#Iniciar-a-aplicação)

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
```
------
#### Iniciar a aplicação

Para iniciar a aplicação, usar os seguintes comandos:

```
python app.py
```

------
#### Status do Projeto

Desenvolvido ao final da disciplina de Processamento de Linguagem Natural - Prof. Leando Balby.
