from flask import Flask, request, Response
import yt_dlp
import requests
import os

app = Flask(__name__)

# Configuración del Proxy
PROXY_URL = "http://xgazzmhp:5uqjrn9myazq@31.59.20.176:6754"

# Ruta absoluta para que encuentre el archivo cookies.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, 'cookies.txt')

@app.route('/descargar')
def descargar():
    url = request.args.get('url')
    if not url:
        return "Falta la URL", 400
    
    try:
        # Configuración forzando el uso de las cookies
        ydl_opts = {
            'format': 'best',
            'proxy': PROXY_URL,
            'quiet': True,
            'cookiefile': COOKIES_PATH,  # Aquí usamos la ruta absoluta
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        
        r = requests.get(video_url, stream=True)
        return Response(
            r.iter_content(chunk_size=1024*1024), 
            content_type=r.headers.get('Content-Type', 'video/mp4'),
            headers={'Content-Disposition': 'attachment; filename="video.mp4"'}
        )
    except Exception as e:
        return f"Error con cookies o proxy: {str(e)}", 500

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return {"error": "Falta la URL"}, 400
        
    try:
        ydl_opts = {
            'proxy': PROXY_URL, 
            'quiet': True,
            'cookiefile': COOKIES_PATH
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            streams = []
            for f in info.get('formats', []):
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
