from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
        
    try:
        # Configuración de yt-dlp para extraer información sin descargar el archivo
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos los metadatos del video
            info = ydl.extract_info(url, download=False)
            
            # Filtramos los formatos que tengan video y audio juntos (similar a progressive de pytube)
            # y que tengan una URL de descarga directa activa
            streams = []
            formats = info.get('formats', [])
            
            for f in formats:
                # Buscamos formatos que tengan tanto video como audio (acodec y vcodec no sean None o 'none')
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    # Simplificamos la resolución para mostrarla de manera amigable
                    resolution = f.get('resolution') or f"{(f.get('height') or f.get('width') or 'video')}p"
                    
                    streams.append({
                        "resolution": resolution,
                        "url": f['url'],
                        "mime_type": f.get('ext', 'mp4') # Usamos la extensión como tipo
                    })
            
            # Si por alguna razón la lista quedó vacía, añadimos el formato por defecto "best"
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
