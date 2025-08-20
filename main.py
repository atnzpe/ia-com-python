# -*- coding: utf-8 -*-
# main.py - Arquivo principal da aplicação do chatbot "Seu Blusa".
# Este arquivo contém toda a lógica de interface, comunicação com a IA e tratamento de dados.

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# Módulos padrão da biblioteca Flet para construção da interface gráfica.
import flet as ft

# Módulo para interagir com o sistema operacional, como carregar variáveis de ambiente.
import os

# Módulo para registrar eventos, erros e informações de depuração.
import logging

# Módulo para trabalhar com expressões regulares, usado para encontrar URLs.
import re

# Módulo para manipulação de tempo, usado para criar um atraso.
import time

# Módulo para tratar erros de requisição HTTP.
import urllib.error

# Biblioteca para ler e extrair conteúdo de arquivos PDF.
from pypdf import PdfReader

# Módulo `pytubefix` e suas exceções específicas para o carregamento de vídeos do YouTube.
# Ele é um fork do pytube e é mais robusto contra as mudanças da API do YouTube.
import pytubefix
from pytubefix.exceptions import (
    # Erro quando a expressão regular falha ao encontrar um padrão.
    RegexMatchError,
    # Erro para vídeos que não estão disponíveis.
    VideoUnavailable,
    # Erro para vídeos com restrição de idade.
    AgeRestrictedError,
    # Erro para vídeos que são transmissões ao vivo.
    LiveStreamError,
    # Erro genérico na extração de dados do YouTube.
    ExtractError,
    # Erro na análise do HTML da página.
    HTMLParseError,
    # Erro quando o limite de tentativas de conexão é excedido.
    MaxRetriesExceeded,
    VideoPrivate,
)

# Módulos para gerenciar a chave de API e para a comunicação com o modelo de linguagem.
# `dotenv` para carregar a chave de API de um arquivo .env.
from dotenv import load_dotenv

# Classe do modelo de linguagem da Groq (llama-3.3-70b-versatile).
from langchain_groq import ChatGroq

# Classe para criar prompts estruturados para a IA.
from langchain.prompts import ChatPromptTemplate

# Módulos de carregamento de documentos da biblioteca LangChain.
# `WebBaseLoader` para extrair conteúdo de páginas da web.
from langchain_community.document_loaders import WebBaseLoader

# `YoutubeLoader` para extrair a transcrição de vídeos do YouTube.
from langchain_community.document_loaders import YoutubeLoader

# `PyPDFLoader` para extrair conteúdo de arquivos PDF.
from langchain_community.document_loaders import PyPDFLoader

# Módulos para tratar transcrições do YouTube.
# `TranscriptsDisabled` e `NoTranscriptFound` são exceções específicas.
from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
)

# -------------------
# 2. CONFIGURAÇÃO E INICIALIZAÇÃO
# -------------------
# Configura o sistema de logging para gravar em um arquivo chamado `chat_app.log`.
# `level=logging.INFO` define o nível mínimo de mensagens a serem registradas.
# `format` define o formato da mensagem de log.
logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Arquivo .env carregado.")
# Carrega as variáveis de ambiente do arquivo .env.
load_dotenv()
chat = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

# Define o prompt do sistema que instrui a IA sobre sua persona e comportamento.
# Este prompt inicial será usado no histórico da conversa.
system_prompt = [
    (
        "system",
        "Você é um assistente prestativo e amigável chamado Seu Blusa. Responda sempre em português do Brasil.",
    )
]


# -------------------
# 3. FUNÇÕES AUXILIARES
# -------------------
def find_url(text: str):
    """
    Busca por um URL em uma string de texto usando uma expressão regular.

    Args:
        text (str): A string de entrada do usuário.

    Returns:
        str | None: O URL encontrado ou None se nenhum for encontrado.
    """
    url_pattern = r"https?://\S+"
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    return None


def is_youtube_url(url: str):
    """
    Verifica se um URL pertence ao YouTube.

    Args:
        url (str): O URL a ser verificado.

    Returns:
        bool: True se for um URL do YouTube, False caso contrário.
    """
    youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)"
    is_match = re.search(youtube_pattern, url)
    if is_match:
        return True
    return False


def is_pdf_file_path(text: str):
    """
    Verifica se uma string é um caminho de arquivo que termina com .pdf.

    Args:
        text (str): A string a ser verificada.

    Returns:
        bool: True se for um caminho de arquivo PDF, False caso contrário.
    """
    return text.lower().endswith(".pdf")


def get_content_from_youtube(url: str):
    """
    Carrega a transcrição de um vídeo do YouTube usando YoutubeLoader.

    Args:
        url (str): O URL do vídeo do YouTube.

    Returns:
        tuple[str | None, str | None]: Uma tupla com o conteúdo e uma mensagem de erro (se houver).
    """
    logging.info(f"Iniciando carregamento de transcrição do YouTube: {url}")
    try:
        # Tenta carregar a transcrição do URL do YouTube.
        # `add_video_info=True`: Adiciona metadados do vídeo.
        # `language`: Prioriza a busca por transcrições em português, inglês e espanhol.
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=True, language=["pt", "en", "es", "pt-BR"]
        )
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Transcrição do YouTube carregada com sucesso para a URL: {url}")
        return content.strip(), None
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        # Captura erros quando o vídeo não tem transcrições.
        error_message = "Não consegui encontrar transcrições para este vídeo. Verifique se as legendas estão ativadas."
        logging.error(f"Erro de transcrição do YouTube. Erro: {e}", exc_info=True)
        return None, error_message
    except (
        pytubefix.exceptions.VideoUnavailable,
        urllib.error.HTTPError,
        pytubefix.exceptions.AgeRestrictedError,
        pytubefix.exceptions.LiveStreamError,
        pytubefix.exceptions.VideoPrivateError,
        pytubefix.exceptions.VideoRegionBlockedError,
    ) as e:
        # Captura erros relacionados a restrições do vídeo ou falhas de requisição.
        error_message = f"O vídeo não está disponível ou a requisição foi bloqueada. Verifique o link e tente novamente mais tarde."
        logging.error(f"Erro de acesso ao vídeo do YouTube. Erro: {e}", exc_info=True)
        return None, error_message
    except Exception as e:
        # Captura qualquer outro erro inesperado.
        logging.error(
            f"Falha ao carregar transcrição do YouTube. Erro: {e}", exc_info=True
        )
        error_message = f"Não consegui processar o vídeo deste link: {url}. Por favor, tente com outro link."
        return None, error_message


def get_content_from_pdf(file_path: str):
    """
    Carrega o conteúdo de um arquivo PDF local usando PyPDFLoader.

    Args:
        file_path (str): O caminho do arquivo PDF.

    Returns:
        tuple[str | None, str | None]: Uma tupla com o conteúdo e uma mensagem de erro (se houver).
    """
    logging.info(f"Iniciando carregamento do arquivo PDF: {file_path}")
    try:
        if not os.path.exists(file_path):
            error_message = f"Arquivo PDF não encontrado no caminho: {file_path}"
            logging.error(error_message)
            return None, error_message

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        content = " ".join([doc.page_content for doc in docs])
        logging.info(
            f"Conteúdo do PDF carregado com sucesso para o caminho: {file_path}"
        )

        return content.strip(), None
    except Exception as e:
        logging.error(f"Falha ao carregar o arquivo PDF. Erro: {e}", exc_info=True)
        error_message = f"Não consegui ler o arquivo PDF em: {file_path}. O arquivo pode estar corrompido ou com formato inválido."
        return None, error_message


def get_content_from_url(url: str):
    """
    Carrega o conteúdo de uma página web padrão usando WebBaseLoader.

    Args:
        url (str): O URL da página da web.

    Returns:
        tuple[str | None, str | None]: Uma tupla com o conteúdo e uma mensagem de erro (se houver).
    """
    logging.info(f"Iniciando carregamento de conteúdo da URL padrão: {url}")
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
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
    Classe para criar um componente de mensagem na interface do chat.
    Cada mensagem exibe um avatar, o nome do usuário e o texto da mensagem.
    """

    def __init__(self, message: str, user_name: str, message_type: str):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            (
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(user_name)),
                    bgcolor=ft.Colors.BLUE_GREY_200,
                )
                if message_type == "user"
                else ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.SMART_TOY_OUTLINED),
                    bgcolor=ft.Colors.GREEN_200,
                )
            ),
            ft.Column(
                [
                    ft.Text(user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message, selectable=True, width=500, data=message),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        """
        Método para obter as duas primeiras letras do nome do usuário para o avatar.

        Args:
            user_name (str): O nome do usuário.

        Returns:
            str: As duas primeiras letras em maiúsculo ou 'U' se o nome for vazio.
        """
        return user_name[:2].upper() if user_name else "U"


# -------------------
# 5. CLASSE PRINCIPAL DA APLICAÇÃO (FLET)
# -------------------
class MainChatApp:
    def __init__(self, page: ft.Page):
        """
        Construtor da classe principal da aplicação.
        Inicializa todos os componentes da interface e o estado da aplicação.

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
        """Configura as propriedades iniciais da página."""
        self.page.title = "Chat com Seu Blusa"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.theme_mode = ft.ThemeMode.LIGHT

    def _create_controls(self):
        """Cria todos os componentes da interface (controles)."""
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
        self.page.overlay.append(self.file_picker)

        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            tooltip="Enviar mensagem",
            on_click=self.send_message,
        )
        self.pdf_upload_button = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Enviar arquivo PDF",
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["pdf"],
                allow_multiple=False,
            ),
        )
        self.restart_button = ft.ElevatedButton(
            "Reiniciar Chat", on_click=self.restart_chat, icon=ft.Icons.REFRESH
        )
        self.exit_button = ft.ElevatedButton(
            "Sair", on_click=self.end_chat, icon=ft.Icons.EXIT_TO_APP
        )

    def _add_controls_to_page(self):
        """Adiciona os controles à página na ordem correta."""
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
            ft.Row([self.new_message, self.pdf_upload_button, self.send_button]),
        )
        self.new_message.on_submit = self.send_message

    def _setup_initial_state(self):
        """Configura as variáveis de sessão e estado inicial."""
        self.page.session.set("onboarding_state", "awaiting_name")
        self.page.session.set("history", [])

    def send_message(self, e):
        """
        Função de callback para o botão de envio e o evento de submissão do campo de texto.
        Gerencia o fluxo de onboarding e a interação do chat.

        Args:
            e: Objeto do evento.
        """
        user_message_text = self.new_message.value
        if not user_message_text.strip():
            self.page.update()
            return

        self.new_message.value = ""
        self.page.update()
        logging.info(f"Mensagem recebida do usuário: '{user_message_text}'")

        current_state = self.page.session.get("onboarding_state")

        # Lógica centralizada para o fluxo de onboarding.
        if current_state == "awaiting_name":
            self.handle_awaiting_name(user_message_text)
        elif current_state == "awaiting_confirmation":
            self.handle_awaiting_confirmation(user_message_text)
        elif current_state == "onboarding_complete":
            self.handle_chat_message(user_message_text)

        self.page.update()
        self.new_message.focus()

    def handle_awaiting_name(self, user_message_text: str):
        """Gerencia o estado 'awaiting_name'."""
        self.chat_list.controls.append(
            ChatMessage(
                message=user_message_text, user_name="Usuário", message_type="user"
            )
        )
        self.page.session.set("pending_name", user_message_text)
        bot_response_text = (
            f"Entendido, você gostaria de usar o nome '{user_message_text}'? (Sim/Não)"
        )
        self.page.session.set("onboarding_state", "awaiting_confirmation")
        self.chat_list.controls.append(
            ChatMessage(
                message=bot_response_text,
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )

    def handle_awaiting_confirmation(self, user_message_text: str):
        """Gerencia o estado 'awaiting_confirmation'."""
        self.chat_list.controls.append(
            ChatMessage(
                message=user_message_text, user_name="Usuário", message_type="user"
            )
        )
        affirmative_responses = ["sim", "s", "ok", "claro", "yes"]
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
            ChatMessage(
                message=bot_response_text,
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )

    def handle_chat_message(self, user_message_text: str):
        """Gerencia o estado 'onboarding_complete' e a lógica do chat principal."""
        user_name = self.page.session.get("user_name") or "Usuário"
        self.chat_list.controls.append(
            ChatMessage(
                message=user_message_text, user_name=user_name, message_type="user"
            )
        )
        thinking_indicator = ChatMessage(
            message="analisando...", user_name="Seu Blusa", message_type="assistant"
        )
        self.chat_list.controls.append(thinking_indicator)
        self.page.update()

        history = self.page.session.get("history")
        url = find_url(user_message_text)
        is_pdf = is_pdf_file_path(user_message_text)
        content, error_message = None, None

        if url:
            clean_url = url.split("&t=")[0] if "&t=" in url else url
            content, error_message = (
                get_content_from_youtube(clean_url)
                if is_youtube_url(url)
                else get_content_from_url(url)
            )
        elif is_pdf:
            pdf_path = user_message_text
            content, error_message = get_content_from_pdf(pdf_path)
        else:
            history.append(("user", user_message_text))
            template = ChatPromptTemplate.from_messages(system_prompt + history)
            chain = template | chat
            bot_response_text = chain.invoke({}).content

        if content:
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
            bot_response_text = chain.invoke({}).content
        elif error_message:
            bot_response_text = error_message
        else:
            bot_response_text = "Desculpe, não consegui processar a sua solicitação. Poderia tentar novamente?"

        self.chat_list.controls.pop()
        self.chat_list.controls.append(
            ChatMessage(
                message=bot_response_text,
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )

        history.append(("user", user_message_text))
        history.append(("assistant", bot_response_text))
        self.page.session.set("history", history)

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        """
        Função de callback chamada quando um arquivo é selecionado via FilePicker.
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
        Função para finalizar o chat e em seguida reiniciá-lo.
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
        logging.info(
            f"Chat finalizado. Mensagem de despedida enviada para '{user_name}'."
        )

        time.sleep(2)
        self.restart_chat(e)


def main(page: ft.Page):
    MainChatApp(page)


# -------------------
# 6. INICIALIZAÇÃO DA APLICAÇÃO
# -------------------
ft.app(target=main, view=ft.WEB_BROWSER)
