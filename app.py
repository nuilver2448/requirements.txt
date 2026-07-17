from flask import Flask, request, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    if not video_url:
        return "Error: No URL", 400
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            url_video_real = info['url']
            
            # Aquí está el truco: descargamos el stream del video en el servidor 
            # y lo enviamos al usuario como una descarga forzada
            video_stream = requests.get(url_video_real, stream=True)
            
            return Response(
                video_stream.iter_content(chunk_size=1024*1024),
                content_type='video/mp4',
                headers={'Content-Disposition': 'attachment; filename="nexo_video.mp4"'}
            )
            
        except Exception as e:
            return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run()
