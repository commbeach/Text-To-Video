#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

# Carrega variáveis de ambiente
load_dotenv()
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
if not PEXELS_API_KEY:
    raise ValueError('A variável de ambiente PEXELS_API_KEY não está definida.')


def search_videos(query_string: str, orientation_landscape: bool = True) -> dict:
    """
    Busca vídeos no Pexels com base numa query e orientação.
    Retorna o JSON da API.
    """
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, data)
    return data


def get_best_video(query_string: str, orientation_landscape: bool = True, used_vids: list = None) -> str:
    """
    Retorna o link do primeiro vídeo não utilizado que atenda à resolução 16:9.
    """
    used_vids = used_vids or []
    data = search_videos(query_string, orientation_landscape)
    videos = data.get('videos', [])

    # Filtra vídeos com resolução mínima e proporção 16:9
    if orientation_landscape:
        filtered = [v for v in videos
                    if v['width'] >= 1920 and v['height'] >= 1080
                    and abs((v['width'] / v['height']) - (16/9)) < 0.01]
    else:
        filtered = [v for v in videos
                    if v['width'] >= 1080 and v['height'] >= 1920
                    and abs((v['height'] / v['width']) - (16/9)) < 0.01]

    # Ordena por duração próxima a 15s
    filtered.sort(key=lambda v: abs(v.get('duration', 0) - 15))

    for video in filtered:
        for vf in video.get('video_files', []):
            w, h, link = vf['width'], vf['height'], vf['link']
            key = link.split('.hd')[0]
            if orientation_landscape and w == 1920 and h == 1080:
                if key not in used_vids:
                    return link
            if not orientation_landscape and w == 1080 and h == 1920:
                if key not in used_vids:
                    return link
    # se não encontrou
    return None


def generate_video_url(timed_searches: list, video_server: str) -> list:
    """
    Para cada segmento ([t1, t2], [kw1, kw2,...]), busca um vídeo correspondente.
    Suporta apenas 'pexels'.
    Retorna lista de [[t1, t2], url] (url pode ser None).
    """
    results = []
    if video_server.lower() == 'pexels':
        used = []
        for (t1, t2), queries in timed_searches:
            url = None
            for q in queries:
                link = get_best_video(q, True, used)
                if link:
                    used.append(link.split('.hd')[0])
                    url = link
                    break
            results.append([[t1, t2], url])
    else:
        raise ValueError(f"Serviço de vídeo desconhecido: {video_server}")
    return results
