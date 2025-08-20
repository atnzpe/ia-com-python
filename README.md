# Chatbot "Seu Blusa"

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Version](https://img.shields.io/badge/version-v1.4.0-blue)

Um chatbot de desktop/web chamado "Seu Blusa", construído com Python. Ele usa uma interface gráfica interativa para responder às perguntas dos usuários de forma amigável, podendo analisar conteúdo de links e documentos.

## Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Interface Gráfica:** Flet
* **Inteligência Artificial:** LangChain com a API da Groq (modelo Llama 3)
* **Gerenciamento de Dependências:** Poetry
* **Outros:** PyPDF (para leitura de arquivos PDF), Pytubefix (para transcrição do YouTube)

## Versão

**Versão atual:** v1.4.0

## Funcionalidades

-   [x] Interface de chat interativa com histórico de conversas.
-   [x] Análise de conteúdo de páginas web a partir de um link.
-   [x] Leitura e interpretação de documentos PDF via upload.
-   [x] Extração de transcrições de vídeos do YouTube.
-   [x] Controles de chat para reiniciar ou finalizar a conversa.
-   [x] Fluxo de onboarding para personalização com o nome do usuário.

## A Fazer

-   [ ] Criar uma arquitetura para que o Bot aprenda com as conversas e crie uma base de conhecimento.
-   [ ] Criar um instalador para o projeto (Desktop e APK).
-   [ ] Fazer o Deploy da aplicação no Fly.io.
-   [ ] Evoluir o projeto para um produto comercializável.

## Como Executar o Projeto

Siga os passos abaixo para configurar e rodar o projeto em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.9 ou superior
-   Poetry (gerenciador de dependências). Se não tiver, instale com:
    ```bash
    pip install poetry
    ```

### 2. Clone o Repositório

```bash
git clone [https://github.com/atnzpe/ia-com-python.git](https://github.com/atnzpe/ia-com-python.git)
cd ia-com-python
```


### 2. Crie um Ambiente Virtual

#### No macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```
#### No Windows
```
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instale as Dependências
Crie um arquivo requirements.txt com o conteúdo abaixo:

```
flet
langchain
langchain-groq
langchain-core
langchain-openai
langchain-community
python-dotenv
beautifulsoup4
```
E depois instale-o:

```
pip install -r requirements.txt
```
### 4. Configure sua Chave de API
1. Crie um arquivo chamado .env na pasta principal do projeto.

2. Dentro dele, adicione sua chave da Groq:
```
GROQ_API_KEY="sua_chave_aqui"
```

#### s. Atualize o Código
Garanta que seu arquivo Python (chatbot_flet_groq_e_logchain.py) carregue a chave do arquivo .env em vez de tê-la no código.

Adicione no início do script:
```Python

import os
from dotenv import load_dotenv

load_dotenv()
```
E use 
```Python
os.environ['GROQ_API_KEY']
```

para pegar a chave.



## Licença

Este projeto é distribuído sob a licença GNU GPL v3.0. Veja o arquivo LICENSE para mais detalhes.