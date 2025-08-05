# -*- coding: utf-8 -*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
import flet as ft
import os
import logging
# ADICIONADO: Importa a função para carregar o arquivo .env
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# ADICIONADO: Carrega as variáveis de ambiente do arquivo .env
# Esta função deve ser chamada no início do script.
load_dotenv()

# -------------------
# 2. CONFIGURAÇÃO DE LOGS
# -------------------
logging.basicConfig(
    filename='chat_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------
# 3. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (BOT)
# -------------------
logging.info("Configurando o cliente da API Groq...")

# ALTERADO: Lógica para carregar a chave da API de forma segura do ambiente.
# A função os.getenv() busca a variável de ambiente 'GROQ_API_KEY' que foi carregada pelo load_dotenv().
api_key = os.getenv("GROQ_API_KEY")

# Verifica se a chave da API foi realmente encontrada no ambiente.
if not api_key:
    # Se a chave não for encontrada, loga um erro e encerra a aplicação.
    logging.error("A variável de ambiente GROQ_API_KEY não foi encontrada!")
    print("ERRO: A chave da API da Groq não foi encontrada. Crie um arquivo .env e defina a variável 'GROQ_API_KEY'.")
    exit()  # Encerra o script.
else:
    logging.info("Chave da API Groq carregada com sucesso do ambiente.")


# Inicializa o cliente do chat com o modelo e a chave da API carregada.
chat = ChatGroq(model='llama-3.3-70b-versatile', groq_api_key=api_key)

# Define a instrução de sistema (personalidade) do bot.
system_prompt = [
    ("system", "Você é um assistente prestativo e amigável chamado Seu Blusa. Responda sempre em português do Brasil.")
]
logging.info("Cliente do chat e prompt de sistema inicializados.")


# -------------------
# 4. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
# -------------------
# (Esta seção permanece inalterada)
class ChatMessage(ft.Row):
    def __init__(self, message: str, user_name: str, message_type: str):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(user_name)),
                bgcolor=ft.Colors.BLUE_GREY_200,
            ) if message_type == "user"
            else ft.CircleAvatar(
                content=ft.Icon(ft.Icons.SMART_TOY_OUTLINED),
                bgcolor=ft.Colors.GREEN_200,
            ),
            ft.Column(
                [
                    ft.Text(user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message, selectable=True, width=500),
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
# (Esta seção permanece inalterada, mas precisei corrigir a ordem de definição de `new_message`
# para garantir que o código funcione sem erros)
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
                message="Olá! Eu sou o Seu Blusa. Para começarmos, por favor, digite o seu nome abaixo.",
                user_name="Seu Blusa",
                message_type="assistant"
            )
        )
        page.update()

    page.on_connect = on_connect

    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A definição do campo de texto foi movida para ANTES da função que o utiliza
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
            logging.info(f"Nome do usuário definido como: '{user_name}'")

            chat_list.controls.append(ChatMessage(
                message=user_name, user_name=user_name, message_type="user"))

            welcome_message = f"Prazer em conhecê-lo, {user_name}! Qual a sua dúvida?"
            logging.info(f"Enviando mensagem de boas-vindas para {user_name}.")
            chat_list.controls.append(ChatMessage(
                message=welcome_message, user_name="Seu Blusa", message_type="assistant"))
        else:
            chat_list.controls.append(ChatMessage(
                message=user_message_text, user_name=user_name, message_type="user"))

            thinking_indicator = ChatMessage(
                message="pensando...", user_name="Seu Blusa", message_type="assistant")
            chat_list.controls.append(thinking_indicator)
            page.update()

            history = page.session.get("history")
            history.append(('user', user_message_text))

            prompt_completo = system_prompt + history
            template = ChatPromptTemplate.from_messages(prompt_completo)
            chain = template | chat

            logging.info("Invocando o modelo de linguagem para gerar resposta...")
            bot_response_text = chain.invoke({}).content
            logging.info(f"Resposta recebida do modelo: '{bot_response_text}'")

            history.append(('assistant', bot_response_text))
            page.session.set("history", history)

            chat_list.controls.pop()
            chat_list.controls.append(ChatMessage(
                message=bot_response_text, user_name="Seu Blusa", message_type="assistant"))

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
# Para rodar como uma janela de desktop, use: ft.app(target=main)
ft.app(target=main, view=ft.WEB_BROWSER)
