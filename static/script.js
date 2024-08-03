document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const loadingSection = document.getElementById('loadingSection');
    const formData = new FormData(this);
    const downloadSection = document.getElementById('downloadSection');
    const errorSection = document.getElementById('errorSection');
    submitButton.disabled = true;
    loadingSection.classList.remove('hidden');
    downloadSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    try {
        const response = await fetch('/api/transcrever', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        loadingSection.classList.add('hidden');
        submitButton.disabled = false;

        if (result.status === 'success') {
            const downloadLink = document.getElementById('downloadLink');
            const tempoExecucao = document.getElementById('tempoExecucao');
            downloadLink.href = result.download;
            tempoExecucao.textContent = `Tempo de transcrição: ${result.tempo_transcricao}`;
            downloadSection.classList.remove('hidden');
        } else {
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = result.message;
            errorSection.classList.remove('hidden');
        }
    } catch (error) {
        loadingSection.classList.add('hidden');
        submitButton.disabled = false;
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = 'Ocorreu um erro durante o processo de transcrição.';
        errorSection.classList.remove('hidden');
    }
});
