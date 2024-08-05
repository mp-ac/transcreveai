## Transcrição de áudio para texto com Whisper


O Whisper utiliza redes neurais profundas treinadas em vastas quantidades de dados de áudio e texto. O modelo é baseado em uma arquitetura de transformadores, que permite processar grandes sequências de dados de forma eficiente. Ele trabalha em duas etapas principais:

* Pré-processamento: O áudio é convertido em um formato de entrada adequado para o modelo. Isso inclui a normalização do som, remoção de ruídos e segmentação do áudio em partes menores.
* Reconhecimento e Transcrição: O modelo processa essas partes segmentadas, reconhecendo padrões na fala e convertendo-os em texto. Graças ao seu treinamento extenso, o Whisper consegue captar nuances da linguagem, como variações de sotaque e entonações, proporcionando transcrições precisas.

```
O whisper-large-v3 foi criado e é mantido pela OpenAI
```

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

Você pode usar dois métodos diferentes para transcrição de áudio. Subindo uma interface web com endpoints ou transcrição em massa de arquivos.

_*Lembre-se de antes de fazer uma cópia do arquivo .env.example com o nome .env e preencher as informações necessárias para a aplicação_

```bash
cp .env.example .env
```

#### Transcrição com interface web e endpoints

A interface web é recomendada para testar o desempenho do seu hardware na hora de transcrever áudios e permitir que outros usuários também realizem um teste rápido da ferramenta. Inicie o _prod.sh_

_*Para o primeiro uso, você deve atribuir permissão de execução para o arquivo_

```bash
chmod u+x prod.sh
./prod.sh
```

Acesse o seu endereço ipv4 no navegador, seguido da porta 8080. Exemplo: 192.168.0.2:8080

Você também terá a sua disposição os endpoints para transcrever áudios e fazer o download dos arquivos de áudio que foram transcritos.

#### Transcrição de arquivos em massa

Copie os áudios a serem transcritos para a pasta _audios_, execute o arquivo _transcrever-audios.py_

```bash
py transcrever-audios.py
```
Seus arquivos de áudio transcritos ficarão na pasta _audios-transcritos_
