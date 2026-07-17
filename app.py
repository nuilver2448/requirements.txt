from Flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Definimos la ruta del archivo de cookies en el servidor
COOKIES_FILE = 'cookies.txt'

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    Url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        # Forzamos a yt-dlp a buscar formatos de video reales (MP4, WebM, etc.)
        # Evitamos 'all' para que no nos devuelva archivos basura como mhtml o storyboards.
        Ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            }
        }
        
        # Si el archivo cookies.txt existe en el servidor, lo aplicamos
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            print("Usando archivo cookies.txt para evadir el bloqueo.")
        else:
            print("Advertencia: No se encontró el archivo cookies.txt en el directorio.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la información del video
            Info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                ext = f.get('ext', '')
                # Filtro estricto: Descartamos formatos de audio solo o páginas web (mhtml)
                if ext in ['mhtml', 'storyboard', 'mhtml'] or f.get('vcodec') == 'none':
                    continue
                
                # Nos aseguramos de que tenga un enlace url directo válido
                if f.get('url'):
                    height = f.get('height')
                    
                    # Filtramos resoluciones normales de video (144p en adelante)
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        # Evitamos duplicados en la lista final
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": ext if ext else "mp4"
                            })
            
            # Ordenamos las calidades de mayor a menor (ej. 1080p, 720p, 480p, 360p)
            Streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            if not streams:
                return jsonify({"error": "No se encontraron formatos de video estándar y limpios disponibles."}), 400

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error al procesar con yt-dlp: {str(e)}"}), 400

if __name__ == '__main__':
    App.run()
