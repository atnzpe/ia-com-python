# -*- coding: utf-8 -*-

"""
Arquivo de testes para as funções auxiliares de main.py.
"""
import pytest
# Importa as novas funções que queremos testar.
from main import find_url, get_content_from_url, is_youtube_url, get_content_from_youtube

# --- Testes para a função find_url (inalterados) ---
def test_find_url_com_url_http():
    assert find_url("Leia http://example.com") == "http://example.com"
def test_find_url_sem_url():
    assert find_url("Qual a capital do Brasil?") is None

# --- [NOVO] Testes para a função is_youtube_url ---
def test_is_youtube_url_com_link_padrao():
    """Verifica se identifica um link padrão do YouTube."""
    assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

def test_is_youtube_url_com_link_curto():
    """Verifica se identifica um link curto do YouTube (youtu.be)."""
    assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True

def test_is_youtube_url_com_link_generico():
    """Verifica se retorna False para um site que não é o YouTube."""
    assert is_youtube_url("https://www.google.com") is False

def test_is_youtube_url_texto_sem_link():
    """Verifica se retorna False para um texto sem link."""
    assert is_youtube_url("um video sobre python no youtube") is False

# --- Testes para os loaders (com chamadas de rede puladas por padrão) ---
@pytest.mark.skip(reason="Este teste faz uma chamada real à rede.")
def test_get_content_from_url_com_sucesso():
    assert get_content_from_url("https://flet.dev/") is not None

def test_get_content_from_url_com_erro():
    assert get_content_from_url("http://dominio-inexistente-12345.com") is None

@pytest.mark.skip(reason="Este teste faz uma chamada real à rede e depende de legendas.")
def test_get_content_from_youtube_com_sucesso():
    """Verifica se a função consegue carregar a transcrição de um vídeo."""
    # URL de um vídeo que sabemos que tem legendas em português ou inglês.
    url = "https://www.youtube.com/watch?v=nLplWffsLI&ab_channel=AsimovAcademy" 
    content = get_content_from_youtube(url)
    assert content is not None
    # Verifica se uma palavra comum do vídeo está na transcrição.
    assert "Python" in content 

def test_get_content_from_youtube_com_erro():
    """Verifica se retorna None para um vídeo inválido ou sem legendas."""
    # Link para um vídeo que não existe.
    url = "https://www.youtube.com/watch?v=videoquenaoexiste"
    assert get_content_from_youtube(url) is None