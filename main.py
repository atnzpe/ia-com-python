# -*- coding: utf-8 -*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# (Nenhuma mudança nesta seção)
import flet as ft
import os
import logging
import re

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

load_dotenv()
logging.info("Arquivo .env carregado.")

# -------------------
# 2. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (BOT)
# -------------------
# (Nenhuma mudança nesta seção)
# ... (código do bot inalterado) ...
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
# (Nenhuma mudança em find_url e is_youtube_url)
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


# [LÓGICA ALTERADA] A função agora retorna uma tupla: (conteúdo, mensagem_de_erro)
def get_content_from_youtube(url: str):
    """
    Carrega a transcrição de um vídeo do YouTube.
    Retorna uma tupla (conteúdo, None) em caso de sucesso,
    ou (None, mensagem_de_erro) em caso de falha.
    """
    logging.info(f"Iniciando carregamento de transcrição do YouTube: {url}")
    try:
        # [ADICIONADO] Implementando sua sugestão de especificar o idioma.
        # Isso é uma boa prática para priorizar legendas.
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=True, language=["pt", "en"]
        )
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Transcrição do YouTube carregada com sucesso para a URL: {url}")
        # Retorna o conteúdo e None para o erro.
        return content.strip(), None
    except Exception as e:
        # Em caso de erro, loga a exceção completa.
        logging.error(
            f"Falha ao carregar transcrição do YouTube. Erro: {e}", exc_info=True
        )
        # Monta uma mensagem de erro amigável e útil para o usuário.
        error_message = f"Não consegui processar o vídeo do YouTube deste link: {url}. O vídeo pode ser privado, ter restrição de idade ou estar indisponível. Por favor, tente com outro link."
        # Retorna None para o conteúdo e a mensagem de erro.
        return None, error_message


# [LÓGICA ALTERADA] A função agora retorna uma tupla: (conteúdo, mensagem_de_erro)
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
        # Retorna o conteúdo e None para o erro.
        return content.strip(), None
    except Exception as e:
        logging.error(
            f"Falha ao carregar conteúdo da URL padrão. Erro: {e}", exc_info=True
        )
        # Monta uma mensagem de erro amigável.
        error_message = f"Não consegui acessar a página neste link: {url}. Verifique se o link está correto e se o site está no ar."
        # Retorna None para o conteúdo e a mensagem de erro.
        return None, error_message


# -------------------
# 4. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
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
# 5. FUNÇÃO PRINCIPAL DA APLICAÇÃO (FLET)
# -------------------
def main(page: ft.Page):
    # (Nenhuma mudança nesta seção)
    page.title = "Chat com Seu Blusa"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.LIGHT
    page.session.clear()

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
            # ... (Lógica de onboarding inalterada) ...
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

        # [LÓGICA ALTERADA] O tratamento de erros agora é mais inteligente.
        url = find_url(user_message_text)
        if url:
            content, error_message = (
                get_content_from_youtube(url)
                if is_youtube_url(url)
                else get_content_from_url(url)
            )

            # Se o conteúdo foi carregado com sucesso...
            if content:
                content_type = (
                    "da transcrição do vídeo do YouTube"
                    if is_youtube_url(url)
                    else "da página web"
                )
                prompt_text = f"""Com base no seguinte conteúdo extraído {content_type} '{url}':
                --- CONTEÚDO ---
                {content[:4000]} 
                --- FIM DO CONTEÚDO ---
                Responda à pergunta do usuário de forma concisa: '{user_message_text}'"""
                # Envia o prompt com contexto para a IA.
                prompt_completo = [("user", prompt_text)]
                template = ChatPromptTemplate.from_messages(prompt_completo)
                chain = template | chat
                bot_response_text = chain.invoke({}).content
            # Se houve um erro ao carregar...
            else:
                # Usa a mensagem de erro específica retornada pela função de carregamento.
                bot_response_text = error_message

        # Se não for uma URL, segue a conversa normal...
        else:
            history.append(("user", user_message_text))
            template = ChatPromptTemplate.from_messages(system_prompt + history)
            chain = template | chat
            bot_response_text = chain.invoke({}).content

        # Atualiza a UI e o histórico.
        history.append(
            ("user", user_message_text)
        )  # Adiciona a pergunta original ao histórico
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
# 6. INICIALIZAÇÃO DA APLICAÇÃO
# -------------------
ft.app(target=main, view=ft.WEB_BROWSER)
