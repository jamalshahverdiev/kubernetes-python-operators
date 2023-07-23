from flask import Flask, request
from src.functions import handle_mutate, handle_validate

app = Flask(__name__)

@app.route('/mutate', methods=['POST'])
def mutate_endpoint():
    return handle_mutate(request)

@app.route('/validate', methods=['POST'])
def validate_endpoint():
    return handle_validate(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('certs/server.crt', 'certs/server.key'))
