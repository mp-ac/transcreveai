import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from docx import Document
import os
import GPUtil
from pydub import AudioSegment

# Defina o caminho do ffmpeg se necessário
AudioSegment.ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"  # Substitua pelo caminho correto no Windows
# AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"  # Substitua pelo caminho correto no macOS ou Linux

def transcrever_audio(nome_arquivo):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
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

    diretorio_audios = 'audios'
    diretorio_transcritos = 'audios-transcritos'
    formato_arquivo_saida = '.docx'

    if not os.path.exists(diretorio_transcritos):
        os.makedirs(diretorio_transcritos)

    nome_arquivo, extensao_arquivo = os.path.splitext(nome_arquivo)
    arquivo_docx = nome_arquivo + formato_arquivo_saida

    caminho_completo_docx = os.path.join(diretorio_transcritos, arquivo_docx)

    if os.path.isfile(caminho_completo_docx):
        return caminho_completo_docx
    else:
        res = pipe(os.path.join(diretorio_audios, nome_arquivo + extensao_arquivo), batch_size=10, return_timestamps=True, chunk_length_s=30, stride_length_s=(4, 2))
        input_dictionary = res['text']
        output = input_dictionary.replace(". ", "\n\n")

        document = Document()
        document.add_paragraph(output)
        document.save(caminho_completo_docx)

        return caminho_completo_docx
