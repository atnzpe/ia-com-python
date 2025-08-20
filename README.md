# Chatbot "Seu Blusa"

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)

Um chatbot de desktop/web chamado "Seu Blusa", construído com Python. Ele usa uma interface gráfica interativa para responder às perguntas dos usuários de forma amigável.

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface Gráfica:** Flet
* **Inteligência Artificial:** LangChain com a API da Groq (modelo Llama 3)
* **Outros:** PyPDF (para leitura de arquivos PDF)

## Versão

**Versão atual:** v0.7.2

## Feitos

-   [x] Dar ao bot acesso a sites.
-   [x] Permitir que o bot leia PDFs e vídeos do YouTube.
-   [x] Adicionar botões de controle de chat (Sair, Reiniciar).
-   [x] Melhorar a estrutura de conversação inicial (onboarding).
-   [x] Ao clicar no botão 'Sair', permitir iniciar uma conversa.

## A fazer

-   [ ] Criar uma arquitetura para que o Bot comece a aprender com as conversas que tem com o usuário, para que se torne um bot de atendimento versátil. Ele pode se necessário criar um arquivo de base de conhecimento.
-   [ ] Criar um instalador para o projeto para APK.
-   [ ] Fazer o Deploy no Fly.io.
-   [ ] Criar um produto que possa ser comercializado.

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