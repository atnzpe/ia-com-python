# -*main.py 12:51 19/08/2025*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
import flet as ft
import os
import logging
import re
import sys
from pypdf import PdfReader

logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
logging.info("Arquivo .env carregado.")

# -------------------
# 2. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (BOT)
# -------------------

chat = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))
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
    url_pattern = r"https?://\S+"
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    return None


def is_youtube_url(url: str):
    youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)"
    is_match = re.search(youtube_pattern, url)
    if is_match:
        return True
    return False


def is_pdf_file_path(text: str):
    """
    Verifica se a string é um caminho de arquivo que termina com .pdf.
    """
    return text.lower().endswith(".pdf")


def get_content_from_youtube(url: str):
    """
    Carrega a transcrição de um vídeo do YouTube.
    Retorna uma tupla (conteúdo, None) em caso de sucesso,
    ou (None, mensagem_de_erro) em caso de falha.
    """
    logging.info(f"Iniciando carregamento de transcrição do YouTube: {url}")
    try:
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=True, language=["pt", "en", "es", "pt-BR"]
        )
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Transcrição do YouTube carregada com sucesso para a URL: {url}")
        return content.strip(), None
    except Exception as e:
        logging.error(
            f"Falha ao carregar transcrição do YouTube. Erro: {e}", exc_info=True
        )
        error_message = f"Não consegui processar o vídeo do YouTube deste link: {url}. O vídeo pode ser privado, ter restrição de idade ou estar indisponível. Por favor, tente com outro link."
        return None, error_message


def get_content_from_url(url: str):
    """
    Carrega o conteúdo de uma página web padrão.
    Retorna uma tupla (conteúdo, None) em caso de sucesso,
    ou (None, mensagem_de_erro) em caso de falha.
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


def get_content_from_pdf(file_path: str):
    """
    Carrega o conteúdo de um arquivo PDF local.
    Retorna uma tupla (conteúdo, None) em caso de sucesso,
    ou (None, mensagem_de_erro) em caso de falha.
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


# -------------------
# 4. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
# -------------------
class ChatMessage(ft.Row):
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
        return user_name[:2].upper() if user_name else "U"


# -------------------
# 5. FUNÇÃO PRINCIPAL DA APLICAÇÃO (FLET)
# -------------------
def main(page: ft.Page):
    page.title = "Chat com Seu Blusa"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.LIGHT
    page.session.clear()

    # [ADICIONADO] Cria a variável para o FilePicker
    file_picker = ft.FilePicker(
        on_result=lambda e: on_dialog_result(e, page, new_message, chat_list)
    )
    page.overlay.append(file_picker)

    chat_list = ft.ListView(
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
    logging.info("Interface do chat inicializada com a mensagem de boas-vindas.")

    new_message = ft.TextField(
        hint_text="Digite seu nome ou sua mensagem...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
    )

    def send_message_click(e):
        user_message_text = new_message.value
        if not user_message_text.strip():
            page.update()
            return

        new_message.value = ""
        logging.info(f"Mensagem recebida do usuário: '{user_message_text}'")
        user_name = page.session.get("user_name")

        if user_name is None:
            user_name = user_message_text
            page.session.set("user_name", user_name)
            page.session.set("history", [])
            chat_list.controls.append(
                ChatMessage(message=user_name, user_name=user_name, message_type="user")
            )
            chat_list.controls.append(
                ChatMessage(
                    message=f"Prazer em conhecê-lo, {user_name}!",
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )
            chat_list.controls.append(
                ChatMessage(
                    message="Agora, como posso te ajudar? Faça uma pergunta ou me envie um link para analisar.",
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )
            page.update()
            new_message.focus()
            return

        chat_list.controls.append(
            ChatMessage(
                message=user_message_text, user_name=user_name, message_type="user"
            )
        )
        thinking_indicator = ChatMessage(
            message="analisando...", user_name="Seu Blusa", message_type="assistant"
        )
        chat_list.controls.append(thinking_indicator)
        page.update()

        history = page.session.get("history")

        url = find_url(user_message_text)
        is_pdf = is_pdf_file_path(user_message_text)
        content, error_message = None, None

        if url:
            content, error_message = (
                get_content_from_youtube(url)
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

        history.append(("user", user_message_text))
        history.append(("assistant", bot_response_text))
        page.session.set("history", history)
        chat_list.controls.pop()
        chat_list.controls.append(
            ChatMessage(
                message=bot_response_text,
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        page.update()
        new_message.focus()

    # [ADICIONADO] Função para lidar com o resultado do FilePicker
    def on_dialog_result(
        e: ft.FilePickerResultEvent,
        page: ft.Page,
        new_message: ft.TextField,
        chat_list: ft.ListView,
    ):
        """
        Função de callback chamada quando um arquivo é selecionado.
        Ela processa o caminho do arquivo e o envia para a função de processamento de PDF.
        """
        logging.info("Evento do FilePicker acionado.")
        if e.files is not None and len(e.files) > 0:
            file_path = e.files[0].path
            logging.info(f"Arquivo selecionado: {file_path}")

            # Envia o caminho do arquivo para a lógica de processamento
            new_message.value = file_path
            send_message_click(e)

    # [ADICIONADO] Função para limpar o chat e recomeçar
    def restart_chat(e, page, new_message, chat_list, send_button):
        page.session.clear()
        chat_list.controls.clear()
        chat_list.controls.append(
            ChatMessage(
                message="Olá! Eu sou o Seu Blusa. Para começarmos, qual o seu nome?",
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        new_message.value = ""
        new_message.hint_text = "Digite seu nome ou sua mensagem..."
        new_message.disabled = False
        send_button.disabled = False
        page.update()
        logging.info("Chat reiniciado.")

    # [ALTERADO] Função para finalizar e reiniciar o chat
    def end_chat(e, page, new_message, chat_list, send_button):
        user_name = page.session.get("user_name") or "usuário"
        final_message = f"Até mais, {user_name}!"

        chat_list.controls.append(
            ChatMessage(
                message=final_message, user_name="Seu Blusa", message_type="assistant"
            )
        )
        new_message.disabled = True
        send_button.disabled = True
        page.update()
        logging.info(
            f"Chat finalizado. Mensagem de despedida enviada para '{user_name}'."
        )

        # Chama a função de reinício após 2 segundos
        page.update()
        time.sleep(2)
        restart_chat(e, page, new_message, chat_list, send_button)

    # [ADICIONADO] Criação dos botões de ação
    restart_button = ft.ElevatedButton(
        "Reiniciar Chat",
        on_click=lambda e: restart_chat(e, page, new_message, chat_list, send_button),
        icon=ft.Icons.REFRESH,
    )
    exit_button = ft.ElevatedButton(
        "Sair",
        on_click=lambda e: end_chat(e, page, new_message, chat_list, send_button),
        icon=ft.Icons.EXIT_TO_APP,
    )
    send_button = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        tooltip="Enviar mensagem",
        on_click=send_message_click,
    )

    # [ADICIONADO] Botão de upload de PDF
    pdf_upload_button = ft.IconButton(
        icon=ft.Icons.UPLOAD_FILE,
        tooltip="Enviar arquivo PDF",
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["pdf"],
            allow_multiple=False,
        ),
    )

    # [ADICIONADO] Organiza os botões de controle em uma linha
    control_buttons = ft.Row(
        [
            restart_button,
            exit_button,
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    page.add(
        control_buttons,
        ft.Container(
            content=chat_list,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                pdf_upload_button,
                send_button,
            ]
        ),
    )

    # [LÓGICA ALTERADA] Vincula a função send_message_click ao evento on_submit do new_message
    new_message.on_submit = send_message_click


# -------------------
# 6. INICIALIZAÇÃO DA APLICAÇÃO
# -------------------
ft.app(target=main, view=ft.WEB_BROWSER)
