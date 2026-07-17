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
        # Configuración base de yt-dlp
        ydl_opts = {
            'format': 'best',
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
            # Extraemos la información del video
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    resolution = f.get('resolution') or f"{(f.get('height') or f.get('width') or 'video')}p"
                    
                    streams.append({
                        "resolution": resolution,
                        "url": f['url'],
                        "mime_type": f.get('ext', 'mp4')
                    })
            
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
