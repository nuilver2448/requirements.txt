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
        # Extraemos todos los formatos para evitar bloqueos por restricciones de descarga
        ydl_opts = {
            'format': 'all',
            'quiet': True,
            'no_warnings': True,
        }
        
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            print("Usando archivo cookies.txt para evadir el bloqueo.")
        else:
            print("Advertencia: No se encontró el archivo cookies.txt en el directorio.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                ext = f.get('ext', '')
                # 1. Filtramos para descartar extensiones raras como mhtml, storyboards (mhtml) o solo audio
                if ext in ['mhtml', 'storyboard'] or f.get('vcodec') == 'none':
                    continue
                
                # 2. Nos aseguramos de que tenga un enlace url directo válido
                if f.get('url'):
                    # Obtenemos la altura del video (ej. 360, 720, 1080)
                    height = f.get('height')
                    
                    # Ignoramos resoluciones extremadamente bajas que suelen ser miniaturas o fallos
                    if height and height >= 144:
                        resolution = f"{height}p"
                        
                        # Evitamos duplicados en la lista final
                        if not any(s['resolution'] == resolution for s in streams):
                            streams.append({
                                "resolution": resolution,
                                "url": f['url'],
                                "mime_type": ext if ext else "mp4"
                            })
            
            # Ordenamos las calidades de mayor a menor (ej. 1080p, 720p, 360p)
            streams.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].replace('p', '').isdigit() else 0, reverse=True)

            # Si por algún motivo el filtro estricto falló, usamos el formato básico por defecto
            if not streams and info.get('url'):
                streams.append({
                    "resolution": "Default (Best)",
                    "url": info['url'],
                    "mime_type": info.get('ext', 'mp4')
                })

            if not streams:
                return jsonify({"error": "No se encontraron formatos de video estándar disponibles."}), 400

            return jsonify({
                "title": info.get('title', 'video'), 
                "streams": streams
            })
            
    except Exception as e:
        return jsonify({"error": f"Error al procesar con yt-dlp: {str(e)}"}), 400

if __name__ == '__main__':
    app.run()
