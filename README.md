# Chatbot "Seu Blusa"

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Version](https://img.shields.io/badge/version-v1.4.1-blue)

Um chatbot de desktop/web chamado "Seu Blusa", construído com Python. Ele usa uma interface gráfica interativa para responder às perguntas dos usuários de forma amigável, podendo analisar conteúdo de links e documentos.

## Tecnologias Utilizadas

* [cite_start]**Linguagem:** Python 3.9+ 
* [cite_start]**Interface Gráfica:** Flet 
* [cite_start]**Inteligência Artificial:** LangChain com a API da Groq (modelo Llama 3) 
* [cite_start]**Gerenciamento de Dependências:** Poetry 
* [cite_start]**Outros:** PyPDF (para leitura de arquivos PDF), Pytubefix (para transcrição do YouTube) 

## Versão

**Versão atual:** v1.4.1

## Funcionalidades

-   [cite_start][x] Interface de chat interativa com histórico de conversas. 
-   [cite_start][x] Análise de conteúdo de páginas web a partir de um link. 
-   [cite_start][x] Leitura e interpretação de documentos PDF via upload. 
-   [cite_start][x] Extração de transcrições de vídeos do YouTube. 
-   [cite_start][x] Controles de chat para reiniciar ou finalizar a conversa. 
-   [cite_start][x] Fluxo de onboarding para personalização com o nome do usuário. 

## A Fazer

-   [cite_start][ ] Criar uma arquitetura para que o Bot aprenda com as conversas e crie uma base de conhecimento. 
-   [cite_start][ ] Criar um instalador para o projeto (Desktop e APK). 
-   [cite_start][ ] Fazer o Deploy da aplicação no Fly.io. 
-   [cite_start][ ] Evoluir o projeto para um produto comercializável. 

## Como Executar o Projeto

Siga os passos abaixo para configurar e rodar o projeto em seu ambiente local.

### 1. Pré-requisitos

-   [cite_start]Python 3.9 ou superior 
-   Poetry (gerenciador de dependências). [cite_start]Se não tiver, instale com: 
    ```bash
    pip install poetry
    ```

### 2. Clone o Repositório

```bash
git clone [https://github.com/atnzpe/ia-com-python.git](https://github.com/atnzpe/ia-com-python.git)
cd ia-com-python
```

### 3. Instale as Dependências
Com o Poetry instalado, execute o comando abaixo na raiz do projeto. Ele criará um ambiente virtual e instalará todas as dependências listadas no `pyproject.toml` de forma automática.

```bash
poetry install
```

### 4. Configure sua Chave de API
Crie um arquivo chamado `.env` na pasta principal do projeto. Dentro dele, adicione sua chave da Groq e o nome do modelo:

```env
# Adicione sua chave de API da Groq
GROQ_API_KEY="sua_chave_aqui"

# Defina o modelo da Groq a ser utilizado (ex: llama3-70b-8192)
GROQ_MODEL_NAME="llama-3.3-70b-versatile"
```

### 5. Execute a Aplicação
Para iniciar o chatbot, ative o ambiente virtual criado pelo Poetry e execute o arquivo `main.py`.

```bash
poetry run python main.py
```

A aplicação será aberta em seu navegador web padrão.

### Licença
Este projeto é distribuído sob a licença GNU GPL v3.0.