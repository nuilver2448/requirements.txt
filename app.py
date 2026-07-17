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
        # Configuración ultra-segura para evitar validaciones pesadas en el servidor
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'check_formats': False,  # <--- EVITA QUE YT-DLP VALIDE FORMATOS Y TRUENE EN RENDER
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
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                ext = f.get('ext', '')
                # Filtramos: Descartamos páginas web (mhtml) e imágenes (storyboard)
                if ext in ['mhtml', 'storyboard']:
                    continue
                
                # Buscamos formatos que tengan audio y video combinados para que Flutter los reproduzca/descargue directo sin problemas
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    
                    # Filtramos resoluciones normales (144p en adelante)
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        # Evitamos duplicados
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": ext if ext else "mp4"
                            })
            
            # Si no encontramos formatos combinados por el filtro estricto, añadimos el mejor disponible por defecto
            if not streams and info.get('url'):
                streams.append({
                    "resolution": "720p" if info.get('height') == 720 else "360p",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            # Ordenamos las calidades de mayor a menor (ej. 720p, 360p)
            streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            if not streams:
                return jsonify({"error": "No se encontraron formatos de video estándar y limpios disponibles."}), 400

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error al procesar con yt-dlp: {str(e)}"}), 400

if __name__ == '__main__':
    app.run()
