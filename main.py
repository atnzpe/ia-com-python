# -*- coding: utf-8 -*-

# -------------------
# 1. IMPORTAÇÕES
# -------------------
import flet as ft  # Importa a biblioteca Flet para a interface gráfica.
import os  # Usado para acessar variáveis de ambiente.
import logging  # Para registrar eventos da aplicação.
import re  # [ADICIONADO] Importa a biblioteca de expressões regulares para detectar URLs.

from dotenv import load_dotenv  # Importa a função para carregar o arquivo .env.
from langchain_groq import ChatGroq  # Cliente para a API da Groq.
from langchain.prompts import ChatPromptTemplate  # Para criar templates de prompt.
from langchain_community.document_loaders import (
    WebBaseLoader,
)  # Para carregar conteúdo de páginas web.

# Carrega as variáveis de ambiente do arquivo .env no início do script.
load_dotenv()
logging.info("Arquivo .env carregado.")

# -------------------
# 2. CONFIGURAÇÃO DE LOGS
# -------------------
# Configura o logging para salvar eventos em um arquivo, facilitando a depuração.
logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# -------------------
# 3. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (BOT)
# -------------------
logging.info("Configurando o cliente da API Groq...")

# Carrega a chave da API de forma segura do ambiente.
api_key = os.getenv("GROQ_API_KEY")

# Validação da existência da chave da API.
if not api_key:
    # Se a chave não for encontrada, loga um erro crítico e encerra a aplicação.
    logging.error("A variável de ambiente GROQ_API_KEY não foi encontrada!")
    print(
        "ERRO: A chave da API da Groq não foi encontrada. Crie um arquivo .env e defina a variável 'GROQ_API_KEY'."
    )
    exit()  # Encerra o script.
else:
    # Log de sucesso se a chave for encontrada.
    logging.info("Chave da API Groq carregada com sucesso do ambiente.")

# Inicializa o cliente do chat com o modelo e a chave da API.
chat = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=api_key)

# Define a instrução de sistema (personalidade) do bot.
system_prompt = [
    (
        "system",
        "Você é um assistente prestativo e amigável chamado Seu Blusa. Responda sempre em português do Brasil.",
    )
]
logging.info("Cliente do chat e prompt de sistema inicializados.")

# [REMOVIDO] O código de teste do loader que estava solto no escopo global foi removido.
# A lógica agora está encapsulada em uma função.


# -------------------
# 4. FUNÇÕES AUXILIARES [SEÇÃO ADICIONADA]
# -------------------


def find_url(text: str):
    """
    Encontra a primeira URL em uma string de texto usando expressões regulares.

    Args:
        text (str): O texto a ser verificado.

    Returns:
        str | None: A primeira URL encontrada ou None se nenhuma for encontrada.
    """
    # Expressão regular para encontrar URLs que começam com http:// ou https://.
    url_pattern = r"https?://\S+"
    # re.search() procura pelo padrão na string.
    match = re.search(url_pattern, text)
    # Se encontrar uma correspondência, retorna a string correspondente (a URL).
    if match:
        logging.info(f"URL encontrada no texto: {match.group(0)}")
        return match.group(0)
    # Se não, retorna None.
    return None


def get_content_from_url(url: str):
    """
    Carrega e retorna o conteúdo de texto de uma URL usando WebBaseLoader.

    Args:
        url (str): A URL da página a ser lida.

    Returns:
        str | None: O conteúdo de texto da página ou None em caso de erro.
    """
    logging.info(f"Iniciando carregamento de conteúdo da URL: {url}")
    try:
        # Cria uma instância do WebBaseLoader com a URL.
        loader = WebBaseLoader(url)
        # O método .load() busca o conteúdo da página.
        docs = loader.load()
        # Concatena o page_content de todos os documentos retornados.
        content = " ".join([doc.page_content for doc in docs])
        logging.info(f"Conteúdo da URL {url} carregado com sucesso.")
        # Retorna o conteúdo, removendo espaços em branco extras.
        return content.strip()
    except Exception as e:
        # Em caso de qualquer erro (URL inválida, timeout, etc.), loga o erro.
        logging.error(
            f"Falha ao carregar conteúdo da URL {url}. Erro: {e}", exc_info=True
        )
        # Retorna None para indicar que a operação falhou.
        return None


# -------------------
# 5. COMPONENTE DE MENSAGEM DA INTERFACE (FLET)
# -------------------
# (Esta seção permanece inalterada)
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
    # Configurações da página (título, alinhamento, tema).
    page.title = "Chat com Seu Blusa"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme_mode = ft.ThemeMode.LIGHT

    # Limpa a sessão ao iniciar para garantir um estado limpo.
    page.session.clear()

    def on_connect(e):
        # Função executada quando um novo usuário se conecta.
        logging.info(f"Novo usuário conectado: {page.session_id}")
        # Adiciona a mensagem de boas-vindas inicial.
        chat_list.controls.append(
            ChatMessage(
                message="Olá! Eu sou o Seu Blusa. Você pode me fazer uma pergunta ou me enviar um link para eu ler.",
                user_name="Seu Blusa",
                message_type="assistant",
            )
        )
        page.update()

    # Define a função on_connect para ser chamada na conexão.
    page.on_connect = on_connect

    # Cria a lista visual para as mensagens do chat.
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Cria o campo de texto para entrada do usuário.
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
        # Função principal que processa o clique no botão de enviar.

        # Pega o texto da mensagem do usuário.
        user_message_text = new_message.value
        # Se a mensagem estiver vazia, não faz nada.
        if not user_message_text.strip():
            page.update()
            return

        # Limpa o campo de texto após o envio.
        new_message.value = ""
        logging.info(f"Mensagem recebida do usuário: '{user_message_text}'")

        # Recupera o nome do usuário da sessão.
        user_name = page.session.get("user_name")

        # Lógica para o primeiro contato do usuário (definir o nome).
        if user_name is None:
            user_name = user_message_text
            page.session.set("user_name", user_name)
            page.session.set("history", [])  # Inicia o histórico da conversa.
            logging.info(f"Nome do usuário definido como: '{user_name}'")

            # Exibe a mensagem do usuário (o nome dele) na tela.
            chat_list.controls.append(
                ChatMessage(message=user_name, user_name=user_name, message_type="user")
            )

            # Envia a mensagem de boas-vindas.
            welcome_message = f"Prazer em conhecê-lo, {user_name}! Qual a sua dúvida?"
            logging.info(f"Enviando mensagem de boas-vindas para {user_name}.")
            chat_list.controls.append(
                ChatMessage(
                    message=welcome_message,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )
        else:
            # Lógica para conversas normais (após o nome ser definido).
            # Exibe a mensagem do usuário na tela.
            chat_list.controls.append(
                ChatMessage(
                    message=user_message_text, user_name=user_name, message_type="user"
                )
            )
            # Mostra o indicador "pensando..." para o usuário.
            thinking_indicator = ChatMessage(
                message="pensando...", user_name="Seu Blusa", message_type="assistant"
            )
            chat_list.controls.append(thinking_indicator)
            page.update()

            # Recupera o histórico da conversa.
            history = page.session.get("history")
            # Adiciona a pergunta atual do usuário ao histórico.
            history.append(("user", user_message_text))

            # [LÓGICA ALTERADA] Verifica se a mensagem contém uma URL.
            url = find_url(user_message_text)

            if url:
                # Se encontrou uma URL, tenta carregar seu conteúdo.
                logging.info(f"Iniciando processamento de URL: {url}")
                web_content = get_content_from_url(url)

                if web_content:
                    # Se o conteúdo foi carregado com sucesso, cria um prompt especial.
                    prompt_text = f"""Com base no seguinte conteúdo extraído da página web '{url}':
                    --- CONTEÚDO DA PÁGINA ---
                    {web_content[:4000]} 
                    --- FIM DO CONTEÚDO ---
                    Responda à pergunta do usuário de forma concisa: '{user_message_text}'"""
                    logging.info("Criando prompt com contexto da web.")
                    # O prompt para o LLM será apenas a instrução, não o histórico inteiro.
                    prompt_completo = [("user", prompt_text)]
                else:
                    # Se falhou ao carregar, informa o usuário.
                    logging.warning(
                        f"Não foi possível carregar o conteúdo da URL: {url}"
                    )
                    prompt_completo = [
                        (
                            "user",
                            f"Não consegui acessar o conteúdo do link {url}. Poderia verificar se o link está correto?",
                        )
                    ]

            else:
                # Se não há URL, a conversa é normal e usa o histórico.
                logging.info("Nenhuma URL detectada. Prosseguindo com conversa normal.")
                prompt_completo = system_prompt + history

            # Cria o template e a cadeia de execução.
            template = ChatPromptTemplate.from_messages(prompt_completo)
            chain = template | chat

            # Invoca o modelo de linguagem para gerar a resposta.
            logging.info("Invocando o modelo de linguagem para gerar resposta...")
            bot_response_text = chain.invoke({}).content
            logging.info(f"Resposta recebida do modelo: '{bot_response_text}'")

            # Adiciona a resposta do bot ao histórico para manter o contexto.
            history.append(("assistant", bot_response_text))
            page.session.set("history", history)

            # Remove o indicador "pensando...".
            chat_list.controls.pop()
            # Adiciona a mensagem final do bot à tela.
            chat_list.controls.append(
                ChatMessage(
                    message=bot_response_text,
                    user_name="Seu Blusa",
                    message_type="assistant",
                )
            )

        # Atualiza a interface gráfica.
        page.update()
        # Coloca o foco de volta no campo de texto.
        new_message.focus()

    # Associa a função de clique ao evento de submit (pressionar Enter) do campo de texto.
    new_message.on_submit = send_message_click

    # Adiciona os componentes visuais à página.
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
# Inicia a aplicação Flet.
# Para rodar como uma janela de desktop, use: ft.app(target=main)
ft.app(target=main, view=ft.WEB_BROWSER)
