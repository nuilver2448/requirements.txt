from flask import Flask, request, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/descargar-mp3')
def descargar_mp3():
    video_url = request.args.get('url')
    if not video_url:
        return "Error: No se proporcionó ninguna URL", 400
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            url_audio = info['url']
            return redirect(url_audio)
        except Exception as e:
            return f"Error al procesar el audio: {str(e)}", 500

if __name__ == '__main__':
    app.run()
