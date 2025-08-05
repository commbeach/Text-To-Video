#!/usr/bin/env python3
import os
import argparse
import asyncio

from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media

def main():
    parser = argparse.ArgumentParser(
        description="Gera um vídeo jornalístico de ~60s a partir de um tópico."
    )
    parser.add_argument("topic", type=str, help="Tópico para o roteiro do vídeo")
    parser.add_argument("--v", action="store_false", help="Gera video vertical")
    parser.add_argument("--f", action="store_true", help="Gera voz feminina")
    parser.add_argument(
        "--tts-voice", type=str,
        default=os.getenv('TTS_VOICE', 'pt-BR-AntonioNeural'),
        help="Voz TTS (ex: pt-BR-AntonioNeural)"
    )
    parser.add_argument(
        "--video-source", type=str,
        default=os.getenv('VIDEO_SOURCE', 'pexels'),
        help="Serviço de vídeo de fundo (e.g. pexels)"
    )
    args = parser.parse_args()
    print(args.topic)
    # 1. Roteiro
    file_path = 'script.txt'
    try: 
        file = open(file_path, 'r')
        script=file.read()
        print(f"[1/5] Roteiro encontrado:\n{script}\n")

    except:
        script = generate_script(args.topic)
        print(f"[1/5] Roteiro gerado:\n{script}\n")

    # 2. Áudio TTS
    voz_locutor=args.tts_voice
    print(f"[2/5] Gerando áudio TTS...")
    if(args.f):
        voz_locutor = "pt-BR-ThalitaMultilingualNeural" 
    
    asyncio.run(generate_audio(script, "audio_tts.wav", voice=voz_locutor))

    # 3. Legendas Karaoke
    print("[3/5] Transcrevendo áudio para legendas temporizadas...")
    captions = generate_timed_captions("audio_tts.wav")
    print(f"captions {(captions)}")
    print(f" {len(captions)} legendas geradas")

    # 4. Queries de vídeo
    print("[4/5] Gerando queries de busca para vídeos de fundo...")
    queries = getVideoSearchQueriesTimed(script, captions)
    if not queries:
        print("Nenhuma query gerada; abortando.")
        return

    # 5. URLs de vídeo e merge
    print("[5/5] Obtendo vídeos de fundo...")
    if(not args.v):
        print("Gerando Video Vertical")
    else:
        print("Gerando Video Horizontal")

    urls = generate_video_url(queries, args.video_source, args.v)
    #print(urls)
    urls = merge_empty_intervals(urls)

    # 6. Render final
    print("Renderizando vídeo final...")
    print(args.video_source)
    output = get_output_media("audio_tts.wav", captions, urls, args.video_source, args.v)
    print(f"Vídeo gerado em: {output}")

if __name__ == '__main__':
    main()
