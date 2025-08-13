# -*- coding: utf-8 -*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# (Nenhuma mudança nesta seção)
import flet as ft
import os
import logging
import re

# -------------------
# 2. CONFIGURAÇÃO DE LOGS
# -------------------
# (Nenhuma mudança nesta seção)
logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Carrega as variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader


load_dotenv()
logging.info("Arquivo .env carregado.")



# -------------------
# 3. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (BOT)
# -------------------
# (Nenhuma mudança nesta seção)
logging.info("Configurando o cliente da API Groq...")
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logging.error("A variável de ambiente GROQ_API_KEY não foi encontrada!")
    print(
        "ERRO: A chave da API da Groq não foi encontrada. Crie um arquivo .env e defina a variável 'GROQ_API_KEY'."
    )
    exit()
else:
    logging.info("Chave da API Groq carregada com sucesso do ambiente.")

chat = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)
system_prompt = [
    (
        "system",
        "Você é um assistente prestativo e amigável chamado Seu Blusa. Responda sempre em português do Brasil.",
    )
]
logging.info("Cliente do chat e prompt de sistema inicializados.")


# -------------------
# 4. FUNÇÕES AUXILIARES
# -------------------
# (Nenhuma mudança nesta seção)
def find_url(text: str):
    url_pattern = r"https?://\S+"
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    return None


def is_youtube_url(url: str):
    """
    Verifica se uma URL pertence ao YouTube.

    Args:
        url (str): A URL a ser verificada.

    Returns:
        bool: True se for uma URL do YouTube, False caso contrário.
    """
    # Padrão para identificar domínios do YouTube (youtube.com e youtu.be).
    youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([\w-]{11})"
    # re.match verifica se o padrão corresponde ao início da string.
    is_match = re.search(youtube_pattern, url)
    if is_match:
        logging.info(f"URL identificada como link do YouTube: {url}")
        return True
    return False


# [ADICIONADO] Nova função para extrair conteúdo de vídeos do YouTube.
def get_content_from_youtube(url: str):
    """
    Carrega a transcrição de um vídeo do YouTube usando YoutubeLoader.

    Args:
        url (str): A URL do vídeo do YouTube.

    Returns:
        str | None: A transcrição do vídeo ou None em caso de erro.
    """
    logging.info(f"Iniciando carregamento de transcrição do YouTube: {url}")
    try:
        # Cria uma instância do YoutubeLoader a partir da URL.
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=True, language=["pt", "en"]
        )
        # Carrega a transcrição.
        docs = loader.load()
        # Concatena o conteúdo.
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Transcrição do YouTube carregada com sucesso para a URL: {url}")
        return content.strip()
    except Exception as e:
        # Em caso de erro (vídeo sem legenda, URL inválida), loga e retorna None.
        logging.error(
            f"Falha ao carregar transcrição do YouTube. Erro: {e}", exc_info=True
        )
        return None


def get_content_from_url(url: str):
    logging.info(f"Iniciando carregamento de conteúdo da URL: {url}")
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        return content.strip()
    except Exception as e:
        logging.error(
            f"Falha ao carregar conteúdo da URL {url}. Erro: {e}", exc_info=True
        )
        return None


# -------------------
# 5. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
# -------------------
# (Nenhuma mudança nesta seção)
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
# 6. FUNÇÃO PRINCIPAL DA APLICAÇÃO (FLET)
# -------------------
def main(page: ft.Page):
    page.title = "Chat com Seu Blusa"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.LIGHT

    page.session.clear()

    # [REMOVIDO] A função 'on_connect' foi removida, pois não é a forma
    # mais confiável de garantir a exibição da mensagem inicial.

    # [LÓGICA ALTERADA] A mensagem de boas-vindas agora é adicionada DIRETAMENTE
    # na criação do componente 'chat_list'. Isso garante que ela exista
    # desde o primeiro momento em que a página é renderizada.
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

    # Log para registrar que a UI foi inicializada com a mensagem de boas-vindas.
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

        # [LÓGICA MANTIDA] O fluxo de boas-vindas agora funcionará corretamente,
        # pois o usuário verá a pergunta inicial e saberá que deve digitar o nome.
        if user_name is None:
            user_name = user_message_text
            page.session.set("user_name", user_name)
            page.session.set("history", [])
            logging.info(f"Nome do usuário definido como: '{user_name}'")

            chat_list.controls.append(
                ChatMessage(message=user_name, user_name=user_name, message_type="user")
            )

            welcome_message = f"Prazer em conhecê-lo, {user_name}!"
            logging.info(f"Enviando saudação para {user_name}.")
            chat_list.controls.append(
                ChatMessage(
                    message=welcome_message,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )

            prompt_question_message = "Agora, como posso te ajudar? Faça uma pergunta ou me envie um link para analisar."
            logging.info("Enviando convite para a primeira pergunta.")
            chat_list.controls.append(
                ChatMessage(
                    message=prompt_question_message,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )

            page.update()
            new_message.focus()
            return

        # Lógica de conversa normal (inalterada)
        chat_list.controls.append(
            ChatMessage(
                message=user_message_text, user_name=user_name, message_type="user"
            )
        )
        thinking_indicator = ChatMessage(
            message="pensando...", user_name="Seu Blusa", message_type="assistant"
        )
        chat_list.controls.append(thinking_indicator)
        page.update()

        history = page.session.get("history")
        history.append(("user", user_message_text))

        url = find_url(user_message_text)
        if url:
            # Verifica se a URL encontrada é do YouTube.
            if is_youtube_url(url):
                # Se for, usa o loader de YouTube.
                logging.info(f"Processando URL do YouTube: {url}")
                content = get_content_from_youtube(url)
                # Define o tipo de conteúdo para o prompt.
                content_type_for_prompt = "da transcrição do vídeo do YouTube"
            else:
                # Se não, usa o loader de página web padrão.
                logging.info(f"Processando URL de página web: {url}")
                content = get_content_from_url(url)
                # Define o tipo de conteúdo para o prompt.
                content_type_for_prompt = "da página web"

            # Após carregar o conteúdo, monta o prompt adequado.
            if content:
                prompt_text = f"""Com base no seguinte conteúdo extraído {content_type_for_prompt} '{url}':
                --- CONTEÚDO ---
                {content[:4000]} 
                --- FIM DO CONTEÚDO ---
                Responda à pergunta do usuário de forma concisa: '{user_message_text}'"""
                logging.info(
                    f"Criando prompt com contexto de {content_type_for_prompt}."
                )
                prompt_completo = [("user", prompt_text)]
            else:
                # Mensagem de erro se não conseguiu carregar o conteúdo.
                logging.warning(f"Não foi possível carregar o conteúdo do link: {url}")
                prompt_completo = [
                    (
                        "user",
                        f"Não consegui acessar o conteúdo do link {url}. Poderia verificar se o link está correto ou se o vídeo possui legendas?",
                    )
                ]
        else:
            # Se nenhuma URL for encontrada, segue a conversa normal.
            logging.info("Nenhuma URL detectada. Prosseguindo com conversa normal.")
            prompt_completo = system_prompt + history

        template = ChatPromptTemplate.from_messages(prompt_completo)
        chain = template | chat
        bot_response_text = chain.invoke({}).content

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

    new_message.on_submit = send_message_click

    page.add(
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
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    tooltip="Enviar mensagem",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


# -------------------
# 7. INICIALIZAÇÃO DA APLICAÇÃO
# -------------------
ft.app(target=main, view=ft.WEB_BROWSER)
