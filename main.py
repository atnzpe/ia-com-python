# -*- coding: utf-8 -*-
# main.py - Arquivo principal da aplicação do chatbot "Seu Blusa".
# Este arquivo contém toda a lógica de interface, comunicação com a IA e tratamento de dados.
# O objetivo é criar um assistente virtual com a framework Flet e a API da Groq (LLM).

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# Módulos padrão da biblioteca Flet para a construção da interface gráfica (UI).
import flet as ft
# Módulo padrão do Python para interagir com o sistema operacional, como carregar variáveis de ambiente.
import os
# Módulo padrão do Python para registrar eventos, erros e informações de depuração.
# É fundamental para monitorar o comportamento da aplicação.
import logging
# Módulo padrão do Python para trabalhar com expressões regulares, usado para encontrar URLs em textos.
import re
# Módulo padrão do Python para manipulação de tempo, usado para criar um atraso (pausa) na execução.
import time
# Módulo padrão do Python para tratar erros de requisição HTTP, como o erro 400 (Bad Request).
import urllib.error
# Biblioteca para ler e extrair conteúdo de arquivos PDF. É uma dependência da LangChain.
from pypdf import PdfReader
# Módulo `asyncio` para gerenciar operações assíncronas. Essencial para não travar a UI em operações demoradas.
import asyncio
# Módulo para criar um pool de threads. Usado para executar funções síncronas em segundo plano.
from concurrent.futures import ThreadPoolExecutor
import pytube
# Módulo `pytubefix` e suas exceções específicas para o carregamento de vídeos do YouTube.
# Ele é um fork da biblioteca pytube, mais robusto e atualizado para lidar com as constantes
# mudanças na API do YouTube.
import pytubefix
from pytubefix.exceptions import (
    # Exceção de erro quando a expressão regular não encontra um padrão esperado.
    RegexMatchError,
    # Exceção para vídeos que não estão mais disponíveis no YouTube.
    VideoUnavailable,
    # Exceção para vídeos com restrição de idade.
    AgeRestrictedError,
    # Exceção para vídeos que são transmissões ao vivo.
    LiveStreamError,
    # Exceção genérica na extração de dados do YouTube.
    ExtractError,
    # Exceção na análise do HTML da página.
    HTMLParseError,
    # Exceção quando o limite de tentativas de conexão é excedido.
    MaxRetriesExceeded,
    # Exceção para vídeos privados. (O nome foi corrigido de `VideoPrivateError` para `VideoPrivate`).
    VideoPrivate,
    # Exceção para vídeos bloqueados por região. (O nome foi corrigido de `VideoRegionBlockedError` para `VideoRegionBlocked`).
    VideoRegionBlocked,
)

# Módulos para gerenciar a chave de API e para a comunicação com o modelo de linguagem (LLM).
# `dotenv` é usado para carregar a chave de API de um arquivo `.env`, mantendo-a segura e
# separada do código-fonte.
from dotenv import load_dotenv
# Classe da biblioteca `langchain_groq` para inicializar o modelo de linguagem da Groq.
# Estamos usando o modelo "llama-3.3-70b-versatile".
from langchain_groq import ChatGroq
# Classe para criar prompts estruturados. Isso permite definir um comportamento para a IA.
from langchain.prompts import ChatPromptTemplate

# Módulos de carregamento de documentos da biblioteca LangChain.
# `WebBaseLoader` é a ferramenta para extrair conteúdo de páginas da web.
from langchain_community.document_loaders import WebBaseLoader
# `YoutubeLoader` é a ferramenta para extrair a transcrição de vídeos do YouTube.
from langchain_community.document_loaders import YoutubeLoader
# `PyPDFLoader` é a ferramenta para extrair o conteúdo de arquivos PDF.
from langchain_community.document_loaders import PyPDFLoader

# Módulos para tratar transcrições do YouTube.
# Exceções específicas para quando um vídeo não tem legendas ou as legendas estão desativadas.
from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
)

# -------------------
# 2. CONFIGURAÇÃO E INICIALIZAÇÃO
# -------------------
# Configuração do sistema de logging.
# `filename`: Nome do arquivo onde os logs serão salvos (`chat_app.log`).
# `level`: Nível mínimo de mensagens a serem registradas (INFO, WARNING, ERROR, etc.).
# `format`: Formato da mensagem de log (data, nível, mensagem).
logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Registra que o arquivo `.env` foi carregado com sucesso.
logging.info("Arquivo .env carregado.")
# Carrega as variáveis de ambiente do arquivo `.env`.
load_dotenv()
# Instancia o modelo de linguagem da Groq, passando o nome do modelo e a chave da API.
# A chave é lida da variável de ambiente `GROQ_API_KEY`.
chat = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

# Define o prompt do sistema que instrui a IA sobre sua persona e comportamento.
# Este é o prompt inicial que define o papel do chatbot como "Seu Blusa".
system_prompt = [
    (
        "system",
        "Você é um assistente prestativo e amigável chamado Seu Blusa. Responda sempre em português do Brasil.",
    )
]

# Cria um pool de threads com 5 threads. Isso permite que operações de I/O bloqueantes
# sejam executadas em paralelo sem travar a interface gráfica.
executor = ThreadPoolExecutor(max_workers=5)

# -------------------
# 3. FUNÇÕES AUXILIARES
# -------------------
def find_url(text: str):
    """
    Função que busca por um URL em uma string de texto usando uma expressão regular.

    Args:
        text (str): A string de entrada do usuário.

    Returns:
        str | None: O URL encontrado (ex: 'https://exemplo.com') ou `None` se nenhum for encontrado.
    """
    # Expressão regular para encontrar URLs que começam com 'http://' ou 'https://'.
    url_pattern = r"https?://\S+"
    # `re.search` procura a primeira ocorrência do padrão na string.
    match = re.search(url_pattern, text)
    # Se um padrão for encontrado, retorna o texto correspondente.
    if match:
        return match.group(0)
    # Caso contrário, retorna `None`.
    return None

def is_youtube_url(url: str):
    """
    Função que verifica se um URL pertence ao YouTube.

    Args:
        url (str): O URL a ser verificado.

    Returns:
        bool: `True` se o URL for do YouTube, `False` caso contrário.
    """
    # Expressão regular para encontrar domínios do YouTube.
    youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)"
    # `re.search` procura o padrão do YouTube no URL.
    is_match = re.search(youtube_pattern, url)
    # Retorna `True` se houver uma correspondência, `False` caso contrário.
    if is_match:
        return True
    return False

def is_pdf_file_path(text: str):
    """
    Função que verifica se uma string é um caminho de arquivo que termina com a extensão ".pdf".

    Args:
        text (str): A string a ser verificada.

    Returns:
        bool: `True` se a string for um caminho de arquivo PDF, `False` caso contrário.
    """
    # O método `lower()` é usado para garantir que a verificação não seja case-sensitive.
    return text.lower().endswith(".pdf")

def get_content_from_youtube(url: str):
    """
    Função que carrega a transcrição de um vídeo do YouTube usando a biblioteca `YoutubeLoader`.

    Args:
        url (str): O URL do vídeo do YouTube.

    Returns:
        tuple[str | None, str | None]: Uma tupla contendo o conteúdo da transcrição e uma mensagem de erro,
        ou `None, None` em caso de sucesso.
    """
    logging.info(f"Iniciando carregamento de transcrição do YouTube: {url}")
    try:
        # Tenta carregar a transcrição do URL do YouTube.
        # `add_video_info=True`: Adiciona metadados do vídeo à transcrição.
        # `language`: Define a prioridade de busca por transcrições em diferentes idiomas.
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=True, language=["pt", "en", "es", "pt-BR"]
        )
        docs = loader.load()
        # Concatena o conteúdo de todos os documentos (partes da transcrição) em uma única string.
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Transcrição do YouTube carregada com sucesso para a URL: {url}")
        return content.strip(), None
    # Captura exceções específicas de falta de transcrição.
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        error_message = "Não consegui encontrar transcrições para este vídeo. Verifique se as legendas estão ativadas."
        logging.error(f"Erro de transcrição do YouTube. Erro: {e}", exc_info=True)
        return None, error_message
    # Captura exceções relacionadas a restrições de vídeo ou falhas de rede.
    except (VideoUnavailable, urllib.error.HTTPError, AgeRestrictedError, LiveStreamError, pytubefix.exceptions.VideoPrivate, pytubefix.exceptions.VideoRegionBlocked) as e:
        error_message = f"O vídeo não está disponível ou a requisição foi bloqueada. Verifique o link e tente novamente mais tarde."
        logging.error(f"Erro de acesso ao vídeo do YouTube. Erro: {e}", exc_info=True)
        return None, error_message
    # Captura qualquer outro erro inesperado.
    except Exception as e:
        logging.error(
            f"Falha ao carregar transcrição do YouTube. Erro: {e}", exc_info=True
        )
        error_message = f"Não consegui processar o vídeo deste link: {url}. Por favor, tente com outro link."
        return None, error_message

def get_content_from_pdf(file_path: str):
    """
    Função que carrega o conteúdo de um arquivo PDF local usando `PyPDFLoader`.

    Args:
        file_path (str): O caminho do arquivo PDF.

    Returns:
        tuple[str | None, str | None]: Uma tupla contendo o conteúdo do PDF e uma mensagem de erro,
        ou `None, None` em caso de sucesso.
    """
    logging.info(f"Iniciando carregamento do arquivo PDF: {file_path}")
    try:
        # Verifica se o arquivo existe antes de tentar carregá-lo.
        if not os.path.exists(file_path):
            error_message = f"Arquivo PDF não encontrado no caminho: {file_path}"
            logging.error(error_message)
            return None, error_message

        # Cria uma instância do loader com o caminho do arquivo.
        loader = PyPDFLoader(file_path)
        # Carrega os documentos do PDF.
        docs = loader.load()
        
        # Concatena o conteúdo de todas as páginas em uma única string.
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Conteúdo do PDF carregado com sucesso para o caminho: {file_path}")
        
        return content.strip(), None
    except Exception as e:
        logging.error(
            f"Falha ao carregar o arquivo PDF. Erro: {e}", exc_info=True
        )
        error_message = f"Não consegui ler o arquivo PDF em: {file_path}. O arquivo pode estar corrompido ou com formato inválido."
        return None, error_message

def get_content_from_url(url: str):
    """
    Função que carrega o conteúdo de uma página web padrão usando `WebBaseLoader`.

    Args:
        url (str): O URL da página da web.

    Returns:
        tuple[str | None, str | None]: Uma tupla contendo o conteúdo da página e uma mensagem de erro,
        ou `None, None` em caso de sucesso.
    """
    logging.info(f"Iniciando carregamento de conteúdo da URL padrão: {url}")
    try:
        # Cria uma instância do loader com o URL da página.
        loader = WebBaseLoader(url)
        # Carrega os documentos da página web.
        docs = loader.load()
        # Concatena o conteúdo das páginas em uma única string.
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Conteúdo da URL padrão carregado com sucesso para a URL: {url}")
        return content.strip(), None
    except Exception as e:
        logging.error(
            f"Falha ao carregar conteúdo da URL padrão. Erro: {e}", exc_info=True
        )
        error_message = f"Não consegui acessar a página neste link: {url}. Verifique se o link está correto e se o site está no ar."
        return None, error_message

# -------------------
# 4. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
# -------------------
class ChatMessage(ft.Row):
    """
    Classe que representa um componente de mensagem na interface do chat.
    Cada mensagem é composta por um avatar, o nome do remetente e o texto da mensagem.
    """
    def __init__(self, message: str, user_name: str, message_type: str):
        # Chama o construtor da classe base (ft.Row).
        super().__init__()
        # Alinha verticalmente os controles na linha no topo.
        self.vertical_alignment = ft.CrossAxisAlignment.START
        # Define a lista de controles que compõem a mensagem.
        self.controls = [
            (
                # Cria um avatar para o usuário.
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(user_name)),
                    bgcolor=ft.Colors.BLUE_GREY_200,
                )
                if message_type == "user"
                # Cria um avatar para o chatbot.
                else ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.SMART_TOY_OUTLINED),
                    bgcolor=ft.Colors.GREEN_200,
                )
            ),
            # Cria uma coluna para agrupar o nome e o texto da mensagem.
            ft.Column(
                [
                    # Exibe o nome do remetente em negrito.
                    ft.Text(user_name, weight=ft.FontWeight.BOLD),
                    # Exibe o texto da mensagem. A propriedade `selectable=True` permite que o
                    # usuário selecione e copie o texto.
                    ft.Text(message, selectable=True, width=500, data=message),
                ],
                # `tight=True` remove espaços extras entre os controles da coluna.
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        """
        Método auxiliar para obter as duas primeiras letras do nome do usuário para o avatar.

        Args:
            user_name (str): O nome do usuário.

        Returns:
            str: As duas primeiras letras do nome em maiúsculo (ex: "MA" para "Maria") ou "U"
            se o nome for vazio.
        """
        return user_name[:2].upper() if user_name else "U"

# -------------------
# 5. CLASSE PRINCIPAL DA APLICAÇÃO (FLET)
# -------------------
class MainChatApp:
    """
    Classe que encapsula toda a lógica e a interface da aplicação de chat.
    Isso segue o padrão de design `MVC (Model-View-Controller)`, tornando o código mais
    organizado e fácil de manter.
    """
    def __init__(self, page: ft.Page):
        """
        Construtor da classe. Inicializa todos os componentes da UI e o estado da aplicação.

        Args:
            page (ft.Page): A página principal da aplicação Flet.
        """
        self.page = page
        self._setup_page()
        self._create_controls()
        self._add_controls_to_page()
        self._setup_initial_state()
        logging.info("Aplicação inicializada com sucesso.")

    def _setup_page(self):
        """Método privado para configurar as propriedades iniciais da página."""
        self.page.title = "Chat com Seu Blusa"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.theme_mode = ft.ThemeMode.LIGHT

    def _create_controls(self):
        """Método privado para criar todos os componentes da interface (controles)."""
        self.chat_list = ft.ListView(
            controls=[
                ChatMessage(
                    message="Olá! Eu sou o Seu Blusa. Para começarmos, qual o seu nome?",
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            ],
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
        self.new_message = ft.TextField(
            hint_text="Digite seu nome...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
        )
        self.file_picker = ft.FilePicker(on_result=self.on_dialog_result)
        # Adiciona o seletor de arquivos como uma camada de sobreposição na página.
        self.page.overlay.append(self.file_picker)

        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED, tooltip="Enviar mensagem", on_click=self.send_message
        )
        self.pdf_upload_button = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Enviar arquivo PDF",
            # Ao clicar, o `FilePicker` é ativado para selecionar arquivos PDF.
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["pdf"],
                allow_multiple=False,
            ),
        )
        self.restart_button = ft.ElevatedButton("Reiniciar Chat", on_click=self.restart_chat, icon=ft.Icons.REFRESH)
        self.exit_button = ft.ElevatedButton("Sair", on_click=self.end_chat, icon=ft.Icons.EXIT_TO_APP)

    def _add_controls_to_page(self):
        """Método privado para adicionar os controles à página na ordem correta."""
        self.page.add(
            ft.Row(
                [self.restart_button, self.exit_button],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Container(
                content=self.chat_list,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            # Linha contendo o campo de texto, o botão de upload e o botão de envio.
            ft.Row([self.new_message, self.pdf_upload_button, self.send_button]),
        )
        # Vincula a função de envio ao evento de pressionar "Enter" no campo de texto.
        self.new_message.on_submit = self.send_message

    def _setup_initial_state(self):
        """Método privado para configurar as variáveis de sessão e o estado inicial da aplicação."""
        # O estado `onboarding_state` controla o fluxo inicial da conversa.
        self.page.session.set("onboarding_state", "awaiting_name")
        # O histórico de mensagens é mantido na sessão para contexto da IA.
        self.page.session.set("history", [])

    def send_message(self, e):
        """
        Função de callback acionada ao enviar uma mensagem.
        Gerencia o fluxo de onboarding e o envio de mensagens.

        Args:
            e: Objeto do evento.
        """
        user_message_text = self.new_message.value
        # Ignora mensagens vazias para evitar processamento desnecessário.
        if not user_message_text.strip():
            self.page.update()
            return

        # Limpa o campo de entrada e atualiza a UI imediatamente.
        self.new_message.value = ""
        self.page.update()
        logging.info(f"Mensagem recebida do usuário: '{user_message_text}'")

        current_state = self.page.session.get("onboarding_state")
        
        # Usa um `if/elif` para rotear a lógica com base no estado atual da conversa.
        if current_state == "awaiting_name":
            self.handle_awaiting_name(user_message_text)
        elif current_state == "awaiting_confirmation":
            self.handle_awaiting_confirmation(user_message_text)
        elif current_state == "onboarding_complete":
            # CORREÇÃO: Chama a função assíncrona usando `run_task` para não bloquear a UI.
            self.page.run_task(self.handle_chat_message, user_message_text)
        
        # Força uma atualização final da página para refletir as mudanças.
        self.page.update()
        self.new_message.focus()

    def handle_awaiting_name(self, user_message_text: str):
        """
        Gerencia a lógica quando o aplicativo está esperando o nome do usuário.
        Adiciona a mensagem do usuário e responde com um pedido de confirmação.
        """
        self.chat_list.controls.append(
            ChatMessage(message=user_message_text, user_name="Usuário", message_type="user")
        )
        self.page.session.set("pending_name", user_message_text)
        bot_response_text = f"Entendido, você gostaria de usar o nome '{user_message_text}'? (Sim/Não)"
        self.page.session.set("onboarding_state", "awaiting_confirmation")
        self.chat_list.controls.append(
            ChatMessage(message=bot_response_text, user_name="Seu Blusa", message_type="assistant")
        )

    def handle_awaiting_confirmation(self, user_message_text: str):
        """
        Gerencia a lógica quando o aplicativo está esperando a confirmação do nome.
        Se a resposta for "sim", o onboarding é concluído. Caso contrário, pede o nome novamente.
        """
        self.chat_list.controls.append(
            ChatMessage(message=user_message_text, user_name="Usuário", message_type="user")
        )
        affirmative_responses = ["sim", "s", "ok", "claro", "yes"]
        # Verifica se a resposta do usuário é uma das opções afirmativas.
        if user_message_text.lower() in affirmative_responses:
            user_name = self.page.session.get("pending_name")
            self.page.session.set("user_name", user_name)
            self.page.session.set("onboarding_state", "onboarding_complete")
            bot_response_text = (
                f"Perfeito, {user_name}! Prazer em conhecê-lo. "
                "Agora, como posso te ajudar? "
                "Faça uma pergunta, envie um link de site ou YouTube, "
                "ou use o botão de upload para um PDF."
            )
            self.new_message.hint_text = "Digite sua mensagem ou pergunta..."
        else:
            bot_response_text = "Sem problemas. Qual nome você gostaria de usar?"
            self.page.session.set("onboarding_state", "awaiting_name")
            self.new_message.hint_text = "Digite seu nome..."
        
        self.chat_list.controls.append(
            ChatMessage(message=bot_response_text, user_name="Seu Blusa", message_type="assistant")
        )

    async def handle_chat_message(self, user_message_text: str):
        """
        Função assíncrona que gerencia a lógica principal do chat (após o onboarding).
        Processa perguntas, links e PDFs em segundo plano para não travar a UI.
        """
        user_name = self.page.session.get("user_name") or "Usuário"
        
        # Adiciona um indicador de "analisando..." e atualiza a UI imediatamente para feedback visual.
        thinking_indicator = ChatMessage(
            message="analisando...", user_name="Seu Blusa", message_type="assistant"
        )
        self.chat_list.controls.append(thinking_indicator)
        self.page.update()
        
        # Obtém o loop de eventos atual para agendar tarefas.
        loop = asyncio.get_event_loop()
        
        history = self.page.session.get("history")
        url = find_url(user_message_text)
        is_pdf = is_pdf_file_path(user_message_text)
        content, error_message = None, None
        
        if url:
            clean_url = url.split('&t=')[0] if '&t=' in url else url
            # Executa a função síncrona `get_content_from_youtube` ou `get_content_from_url`
            # em um thread separado para não bloquear o loop de eventos.
            content, error_message = await loop.run_in_executor(executor, get_content_from_youtube, clean_url) if is_youtube_url(url) else await loop.run_in_executor(executor, get_content_from_url, clean_url)
        elif is_pdf:
            pdf_path = user_message_text
            # Executa a função síncrona `get_content_from_pdf` em um thread separado.
            content, error_message = await loop.run_in_executor(executor, get_content_from_pdf, pdf_path)
        
        # Lógica para determinar a fonte da informação.
        if not url and not is_pdf:
            # Lógica para perguntas gerais.
            history.append(("user", user_message_text))
            template = ChatPromptTemplate.from_messages(system_prompt + history)
            chain = template | chat
            # Usa o método assíncrono `ainvoke` para fazer a chamada à API da Groq
            # de forma não bloqueante.
            bot_response_text = await chain.ainvoke({})
            bot_response_text = bot_response_text.content
        elif content:
            content_type = ""
            if url and is_youtube_url(url):
                content_type = "da transcrição do vídeo do YouTube"
            elif url:
                content_type = "da página web"
            elif is_pdf:
                content_type = "do arquivo PDF"
                
            prompt_text = f"""
            Com base no seguinte conteúdo extraído {content_type} '{user_message_text}':
            --- CONTEÚDO ---
            {content[:4000]}
            --- FIM DO CONTEÚDO ---
            
            Responda à pergunta do usuário de forma concisa e útil.
            Se a pergunta sugerir uma lista (ex: "cite", "liste", "quais são"),
            formate a resposta como uma lista, usando marcadores ou numeração.
            
            Pergunta do usuário: '{user_message_text}'"""
            
            prompt_completo = [("user", prompt_text)]
            template = ChatPromptTemplate.from_messages(prompt_completo)
            chain = template | chat
            # Usa o método assíncrono `ainvoke` para a chamada à API.
            bot_response_text = await chain.ainvoke({})
            bot_response_text = bot_response_text.content
        elif error_message:
            bot_response_text = error_message
        else:
             bot_response_text = "Desculpe, não consegui processar a sua solicitação. Poderia tentar novamente?"

        # Remove o indicador de "analisando..." e adiciona a resposta final do bot.
        # A UI só é atualizada depois que a operação demorada é concluída.
        self.chat_list.controls.pop()
        self.chat_list.controls.append(
            ChatMessage(
                message=bot_response_text,
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        
        # Adiciona a conversa ao histórico da sessão.
        history.append(("user", user_message_text))
        history.append(("assistant", bot_response_text))
        self.page.session.set("history", history)
        
        # Atualiza a interface e foca no campo de entrada.
        self.page.update()
        self.new_message.focus()

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        """
        Função de callback chamada quando um arquivo é selecionado via FilePicker.

        Args:
            e (ft.FilePickerResultEvent): Objeto do evento de resultado do seletor de arquivos.
        """
        logging.info("Evento do FilePicker acionado.")
        if e.files is not None and len(e.files) > 0:
            file_path = e.files[0].path
            logging.info(f"Arquivo selecionado: {file_path}")
            
            # Coloca o caminho do arquivo no campo de texto e chama a função de envio.
            self.new_message.value = file_path
            self.send_message(e)

    def restart_chat(self, e):
        """
        Função para reiniciar completamente o chat.
        Limpa o histórico de conversa e restaura a interface para o estado inicial.
        """
        self.page.session.clear()
        self.page.session.set("onboarding_state", "awaiting_name")
        self.page.session.set("history", [])
        
        self.chat_list.controls.clear()
        self.chat_list.controls.append(
            ChatMessage(
                message="Olá! Eu sou o Seu Blusa. Para começarmos, qual o seu nome?",
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        self.new_message.value = ""
        self.new_message.hint_text = "Digite seu nome..."
        self.new_message.disabled = False
        self.send_button.disabled = False
        self.page.update()
        logging.info("Chat reiniciado.")

    def end_chat(self, e):
        """
        Função para finalizar o chat e, em seguida, reiniciá-lo após um breve atraso.
        Desabilita a entrada de texto e o botão de envio.
        """
        user_name = self.page.session.get("user_name") or "usuário"
        final_message = f"Até mais, {user_name}!"
        
        self.chat_list.controls.append(
            ChatMessage(
                message=final_message, user_name="Seu Blusa", message_type="assistant"
            )
        )
        self.new_message.disabled = True
        self.send_button.disabled = True
        self.page.update()
        logging.info(f"Chat finalizado. Mensagem de despedida enviada para '{user_name}'.")

        # Cria um pequeno atraso de 2 segundos antes de reiniciar.
        time.sleep(2)
        # Chama a função de reinício do chat.
        self.restart_chat(e)

def main(page: ft.Page):
    """
    Função principal que inicializa a aplicação Flet.
    É o ponto de entrada da aplicação.
    """
    MainChatApp(page)

# -------------------
# 6. INICIALIZAÇÃO DA APLICAÇÃO
# -------------------
# Inicia a aplicação Flet, usando a função `main` como ponto de entrada.
# `view=ft.WEB_BROWSER` executa a aplicação em um navegador web.
ft.app(target=main, view=ft.WEB_BROWSER)