from flask import Flask, request, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    if not video_url or "odysee.com" not in video_url:
        return "Error: Solo se permiten enlaces de Odysee", 400
    
    # Configuración limpia para Odysee
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            url_video_real = info['url']
            
            # Descargamos el stream y lo enviamos al usuario
            video_stream = requests.get(url_video_real, stream=True)
            
            return Response(
                video_stream.iter_content(chunk_size=1024*1024),
                content_type='video/mp4',
                headers={'Content-Disposition': 'attachment; filename="video_odysee.mp4"'}
            )
            
        except Exception as e:
            return f"Error procesando el video de Odysee: {str(e)}", 500

if __name__ == '__main__':
    app.run()
