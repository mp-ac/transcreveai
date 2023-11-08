from transformers import  pipeline
import os
import time
import GPUtil
from tabulate import tabulate

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v2",
    generate_kwargs={"language": "br", "task": "transcribe"},
    device="cuda",
    use_fast=True
)

diretorio_audios = 'audios/'
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
            print('arquivo existe\n')
        else:
            print('\nTranscrevendo arquivo '+nome_arquivo+extensao_arquivo)

            res = pipe(diretorio_audios+nome_arquivo+extensao_arquivo, batch_size=10, return_timestamps=True, chunk_length_s=30, stride_length_s=(4, 2))

            input_dictionary = res['text']

            output = input_dictionary.replace(". ", "\n")
             
            file = open(diretorio_transcritos+'/'+nome_arquivo+formato_arquivo_saida, "w")
            file.write(output)
             
            file.close()
            f = open(diretorio_transcritos+'/'+nome_arquivo+formato_arquivo_saida, 'r')
            if f.mode=='r':
                contents= f.read()

            print('O arquivo de numero '+str(indice)+' '+nome_arquivo+formato_arquivo_saida+' foi salvo na pasta\n')
            time.sleep(1)

            # Alterando contador de chamadas do pipe para 0 para evitar avisos de mais de 10 chamadas
            pipe.call_count = 0

            if GPUtil.getGPUs()[0].temperature >= 75:
                print('\n\nPausa de 20 segundos para esfriar a GPU\n\n')
                time.sleep(20)

except Exception as e:
    print(f"\nOcorreu um erro: {e}\n")
