# Chatbot "Seu Blusa"

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)

Um chatbot de desktop/web chamado "Seu Blusa", construído com Python. Ele usa uma interface gráfica interativa para responder às perguntas dos usuários de forma amigável.

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface Gráfica:** Flet
* **Inteligência Artificial:** LangChain com a API da Groq (modelo Llama 3)

## Como Executar

Siga os passos abaixo para rodar o projeto.

### 1. Clone o Repositório

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
python-dotenv
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

## Próximos Passos

-   [ ] Dar ao bot acesso a sites.
-   [ ] Permitir que o bot leia PDFs e vídeos do YouTube.
-   [ ] Melhorar a estrutura do código.
-   [ ] Criar um instalador para o projeto.

## Licença

Este projeto é distribuído sob a licença GNU GPL v3.0. Veja o arquivo LICENSE para mais detalhes.