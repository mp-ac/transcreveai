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


def registrar_log(arquivo_log, mensagem):
    logging.basicConfig(
        filename=arquivo_log,
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    logging.info(mensagem)


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
            "message": os.getenv('APP_MSG'),
            "versão": os.getenv('APP_VERSION')
        }
    )


@app.route('/api/transcrever', methods=['POST'])
def transcrever():
    #  Requisição via web ou API
    if request.form.get('tipo_requisicao') == 'web':
        if 'chave_txt' not in request.files:
            registrar_log('error.log', "Erro: Arquivo de chave não fornecido")
            return jsonify({"status": "error", "message": "Arquivo de chave não fornecido"}), 400
        chave_txt = request.files['chave_txt']

        if chave_txt.filename == '':
            registrar_log('error.log', "Erro: Nenhum arquivo de chave foi selecionado")
            return jsonify({"status": "error", "message": "Nenhum arquivo de chave foi selecionado"}), 400
        chave = chave_txt.read().decode('utf-8').strip()
        chaves_permitidas = os.getenv('CHAVES').split(',')

        if chave not in chaves_permitidas:
            registrar_log('error.log', "Erro: Chave inválida")
            return jsonify({"status": "error", "message": "Chave inválida"}), 403
    else:
        chave = request.form.get('chave')
        if chave is None or chave == '' or chave != os.getenv('URL_KEY'):
            return jsonify(
                {
                    "status": "error",
                    "message": "Chave inválida"
                }
            ), 401

    timestamps_str = request.form.get('timestamps')
    if timestamps_str in ['true', 'false']:
        timestamps_str.lower()
        timestamps = timestamps_str == 'true'  # Converte para booleano
    else:
        timestamps = timestamps_str == 'false'  # Converte para booleano

    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    #  Calcular tamanho máximo do arquivo
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)

    if file_length > eval(os.getenv('TAMANHO_MAXIMO_ARQUIVO')):
        return jsonify(
            {
                "status": "error",
                "message": "O arquivo é muito grande. Tamanho máximo permitido: " +
                f"{eval(os.getenv('TAMANHO_MAXIMO_ARQUIVO')) / (1024 * 1024)} MB."
            }
        )

    #  Formatos permitidos
    formatos_permitidos = [
        'audio/mpeg',
        'audio/ogg',
        'video/ogg',
        'audio/wav',
        'video/mp4',
        'video/mpeg',
        'application/vnd.ms-asf'
    ]

    if file.content_type not in formatos_permitidos:
        registrar_log('error.log', f"Erro: Formato não permitido: {file.content_type}")
        return jsonify(
            {
                "status": "error",
                "message": "Formato de arquivo inválido"
            }
        ), 400

    try:
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
                os.remove(mp3_path)

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
            registrar_log(
                'transcricao.log',
                f"Arquivo '{file.filename}' - Tempo execução: {tempo_total}. - " +
                f"Salvo como '{transcricao_filename}'."
            )

            return jsonify(
                {
                    "status": "success",
                    "download": os.getenv('URL_PUB')+":"+os.getenv('PORT')+download_link,
                    "tempo_transcricao": tempo_total,
                }
            ), 200
    except Exception as e:
        registrar_log('error.log', f"Erro: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "Ocorreu um erro durante a transcrição do áudio."
            }
        ), 500


@app.route('/api/download/<filename>')
def download(filename):
    return send_from_directory(TRANSCRIBE_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host=os.getenv('URL'), port=8080)
