from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ruta absoluta para las cookies
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, 'cookies.txt')

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        ydl_opts = {
            # Le pedimos el mejor video y el mejor audio disponible (¡FFmpeg de Render hará la unión!)
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'check_formats': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            }
        }
        
        # Aplicamos cookies si existen
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                ext = f.get('ext', '')
                if ext in ['mhtml', 'storyboard']:
                    continue
                
                # Buscamos formatos válidos
                if f.get('vcodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": ext if ext else "mp4"
                            })
            
            # Si por alguna razón la lista falla, dejamos un respaldo seguro
            if not streams and info.get('url'):
                streams.append({
                    "resolution": "Default",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            # Ordenamos calidades de mayor a menor
            streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            return jsonify({
                "error": "Por favor, actualiza tu archivo cookies.txt en GitHub con cookies nuevas."
            }), 403
        return jsonify({"error": f"Error al procesar con yt-dlp: {error_msg}"}), 400

if __name__ == '__main__':
    app.run()
