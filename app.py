from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# =================================================================
# CONFIGURACIÓN DEL PROXY (WEB-SHARE)
# Este proxy enmascara la IP de Render para que YouTube no nos bloquee
# =================================================================
PROXY_URL = "http://xgazzmhp:5uqjrn9myazq@31.59.20.176:6754"

# Ruta absoluta para el archivo cookies.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, 'cookies.txt')

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'check_formats': False,
            'proxy': PROXY_URL,  # Activamos el enmascaramiento de IP
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        
        # Aplicamos cookies si existen para mayor seguridad
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                # Filtramos formatos no deseados
                if f.get('ext') in ['mhtml', 'storyboard']:
                    continue
                
                # Buscamos formatos con video y audio
                if f.get('vcodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": f.get('ext', 'mp4')
                            })
            
            # Respaldo si no hay streams filtrados
            if not streams and info.get('url'):
                streams.append({
                    "resolution": "Default",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error crítico: {str(e)}"}), 400

if __name__ == '__main__':
    app.run()
