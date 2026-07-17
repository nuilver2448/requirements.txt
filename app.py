from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Usamos la ruta absoluta del directorio del script para evitar fallos de ubicación en Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, 'cookies.txt')

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        # Configuración base segura
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'check_formats': False,  # Evita validaciones pesadas en el servidor
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            }
        }
        
        # Validación estricta del archivo de cookies
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            print(f"ÉXITO: Usando archivo cookies detectado en: {COOKIES_FILE}")
        else:
            # Si no existe, le mandamos un error claro a la App para saber que no se subió bien
            return jsonify({
                "error": "Error de configuración: El archivo cookies.txt no se encuentra en el servidor. Por favor súbelo a GitHub."
            }), 500

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la información del video
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                ext = f.get('ext', '')
                # Filtramos formatos basura
                if ext in ['mhtml', 'storyboard']:
                    continue
                
                # Buscamos formatos combinados (video + audio)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": ext if ext else "mp4"
                            })
            
            # Formato de respaldo por si el filtro estricto no arroja nada
            if not streams and info.get('url'):
                streams.append({
                    "resolution": "Default (Best)",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            # Ordenamos calidades
            streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            if not streams:
                return jsonify({"error": "No se encontraron formatos de video compatibles."}), 400

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        # Añadimos un mensaje amigable si YouTube sigue detectando el bot
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            return jsonify({
                "error": "YouTube bloqueó la petición temporalmente. Por favor, genera un archivo cookies.txt nuevo e inténtalo otra vez."
            }), 403
        return jsonify({"error": f"Error al procesar con yt-dlp: {error_msg}"}), 400

if __name__ == '__main__':
    app.run()
