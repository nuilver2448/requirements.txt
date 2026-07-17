from flask import Flask, request, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    if not video_url:
        return "Error: No se proporcionó ninguna URL", 400
    
    # Configuración optimizada para simular un navegador real
    ydl_opts = {
        'format': 'best',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }
    
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
