from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/get_video_info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta la URL"}), 400
    try:
        yt = YouTube(url)
        streams = []
        # Obtenemos las descargas con video y audio
        for stream in yt.streams.filter(progressive=True):
            streams.append({
                "resolution": stream.resolution,
                "url": stream.url,
                "mime_type": stream.mime_type
            })
        return jsonify({"title": yt.title, "streams": streams})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
