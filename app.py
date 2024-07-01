from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from transcribe import transcrever_audio
from pydub import AudioSegment
import os

#local do ffmpeg
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"

app = Flask(__name__)

# Configura o diretório para uploads de áudio
UPLOAD_FOLDER = 'audios'
TRANSCRIBE_FOLDER = 'audios-transcritos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            caminho_transcricao = transcrever_audio(file.filename)
            transcricao_filename = os.path.basename(caminho_transcricao)
            return render_template('index.html', transcricao=transcricao_filename)
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(TRANSCRIBE_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
