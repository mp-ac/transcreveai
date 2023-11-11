import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
import time
import GPUtil
from pydub import AudioSegment

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
    device=device,
)

diretorio_audios = 'audios'
diretorio_transcritos = 'audios-transcritos'
formato_arquivo_saida = '.docx'

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

            res = pipe(diretorio_audios+'/'+nome_arquivo+extensao_arquivo, batch_size=10, return_timestamps=True, chunk_length_s=30, stride_length_s=(4, 2))

            input_dictionary = res['text']

            output = input_dictionary.replace(". ", "\n\n")
             
            file = open(diretorio_transcritos+'/'+nome_arquivo+formato_arquivo_saida, "w")
            file.write(output)
             
            file.close()
            f = open(diretorio_transcritos+'/'+nome_arquivo+formato_arquivo_saida, 'r')
            if f.mode=='r':
                contents= f.read()

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
