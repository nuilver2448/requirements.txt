from flask import Flask, request, render_template_string
import yt_dlp

app = Flask(__name__)

# Esta interfaz es minimalista para que cargue perfecto en tu app
UI_TEMPLATE = """
<html>
<body style="background-color: #121212; color: white; font-family: sans-serif; padding: 20px;">
    <h2 style="color: #03dac6;">Resultados de búsqueda</h2>
    {% for v in results %}
        <div style="border-bottom: 1px solid #333; padding: 15px 0;">
            <p style="margin-bottom: 10px;">{{ v.title }}</p>
            <!-- Enlace temporal solo para verificar que funciona -->
            <a href="{{ v.webpage_url }}" style="color: #bb86fc;">Ver en Odysee</a>
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/buscar')
def buscar():
    query = request.args.get('q')
    if not query:
        return "Por favor, escribe algo para buscar.", 400
    
    # Buscamos en Odysee
    ydl_opts = {'quiet': True, 'default_search': 'odysee'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Obtenemos los 5 primeros resultados
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            return render_template_string(UI_TEMPLATE, results=search_results)
        except Exception as e:
            return f"Error en la búsqueda: {str(e)}", 500

if __name__ == '__main__':
    app.run()
