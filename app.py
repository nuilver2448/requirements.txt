from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        # Configuración avanzada para evadir la detección de bots
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            # Forzamos a yt-dlp a usar clientes oficiales (iOS, Android y Web) para evadir el captcha
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'skip': ['webpage', 'authcheck'],
                }
            },
            # Mandamos cabeceras HTTP reales para que parezca un usuario común
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos los metadatos del video sin descargarlo
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                # Filtramos solo los formatos que contengan video y audio juntos
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    resolution = f.get('resolution') or f"{(f.get('height') or f.get('width') or 'video')}p"
                    
                    streams.append({
                        "resolution": resolution,
                        "url": f['url'],
                        "mime_type": f.get('ext', 'mp4')
                    })
            
            # En caso de que falle el filtro anterior, agregamos el formato directo básico
            if not streams and info.get('url'):
                streams.append({
                    "resolution": info.get('resolution') or "best",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error al procesar con yt-dlp: {str(e)}"}), 400

if __name__ == '__main__':
    app.run()
