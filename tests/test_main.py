# test_main.py - Arquivo de testes para as funções auxiliares de main.py
# O objetivo é garantir que as funções de utilidade (identificação de URL, PDF, etc.)
# funcionem como esperado em diferentes cenários.

# -------------------
# 1. IMPORTAÇÕES
# -------------------
# Importa o framework de testes pytest.
import pytest

# Importa as funções a serem testadas do arquivo main.py.
from main import find_url, is_youtube_url, is_pdf_file_path

# -------------------
# 2. TESTES DA FUNÇÃO `find_url`
# -------------------

# Usa o decorator `pytest.mark.parametrize` para testar múltiplos casos com a mesma função.
# Argumentos: "text_input" (o texto a ser analisado), "expected_output" (o resultado esperado).
@pytest.mark.parametrize("text_input, expected_output", [
    # Caso 1: URL http simples.
    ("Visite http://example.com para mais informações.", "http://example.com"),
    # Caso 2: URL https no início do texto.
    ("https://www.google.com é um buscador.", "https://www.google.com"),
    # Caso 3: URL complexo com query parameters.
    ("Confira o vídeo em https://youtube.com/watch?v=dQw4w9WgXcQ", "https://youtube.com/watch?v=dQw4w9WgXcQ"),
    # Caso 4: Texto sem URL.
    ("Este é um texto simples sem links.", None),
    # Caso 5: URL no final do texto.
    ("O link é: https://flet.dev", "https://flet.dev"),
    # Caso 6: Texto vazio.
    ("", None),
])
def test_find_url(text_input, expected_output):
    """
    Testa a função `find_url` para verificar se ela extrai corretamente
    URLs de diferentes formatos de texto.
    """
    # A asserção verifica se o resultado da função é igual ao resultado esperado.
    assert find_url(text_input) == expected_output

# -------------------
# 3. TESTES DA FUNÇÃO `is_youtube_url`
# -------------------

@pytest.mark.parametrize("url_input, expected_output", [
    # Caso 1: URL padrão do YouTube.
    ("https://www.youtube.com/watch?v=video_id", True),
    # Caso 2: URL encurtado do YouTube.
    ("https://youtu.be/video_id", True),
    # Caso 3: URL sem "www".
    ("https://youtube.com/video_id", True),
    # Caso 4: URL com http.
    ("http://www.youtube.com", True),
    # Caso 5: URL de outro site.
    ("https://www.vimeo.com/12345", False),
    # Caso 6: Texto que não é um URL.
    ("apenas um texto normal", False),
    # Caso 7: URL com parâmetros adicionais.
    ("https://www.youtube.com/watch?v=some_id&t=15s", True),
])
def test_is_youtube_url(url_input, expected_output):
    """
    Testa a função `is_youtube_url` para verificar se ela identifica
    corretamente se um URL pertence ao YouTube.
    """
    # Verifica se a função retorna o booleano esperado.
    assert is_youtube_url(url_input) == expected_output

# -------------------
# 4. TESTES DA FUNÇÃO `is_pdf_file_path`
# -------------------

@pytest.mark.parametrize("path_input, expected_output", [
    # Caso 1: Caminho de arquivo PDF com extensão minúscula.
    ("C:\\Users\\doc\\documento.pdf", True),
    # Caso 2: Caminho de arquivo PDF com extensão maiúscula.
    ("/home/user/files/relatorio.PDF", True),
    # Caso 3: Apenas o nome do arquivo.
    ("meu_arquivo.pdf", True),
    # Caso 4: Caminho de arquivo de outro tipo.
    ("C:\\Users\\imagem.jpg", False),
    # Caso 5: Texto que contém ".pdf" no meio, mas não no final.
    ("pasta.pdf/arquivo.txt", False),
    # Caso 6: Texto sem a extensão.
    ("documento", False),
])
def test_is_pdf_file_path(path_input, expected_output):
    """
    Testa a função `is_pdf_file_path` para garantir que ela identifica
    corretamente strings que terminam com a extensão ".pdf".
    """
    # Verifica se a função retorna o booleano esperado.
    assert is_pdf_file_path(path_input) == expected_output