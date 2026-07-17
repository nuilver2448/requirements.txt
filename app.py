from flask import Flask, request, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    if not video_url:
        return "Error: No se proporcionó ninguna URL", 400
    
    # Aquí obtenemos la información real del video de forma rápida
    ydl_opts = {'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            url_descarga = info['url']
            # Redireccionamos directamente al archivo de video real
            return redirect(url_descarga)
        except Exception as e:
            return f"Error al procesar el video: {str(e)}", 500

if __name__ == '__main__':
    app.run()
