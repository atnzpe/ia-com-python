# -*- coding: utf-8 -*-

"""
Arquivo de testes para as funções auxiliares de main.py.
Usa a biblioteca pytest para verificar o comportamento das funções
de detecção de URL e carregamento de conteúdo.
"""

# Importa a biblioteca de testes.
import pytest

# Importa as funções que queremos testar do nosso arquivo principal.
from main import find_url, get_content_from_url

# --- Testes para a função find_url ---

def test_find_url_com_url_http():
    """Verifica se a função encontra corretamente uma URL com http."""
    texto = "Por favor, leia este artigo: http://example.com/artigo"
    assert find_url(texto) == "http://example.com/artigo"

def test_find_url_com_url_https():
    """Verifica se a função encontra corretamente uma URL com https."""
    texto = "Veja isso https://www.google.com e me diga o que acha."
    assert find_url(texto) == "https://www.google.com"

def test_find_url_sem_url():
    """Verifica se a função retorna None quando não há URL no texto."""
    texto = "Qual a capital do Brasil?"
    assert find_url(texto) is None

def test_find_url_com_multiplas_palavras():
    """Verifica se a URL é extraída corretamente de uma frase complexa."""
    texto = "Acho que a melhor fonte é https://flet.dev/docs, o que você acha?"
    assert find_url(texto) == "https://flet.dev/docs"

# --- Testes para a função get_content_from_url ---

# A anotação @pytest.mark.skip é usada para pular um teste.
# Este teste é pulado por padrão porque ele faz uma chamada real à internet,
# o que pode tornar os testes lentos e dependentes de conexão externa.
# Para rodá-lo, comente ou remova a linha abaixo e execute: pytest
@pytest.mark.skip(reason="Este teste faz uma chamada real à rede e pode ser lento.")
def test_get_content_from_url_com_sucesso():
    """
    Verifica se a função consegue carregar conteúdo de uma URL válida.
    NOTA: Este é um teste de integração, não um teste de unidade puro.
    """
    # Usamos uma URL que sabemos que deve funcionar.
    url = "https://www.google.com"
    content = get_content_from_url(url)
    # Verificamos se o conteúdo retornado não é nulo ou vazio.
    assert content is not None
    assert "Google" in content

def test_get_content_from_url_com_erro():
    """Verifica se a função retorna None para uma URL claramente inválida."""
    # Uma URL que não existe.
    url = "http://dominio-inexistente-12345.com"
    # Esperamos que a função falhe graciosamente e retorne None.
    assert get_content_from_url(url) is None