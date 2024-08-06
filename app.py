from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
import logging
from dotenv import load_dotenv
from transcribe import Transcrever
from pydub import AudioSegment
import time

transcribe = Transcrever()

load_dotenv('./.env')
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"

app = Flask(__name__)

logging.basicConfig(
    filename='transcricao.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Configura o diretório para uploads de áudio
UPLOAD_FOLDER = 'audios'
TRANSCRIBE_FOLDER = 'audios-transcritos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', chave=os.getenv('URL_KEY'))


@app.route('/api', methods=['GET'])
def index_api():
    return jsonify(
        {
            "status": "success",
            "app name": os.getenv('APP_NAME'),
            "message": "Transcrição de áudio com Whisper v3 LARGE",
            "versão": "v0.0.1"
        }
    )


@app.route('/api/transcrever', methods=['POST'])
def transcrever():
    chave = request.form.get('chave')
    if chave is None or chave == '' or chave != os.getenv('URL_KEY'):
        return jsonify(
            {
                "status": "error",
                "message": "Chave inválida"
            }
        )
        exit()

    timestamps_str = request.form.get('timestamps')
    if timestamps_str in ['true', 'false']:
        timestamps_str.lower()
        timestamps = timestamps_str == 'true'  # Converte para booleano
    else:
        timestamps = timestamps_str == 'false'  # Converte para booleano
    # else:
    #     return jsonify(
    #         {
    #             "status": "error",
    #             "message": "Parâmetro 'timestamps' deve ser 'true' ou 'false'"
    #         }
    #     )
    #     exit()

    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print("Upload concluído")

        tempo_inicio = time.time()
        _, file_extension = os.path.splitext(file.filename)
        if file_extension.lower() not in ['.mp3', '.ogg', '.wav']:
            print("Converter arquivo para .mp3")

            # Converter para .mp3
            audio = AudioSegment.from_file(file_path)
            mp3_filename = os.path.splitext(file.filename)[0] + '.mp3'
            mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)
            audio.export(mp3_path, format="mp3")
            print("Arquivo convertido pra .mp3. Iniciando transcrição")
            caminho_transcricao = transcribe.transcrever_audio(mp3_filename, timestamp=timestamps)

        else:
            print("Iniciando transcrição")
            caminho_transcricao = transcribe.transcrever_audio(file.filename, timestamp=timestamps)

        transcricao_filename = os.path.basename(caminho_transcricao)

        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        tempo_total = time.strftime("%H:%M:%S", time.gmtime(tempo_total))

        # Retorne sempre um JSON, pois o HTML será manipulado pelo JavaScript
        download_link = url_for('download', filename=transcricao_filename)

        os.remove(file_path)
        logging.info(
            f"Arquivo '{file.filename}' - Tempo execução: {tempo_total}. - " +
            f"Salvo como '{transcricao_filename}'."
        )

        return jsonify(
            {
                "status": "success",
                "download":  "http://"+os.getenv('URL_PUB')+":"+os.getenv('PORT')+download_link,
                "tempo_transcricao": tempo_total,
            }
        )


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(TRANSCRIBE_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host=os.getenv('URL'), port=os.getenv('PORT'), debug=True)
