from pyannote.audio import Pipeline

# Carrega a pipeline de diarização de falantes
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

def diarize_audio(audio_file_path):
    # Executa a diarização no arquivo de áudio fornecido
    diarization_result = diarization_pipeline(audio_file_path)
    
    # Itera sobre os segmentos de fala e os falantes
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        print(f"Speaker {speaker} speaks from {turn.start:.1f}s to {turn.end:.1f}s")

# Teste com um arquivo de áudio
diarize_audio("./douglas.mp3")
