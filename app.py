from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Definimos la ruta del archivo de cookies en el servidor
COOKIES_FILE = 'cookies.txt'

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        # Configuración ultra-flexible: extraemos todos los formatos disponibles sin filtrar aquí
        ydl_opts = {
            'format': 'all',  # <--- Evita que yt-dlp lance error por no encontrar un formato específico
            'quiet': True,
            'no_warnings': True,
        }
        
        # Si el archivo cookies.txt existe en el servidor, lo aplicamos
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            print("Usando archivo cookies.txt para evadir el bloqueo.")
        else:
            print("Advertencia: No se encontró el archivo cookies.txt en el directorio.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la información completa
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                # Filtramos manualmente formatos que tengan video, audio y un enlace válido
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    # Determinamos la resolución de manera segura
                    resolution = f.get('resolution')
                    if not resolution:
                        height = f.get('height')
                        resolution = f"{height}p" if height else "video"
                    
                    streams.append({
                        "resolution": resolution,
                        "url": f['url'],
                        "mime_type": f.get('ext', 'mp4')
                    })
            
            # Si tras filtrar no quedó ninguno, intentamos usar el formato directo que youtube-dl considere mejor
            if not streams and info.get('url'):
                streams.append({
                    "resolution": info.get('resolution') or "default",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            # Si de plano no hay ningún enlace útil, lanzamos un error controlado
            if not streams:
                return jsonify({"error": "No se encontraron formatos de video directo compatibles para este enlace."}), 400

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error al procesar con yt-dlp: {str(e)}"}), 400

if __name__ == '__main__':
    app.run()
