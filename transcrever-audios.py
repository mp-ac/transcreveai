import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from docx import Document
import os
import time
import GPUtil
from pydub import AudioSegment
from pyannote.audio import Pipeline
# import onnxruntime as ort

tempo_inicio = time.time()
tempo_total_audio = 0

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    generate_kwargs={"language": "portuguese"},
    device=device,
)

pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
)
pipeline.to(torch.device("cuda"))

diretorio_audios = 'audios'
diretorio_transcritos = 'audios-transcritos'
formato_arquivo_saida = '.docx'


def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


if not os.path.exists(diretorio_transcritos):
    os.makedirs(diretorio_transcritos)

try:
    arquivos = [arq for arq in os.listdir(diretorio_audios)]

    for indice, arquivo in enumerate(arquivos, start=1):
        nome_arquivo, extensao_arquivo = os.path.splitext(arquivo)
        arquivo_docx = nome_arquivo+formato_arquivo_saida

        caminho_completo_docx = os.path.join(diretorio_transcritos, arquivo_docx)

        if os.path.isfile(caminho_completo_docx):
            print('O arquivo de numero '+str(indice)+' '+nome_arquivo+formato_arquivo_saida+' já estava transcrito\n')
        else:
            print('\nTranscrevendo arquivo '+nome_arquivo+extensao_arquivo)

            audio_file = f'{diretorio_audios}/{nome_arquivo}{extensao_arquivo}'
            # print(ort.get_device()) # Exibe o device usado pelo ONNX Runtime (CPU ou GPU)
            diarization = pipeline(audio_file)

            res = pipe(
                    diretorio_audios+'/'+nome_arquivo+extensao_arquivo,
                    batch_size=10,
                    return_timestamps=True, chunk_length_s=30, stride_length_s=(4, 2)
            )

            document = Document()

            for chunk in res['chunks']:
                start_time = chunk['timestamp'][0]
                end_time = chunk['timestamp'][1]
                chunk_text = chunk['text']

                # Encontrar falantes correspondentes ao intervalo de tempo do chunk
                speakers = []
                for segment in diarization.itertracks(yield_label=True):
                    segment_start = segment[0].start
                    segment_end = segment[0].end
                    speaker = segment[2]

                    if segment_start < end_time and segment_end > start_time:
                        speakers.append(speaker)

                speakers = list(set(speakers))  # Remover duplicatas de falantes

                start_hms = seconds_to_hms(start_time)
                end_hms = seconds_to_hms(end_time)
                speakers_str = ', '.join(speakers)

                input_dictionary = f'[{start_hms} / {end_hms}] (Speakers: {speakers_str}) - {chunk_text}'
                document.add_paragraph(input_dictionary)

            document.save(f'{diretorio_transcritos}/{nome_arquivo}{formato_arquivo_saida}')

            # Calcular tempo total dos arquivos de áudio
            audio = AudioSegment.from_file(diretorio_audios+'/'+nome_arquivo+extensao_arquivo)
            duracao = len(audio)
            tempo_total_audio += duracao

            print('O arquivo de numero '+str(indice)+' '+nome_arquivo+formato_arquivo_saida+' foi salvo na pasta\n')

            # Alterando contador de chamadas do pipe para 0 para evitar avisos de mais de 10 chamadas
            pipe.call_count = 0

            if GPUtil.getGPUs()[0].temperature >= 75:
                print('\n\nPausa de 20 segundos para esfriar a GPU\n\n')
                time.sleep(20)

except Exception as e:
    print(f"\nOcorreu um erro: {e}\n")

tempo_fim = time.time()

tempo_total = tempo_fim - tempo_inicio
tempo_total = time.strftime("%H:%M:%S", time.gmtime(tempo_total))

print("\n\nTempo de execução do Script:", tempo_total)

tempo_total_segundos = tempo_total_audio / 1000  # Convertendo de milissegundos para segundos
tempo_total_minutos = tempo_total_segundos / 60
tempo_total_horas = tempo_total_minutos / 60

print("{:.2f}".format(tempo_total_minutos)+" minutos de áudio transcritos")

if(tempo_total_horas >= 1):
    print("{:.2f}".format(tempo_total_horas)+" horas de áudio transcritos")
