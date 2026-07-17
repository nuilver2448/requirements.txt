@app.route('/descargar')
def descargar():
    url = request.args.get('url')
    if not url:
        return "Falta la URL", 400
    
    try:
        # Configuración "segura": sin forzar formatos complejos que bloquean la IP
        ydl_opts = {
            'format': 'best', 
            'quiet': True,
            'proxy': PROXY_URL,
            'cookiefile': COOKIES_PATH,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        
        r = requests.get(video_url, stream=True)
        return Response(
            r.iter_content(chunk_size=1024*1024), 
            content_type=r.headers.get('Content-Type', 'video/mp4')
        )
    except Exception as e:
        return f"Error: {str(e)}", 500
