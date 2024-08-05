from docx import Document


class Transcrever:
    """
    Classe para transcrever áudios

    Métodos:
    --------
    seg_para_hms(self, seconds):
        Converte segundos para horas, minutos e segundos

    transcricao(self, pipe, dir_audios, nome, extensao, dir_transcritos, formato_saida):
        Realiza a transcrição do áudio
    """
    def __init__(self):
        pass

    def seg_para_hms(self, seconds):
        """
        Converte segundos para horas, minutos e segundos

        Parâmetros:
        -----------
        seconds : int
            Segundos a serem convertidos

        Retorno:
        --------
        str
            Horas, minutos e segundos convertidos
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def transcricao(self, pipe, dir_audios, nome, extensao, dir_transcritos, formato_saida):
        """
        Realiza a transcrição do áudio

        Parâmetros:
        -----------
        pipe : function
            Função para transcrição
            dir_audios : str
                Diretório dos áudios
            nome : str
                Nome do arquivo de áudio
            extensao : str
                Extensão do arquivo de áudio
            dir_transcritos : str
                Diretório para salvar os transcritos
            formato_saida : str
                Formato de saída da transcrição
        """
        res = pipe(
                dir_audios+'/'+nome+extensao,
                batch_size=10,
                return_timestamps=True,
                chunk_length_s=30,
                stride_length_s=(4, 2)
        )

        document = Document()

        for chunk in res['chunks']:
            start_time = self.seg_para_hms(chunk['timestamp'][0])
            end_time = self.seg_para_hms(chunk['timestamp'][1])
            input_dictionary = '['+str(start_time)+' / '+str(end_time) + '] - '+chunk['text']

            document.add_paragraph(input_dictionary)

        document.save(dir_transcritos+'/'+nome+formato_saida)
