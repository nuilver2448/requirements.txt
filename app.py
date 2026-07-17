from flask import Flask, request, Response, render_template_string
import yt_dlp
import requests

app = Flask(__name__)

# Interfaz con botones grandes y claros
UI_TEMPLATE = """
<html>
<body style="background-color: #121212; color: white; font-family: sans-serif; padding: 20px;">
    <h2 style="color: #03dac6; text-align: center;">RESULTADOS NEXO</h2>
    {% for v in results %}
        <div style="background: #1e1e1e; margin-bottom: 15px; padding: 15px; border-radius: 10px;">
            <p style="font-size: 16px; margin: 0 0 10px 0;">{{ v.title }}</p>
            <a href="/descargar?url={{ v.webpage_url }}" 
               style="display: block; background: #6200ea; color: white; text-align: center; 
                      padding: 12px; text-decoration: none; border-radius: 5px; font-weight: bold;">
               DESCARGAR VIDEO
            </a>
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/buscar')
def buscar():
    query = request.args.get('q')
    ydl_opts = {'quiet': True, 'default_search': 'odysee'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
        return render_template_string(UI_TEMPLATE, results=results)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    # Opciones para Odysee
    ydl_opts = {'format': 'best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_stream = requests.get(info['url'], stream=True)
        return Response(
            video_stream.iter_content(chunk_size=1024*1024),
            content_type='video/mp4',
            headers={'Content-Disposition': 'attachment; filename="nexo_descarga.mp4"'}
        )

if __name__ == '__main__':
    app.run()
