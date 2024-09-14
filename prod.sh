# ./limpar-pastas.sh
# gunicorn -w 2 -b 0.0.0.0:8080 --certfile=cert.pem --keyfile=cert.key --timeout 980 --limit-request-line 0 --limit-request-field_size 0 app:app
gunicorn -w 2 -b 0.0.0.0:8080 --timeout 980 --limit-request-line 0 --limit-request-field_size 0 app:app
