from flask import Flask, request, Response
import yt_dlp
import requests
import os

app = Flask(__name__)

# Configuración del Proxy (Asegúrate de que este proxy siga activo en Webshare)
PROXY_URL = "http://xgazzmhp:5uqjrn9myazq@31.59.20.176:6754"

# Ruta para el archivo de cookies
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, 'cookies.txt')

# User Agent para simular un navegador real
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

@app.route('/')
def home():
    return "Servidor Proxy de Descargas activo"

@app.route('/descargar')
def descargar():
    url = request.args.get('url')
    if not url:
        return "Falta la URL", 400
    
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'proxy': PROXY_URL,
            'quiet': True,
            'cookiefile': COOKIES_PATH,
            'user_agent': USER_AGENT,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        
        r = requests.get(video_url, stream=True, headers={'User-Agent': USER_AGENT})
        return Response(
            r.iter_content(chunk_size=1024*1024), 
            content_type=r.headers.get('Content-Type', 'video/mp4'),
            headers={'Content-Disposition': 'attachment; filename="video.mp4"'}
        )
    except Exception as e:
        return f"Error en descarga: {str(e)}", 500

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return {"error": "Falta la URL"}, 400
        
    try:
        ydl_opts = {
            'proxy': PROXY_URL, 
            'quiet': True,
            'cookiefile': COOKIES_PATH,
            'user_agent': USER_AGENT
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            streams = []
            for f in info.get('formats', []):
                # Filtramos solo formatos de video con URL válida
                if f.get('vcodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    if height and height >= 144:
                        streams.append({
                            "resolution": f"{height}p",
                            "url": f['url'],
                            "mime_type": f.get('ext', 'mp4')
                        })
            return {"title": info.get('title', 'video'), "streams": streams}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
