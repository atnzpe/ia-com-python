# -*- coding: utf-8 -*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# (Nenhuma mudança nesta seção)
import flet as ft
import os
import logging
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()
logging.info("Arquivo .env carregado.")

# -------------------
# 2. CONFIGURAÇÃO DE LOGS
# -------------------
# (Nenhuma mudança nesta seção)
logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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
        logging.info(f"URL encontrada no texto: {match.group(0)}")
        return match.group(0)
    return None


def get_content_from_url(url: str):
    logging.info(f"Iniciando carregamento de conteúdo da URL: {url}")
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Conteúdo da URL {url} carregado com sucesso.")
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

    def on_connect(e):
        logging.info(f"Novo usuário conectado: {page.session_id}")
        chat_list.controls.append(
            ChatMessage(
                message="Olá! Eu sou o Seu Blusa. Para começarmos, qual o seu nome?",
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        page.update()

    page.on_connect = on_connect

    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

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

        # [LÓGICA REFORÇADA] Este bloco agora trata da primeira interação de forma
        # completamente isolada e termina a execução com um 'return'.
        if user_name is None:
            # 1. A primeira mensagem do usuário é tratada como o nome dele.
            user_name = user_message_text
            page.session.set("user_name", user_name)
            page.session.set("history", [])
            logging.info(f"Nome do usuário definido como: '{user_name}'")

            # 2. Exibe o nome que o usuário digitou como uma mensagem 'dele'.
            chat_list.controls.append(
                ChatMessage(message=user_name, user_name=user_name, message_type="user")
            )

            # 3. O bot envia a saudação personalizada.
            welcome_message = f"Prazer em conhecê-lo, {user_name}!"
            logging.info(f"Enviando saudação para {user_name}.")
            chat_list.controls.append(
                ChatMessage(
                    message=welcome_message,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )

            # 4. O bot envia a mensagem de acompanhamento para iniciar a conversa.
            prompt_question_message = "Agora, como posso te ajudar? Faça uma pergunta ou me envie um link para analisar."
            logging.info("Enviando convite para a primeira pergunta.")
            chat_list.controls.append(
                ChatMessage(
                    message=prompt_question_message,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )

            # 5. [GARANTIA] Atualiza a página e termina a função aqui.
            # O `return` impede que o código continue e entre na lógica de IA por engano.
            page.update()
            new_message.focus()
            return

        # --- INÍCIO DA LÓGICA DE CONVERSA NORMAL ---
        # Este código só será executado se 'user_name' JÁ EXISTIR.

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
            logging.info(f"Iniciando processamento de URL: {url}")
            web_content = get_content_from_url(url)
            if web_content:
                prompt_text = f"""Com base no seguinte conteúdo extraído da página web '{url}':
                --- CONTEÚDO DA PÁGINA ---
                {web_content[:4000]} 
                --- FIM DO CONTEÚDO ---
                Responda à pergunta do usuário de forma concisa: '{user_message_text}'"""
                logging.info("Criando prompt com contexto da web.")
                prompt_completo = [("user", prompt_text)]
            else:
                logging.warning(f"Não foi possível carregar o conteúdo da URL: {url}")
                prompt_completo = [
                    (
                        "user",
                        f"Não consegui acessar o conteúdo do link {url}. Poderia verificar se o link está correto?",
                    )
                ]
        else:
            logging.info("Nenhuma URL detectada. Prosseguindo com conversa normal.")
            prompt_completo = system_prompt + history

        template = ChatPromptTemplate.from_messages(prompt_completo)
        chain = template | chat

        logging.info("Invocando o modelo de linguagem para gerar resposta...")
        bot_response_text = chain.invoke({}).content
        logging.info(f"Resposta recebida do modelo: '{bot_response_text}'")

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
