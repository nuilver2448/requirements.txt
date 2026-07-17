from flask import Flask, request, Response
import yt_dlp
import requests

app = Flask(__name__)

# Configuración del Proxy para saltar bloqueos de YouTube
PROXY_URL = "http://xgazzmhp:5uqjrn9myazq@31.59.20.176:6754"

@app.route('/descargar')
def descargar():
    url = request.args.get('url')
    if not url:
        return "Falta la URL", 400
    
    try:
        # Extraemos la información del video usando el proxy
        ydl_opts = {
            'format': 'best',
            'proxy': PROXY_URL,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        
        # El servidor de Render descarga el stream y lo pasa al usuario
        # Esto evita el error 403 Forbidden al ser Render quien gestiona la conexión
        r = requests.get(video_url, stream=True)
        
        return Response(
            r.iter_content(chunk_size=1024*1024), 
            content_type=r.headers.get('Content-Type', 'video/mp4'),
            headers={'Content-Disposition': 'attachment; filename="video.mp4"'}
        )
        
    except Exception as e:
        return f"Error procesando la descarga: {str(e)}", 500

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    # Mantenemos esta ruta para que tu App siga obteniendo la lista de calidades
    url = request.args.get('url')
    if not url:
        return {"error": "Falta la URL"}, 400
        
    try:
        ydl_opts = {'proxy': PROXY_URL, 'quiet': True}
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
    app.run()
