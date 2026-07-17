from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/descargar')
def descargar():
    video_url = request.args.get('url')
    if not video_url:
        return "Error", 400
    
    # Extraemos el ID del video del enlace de YouTube
    # Ejemplo: https://www.youtube.com/watch?v=EMKbOG_Rx8w -> EMKbOG_Rx8w
    video_id = ""
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
    
    if not video_id:
        return "URL no válida", 400

    # APLICAMOS EL TRUCO: Redirigimos a un servicio que fuerza la descarga automáticamente
    # Usamos un servicio que maneja el truco de la URL por nosotros
    url_truco = f"https://ssyoutube.com/watch?v={video_id}"
    
    return redirect(url_truco)

if __name__ == '__main__':
    app.run()
