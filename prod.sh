./limpar-pastas.sh
gunicorn -w 2 -b 0.0.0.0:8080 --timeout 180 app:app
