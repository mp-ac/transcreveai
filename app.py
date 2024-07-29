from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import os
from dotenv import load_dotenv
from transcribe import transcrever_audio
from pydub import AudioSegment

load_dotenv('./.env')

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
            return jsonify(
                    {
                        "download":  os.getenv('URL')+":"+os.getenv('PORT')+"/"+url_for('download_file', filename=transcricao_filename),
                    }
            )
    return jsonify(
            {
                "status": "ok",
                "message": "Transcrição de áudio com Whisper v3 LARGE",
                "versão": "v0.0.1"
            }
    )

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(TRANSCRIBE_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host=os.getenv('URL'), port=os.getenv('PORT'), debug=True)
