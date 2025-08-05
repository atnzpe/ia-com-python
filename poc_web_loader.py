# -*- coding: utf-8 -*-

"""
Prova de Conceito (PoC) para Acesso a Páginas Web.

Este script demonstra como usar o WebBaseLoader da biblioteca LangChain
para carregar o conteúdo de uma URL específica e exibi-lo no console.
Este é o primeiro passo para permitir que o chatbot "leia" sites.
"""

# 1. IMPORTAÇÕES
# =================
# Importando a biblioteca 'logging' para registrar o progresso e possíveis erros.
import logging

# Importando o WebBaseLoader, a ferramenta específica da LangChain para carregar conteúdo de URLs.
# Note que ela vem da 'langchain_community', que é um pacote com integrações mantidas pela comunidade.
from langchain_community.document_loaders import WebBaseLoader

# 2. CONFIGURAÇÃO DE LOGS
# =========================
# Configuração básica do logging para exibir mensagens no console.
# Define o nível para INFO, o que significa que todas as mensagens de 'info', 'warning', 'error', etc., serão mostradas.
# O formato inclui a data/hora, o nível e a mensagem do log.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# 3. FUNÇÃO PRINCIPAL DE EXECUÇÃO
# ===============================
def carregar_conteudo_web(url: str):
    """
    Carrega o conteúdo de uma URL usando WebBaseLoader e imprime um resumo.

    Args:
        url (str): A URL completa da página a ser carregada.
    """
    # Loga o início do processo, informando qual URL está sendo acessada.
    logging.info(f"Iniciando o carregamento do conteúdo da URL: {url}")

    try:
        # Cria uma instância do WebBaseLoader, passando a URL como alvo.
        # O loader é o objeto responsável por fazer a requisição HTTP e extrair o texto da página.
        loader = WebBaseLoader(url)

        # O método .load() executa o processo de carregamento.
        # Ele retorna uma lista de objetos 'Document'. Cada documento pode representar uma parte da página.
        lista_documentos = loader.load()
        logging.info(
            f"Conteúdo carregado com sucesso. Número de documentos extraídos: {len(lista_documentos)}"
        )

        # Variável para agregar o conteúdo de todos os documentos em um único texto.
        conteudo_completo = ""

        # Itera sobre a lista de documentos para extrair o texto de cada um.
        for doc in lista_documentos:
            # A propriedade 'page_content' de cada objeto 'Document' contém o texto extraído da página.
            conteudo_completo += doc.page_content

        # Verifica se algum conteúdo foi extraído.
        if conteudo_completo.strip():
            # Imprime os primeiros 800 caracteres do conteúdo para evitar poluir o console.
            logging.info("Impressão de um trecho do conteúdo extraído:")
            print("\n--- INÍCIO DO CONTEÚDO DA PÁGINA ---")
            print(conteudo_completo[:800] + "...")
            print("--- FIM DO TRECHO ---")
        else:
            logging.warning(
                "A página foi carregada, mas nenhum conteúdo de texto foi extraído."
            )

    except Exception as e:
        # Em caso de erro (ex: URL inválida, problema de conexão), loga a exceção.
        # Isso é crucial para a depuração. "Erros nunca devem passar silenciosamente." - Zen of Python.
        logging.error(f"Ocorreu um erro ao tentar carregar a URL: {e}", exc_info=True)
        print(
            f"\nERRO: Não foi possível carregar o conteúdo da página. Verifique a URL e sua conexão. Detalhes no log."
        )


# 4. PONTO DE ENTRADA DO SCRIPT
# ============================
# Este bloco garante que o código dentro dele só será executado quando o script
# for rodado diretamente (e não quando for importado por outro script).
if __name__ == "__main__":
    # Define a URL alvo para esta demonstração.
    url_asimov = "https://asimov.academy/"

    # Chama a função principal para executar a lógica de carregamento.
    carregar_conteudo_web(url_asimov)
