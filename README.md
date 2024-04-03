## Áudio para texto

Este simples trecho de código percorre todos os arquivos de áudio de uma pasta chamada **audios** para fazer a transcrição para texto, 
gerando para cada arquivo, um novo arquivo com o mesmo nome no formato _.docx_

O PML (modelo de linguagem pré-treinado) **whisper-large-v3** foi criado e é mantido pela **OpenAI**.

### Whisper
Whisper é um modelo pré-treinado para reconhecimento automático de fala (ASR) e tradução de fala. 
Treinado com 680 mil horas de dados rotulados, os modelos Whisper demonstram uma forte capacidade de se adaptar a muitos conjuntos de dados e áreas sem a necessidade de ajustes finos.

Saiba mais em [https://huggingface.co/openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3)

### Requisitos

Cria uma pasta chamada _audios_ (para os arquivos de áudio) e outra _audios-transcritos_ (resultado da transcrição)

```bash
mkdir audios
mkdir audios-transcritos
```
Instale o _FFMPEG_

```bash
sudo apt install ffmpeg
```
Use o _pip_ para instalar o conteúdo do _requirements.txt_

```bash
pip install -r requirements.txt
```

### Uso

Após copiar os áudios a serem transcritos para a pasta _audios_, execute o arquivo _transcrever-audios.py_

```bash
py transcrever-audios.py
```
