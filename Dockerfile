ARG CUDA_IMAGE="12.5.0-devel-ubuntu22.04"
FROM nvidia/cuda:${CUDA_IMAGE}

WORKDIR /app
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive
ENV HOST=0.0.0.0
ENV CUDA_DOCKER_ARCH=all

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y python3 python3-pip ffmpeg libopenblas-dev

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN python3 -c "from transformers import AutoModelForSpeechSeq2Seq; AutoModelForSpeechSeq2Seq.from_pretrained('openai/whisper-large-v3')"

COPY ./static static
COPY ./templates templates
COPY ./app.py .
COPY ./main.py .
COPY ./prod.sh .
COPY ./transcribe.py .
COPY ./transcrever.py .
COPY ./.env .

EXPOSE 8080
